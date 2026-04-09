#!/usr/bin/env python3
"""
niryo_vision/vision_node.py
---------------------------
Subscribes to /camera/image_raw (overhead camera at z=0.85 looking straight down).
Detects blue (good) and orange (defective) cylinders via HSV segmentation.
Converts pixel centroid → world XY using the known camera geometry.
Publishes niryo_interfaces/Detection on /niryo/detection.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from niryo_interfaces.msg import Detection


# ── Camera geometry (from sorting_world.sdf) ─────────────────────────────────
# Camera pose:  x=0.15  y=0.0  z=0.85  pointing straight down (pitch = pi/2)
# FOV horizontal: 1.047 rad (60°),  image: 640×480
# Table surface z = 0.40 m  →  camera height above table = 0.85 - 0.40 = 0.45 m

CAM_X        = 0.15    # world X of camera (= principal point projected onto table)
CAM_Y        = 0.00    # world Y of camera
CAM_Z        = 0.85    # world Z of camera
TABLE_Z      = 0.40    # world Z of table surface (where bottles sit)
CAM_HEIGHT   = CAM_Z - TABLE_Z          # 0.45 m

IMG_W, IMG_H = 640, 480
HFOV         = 1.047                    # radians
# Focal length in pixels  f = (W/2) / tan(HFOV/2)
F_PX         = (IMG_W / 2.0) / np.tan(HFOV / 2.0)

# ── HSV color ranges ─────────────────────────────────────────────────────────
# Blue  (good bottle):      hue ~210°  →  OpenCV hue ~105–130
# Orange (defective):       hue ~15°   →  OpenCV hue ~5–20
HSV_RANGES = {
    'blue':   ([100, 80, 80],  [130, 255, 255]),
    'orange': ([5,   100, 100], [20,  255, 255]),
}

# Map color → label
COLOR_LABEL = {
    'blue':   'good',
    'orange': 'defective',
}

MIN_CONTOUR_AREA = 200   # pixels² — ignore noise


class VisionNode(Node):

    def __init__(self):
        super().__init__('niryo_vision_node')
        self._bridge = CvBridge()

        self._sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self._image_callback,
            10,
        )

        self._pub = self.create_publisher(Detection, '/niryo/detection', 10)

        # Debug image publisher (optional — view with `ros2 run rqt_image_view rqt_image_view`)
        self._debug_pub = self.create_publisher(Image, '/niryo/debug_image', 10)

        self.get_logger().info('Vision node started — waiting for images.')

    # ── Pixel → world coordinates ─────────────────────────────────────────────

    def _pixel_to_world(self, px: float, py: float):
        """
        Convert image pixel (px, py) to world (x, y) assuming:
        - Camera is directly above the scene, pointing straight down
        - No lens distortion
        """
        # Offset from image centre (principal point)
        dx_px = px - IMG_W / 2.0
        dy_px = py - IMG_H / 2.0

        # Scale: metres per pixel at table distance
        scale = CAM_HEIGHT / F_PX

        # Camera is looking down: image X → world X, image Y → world -Y
        # (depends on camera orientation; adjust sign if robot moves wrong way)
        world_x = CAM_X + dx_px * scale
        world_y = CAM_Y - dy_px * scale
        return world_x, world_y

    # ── Main callback ─────────────────────────────────────────────────────────

    def _image_callback(self, msg: Image):
        try:
            frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'CvBridge error: {e}')
            return

        hsv   = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        debug = frame.copy()

        best_detection = None   # publish the largest object found this frame

        for color_name, (lo, hi) in HSV_RANGES.items():
            lo_arr = np.array(lo, dtype=np.uint8)
            hi_arr = np.array(hi, dtype=np.uint8)
            mask   = cv2.inRange(hsv, lo_arr, hi_arr)

            # Clean up mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
            mask   = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < MIN_CONTOUR_AREA:
                    continue

                # Centroid
                M  = cv2.moments(cnt)
                if M['m00'] == 0:
                    continue
                cx = M['m10'] / M['m00']
                cy = M['m01'] / M['m00']

                world_x, world_y = self._pixel_to_world(cx, cy)
                confidence = min(1.0, area / 5000.0)  # crude area→confidence

                # Draw on debug image
                colour_bgr = (255, 100, 0) if color_name == 'blue' else (0, 100, 255)
                cv2.drawContours(debug, [cnt], -1, colour_bgr, 2)
                cv2.circle(debug, (int(cx), int(cy)), 5, colour_bgr, -1)
                cv2.putText(
                    debug,
                    f'{color_name} ({world_x:.2f},{world_y:.2f})',
                    (int(cx) + 8, int(cy)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, colour_bgr, 1,
                )

                det = Detection()
                det.x          = world_x
                det.y          = world_y
                det.z          = TABLE_Z + 0.05   # centre of 0.1m bottle
                det.color      = color_name
                det.label      = COLOR_LABEL[color_name]
                det.confidence = confidence

                if best_detection is None or confidence > best_detection.confidence:
                    best_detection = det

        if best_detection is not None:
            self._pub.publish(best_detection)
            self.get_logger().info(
                f'Detected: {best_detection.label} ({best_detection.color}) '
                f'at world ({best_detection.x:.3f}, {best_detection.y:.3f})',
                throttle_duration_sec=1.0,
            )

        # Always publish debug image
        try:
            self._debug_pub.publish(
                self._bridge.cv2_to_imgmsg(debug, encoding='bgr8'))
        except Exception:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
