#!/usr/bin/env python3
"""
calibrate_poses.py  — position-only IK, no orientation constraint
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
import time

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest, Constraints,
    PositionConstraint, BoundingVolume, MoveItErrorCodes,
)
from geometry_msgs.msg import PoseStamped, Pose
from shape_msgs.msg import SolidPrimitive
from sensor_msgs.msg import JointState


ARM_JOINTS = ['joint_1', 'joint_2', 'joint_3',
              'joint_4', 'joint_5', 'joint_6']

# Target positions in base_link frame
# Robot base at world z=0.4. Positions are relative to base_link (z=0 = robot base).
# Table top ~ z=0.0 in base frame. Bottle top ~ z=0.05.
TARGETS = {
    'inspect_above': (0.15,  0.00,  0.15),   # safe height above bottle
    'inspect_pick':  (0.15,  0.00,  0.00),   # at bottle pick height
    'good_above':    (0.35, -0.20,  0.10),   # above green bin
    'defect_above':  (0.35,  0.20,  0.10),   # above red bin
}


class CalibrationNode(Node):

    def __init__(self):
        super().__init__('calibration_node')
        self._client = ActionClient(self, MoveGroup, '/move_action')
        self._joint_state = None
        self.create_subscription(JointState, '/joint_states', self._js_cb, 10)
        self.get_logger().info('Waiting for MoveGroup...')
        self._client.wait_for_server()
        self.get_logger().info('Ready.')

    def _js_cb(self, msg):
        self._joint_state = msg

    def _get_joints(self):
        for _ in range(30):
            rclpy.spin_once(self, timeout_sec=0.05)
        if not self._joint_state:
            return None
        return {n: p for n, p in zip(
            self._joint_state.name, self._joint_state.position)}

    def _move_cartesian(self, name, x, y, z) -> bool:
        self.get_logger().info(f'→ {name}  ({x:.3f}, {y:.3f}, {z:.3f})')

        pose = Pose()
        pose.position.x = x
        pose.position.y = y
        pose.position.z = z
        # Neutral orientation — let IK pick whatever works
        pose.orientation.w = 1.0

        sphere = SolidPrimitive()
        sphere.type = SolidPrimitive.SPHERE
        sphere.dimensions = [0.05]   # 5 cm tolerance

        bv = BoundingVolume()
        bv.primitives = [sphere]
        bv.primitive_poses = [pose]

        pcm = PositionConstraint()
        pcm.header.frame_id = 'base_link'
        pcm.link_name = 'tool_link'
        pcm.constraint_region = bv
        pcm.weight = 1.0
        pcm.target_point_offset.x = 0.0
        pcm.target_point_offset.y = 0.0
        pcm.target_point_offset.z = 0.0

        constraints = Constraints()
        constraints.position_constraints = [pcm]

        request = MotionPlanRequest()
        request.group_name = 'arm'
        request.goal_constraints = [constraints]
        request.num_planning_attempts = 20
        request.allowed_planning_time = 10.0
        request.max_velocity_scaling_factor = 0.3
        request.max_acceleration_scaling_factor = 0.3

        goal = MoveGroup.Goal()
        goal.request = request
        goal.planning_options.plan_only = False
        goal.planning_options.replan = True
        goal.planning_options.replan_attempts = 3

        future = self._client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        gh = future.result()
        if not gh.accepted:
            self.get_logger().error(f'Rejected: {name}')
            return False

        res_future = gh.get_result_async()
        rclpy.spin_until_future_complete(self, res_future)
        val = res_future.result().result.error_code.val
        if val == MoveItErrorCodes.SUCCESS:
            self.get_logger().info(f'Reached: {name}')
            return True
        self.get_logger().error(f'Failed {name}: code {val}')
        return False

    def run(self):
        results = {}
        for name, (x, y, z) in TARGETS.items():
            ok = self._move_cartesian(name, x, y, z)
            if ok:
                time.sleep(1.0)
                joints = self._get_joints()
                if joints:
                    vals = [round(joints.get(j, 0.0), 4) for j in ARM_JOINTS]
                    results[name] = vals
                    self.get_logger().info(f'  {name}: {vals}')
            else:
                self.get_logger().warn(f'Skipped: {name}')

        print('\n\n' + '=' * 64)
        print('  Copy this POSES dict into decision_node.py')
        print('=' * 64)
        print('POSES = {')
        print("    'home':              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],")
        for name, vals in results.items():
            pad = ' ' * max(1, 20 - len(name))
            print(f"    '{name}':{pad}{vals},")
        # Auto-estimate drop poses
        for name, vals in results.items():
            if 'above' in name:
                drop = name.replace('above', 'drop')
                pad  = ' ' * max(1, 20 - len(drop))
                dv   = vals.copy()
                dv[1] = round(vals[1] + 0.28, 4)
                dv[2] = round(vals[2] - 0.22, 4)
                print(f"    '{drop}':{pad}{dv},  # estimate — verify!")
        print('}')
        print('=' * 64)
        print('\nNOTE: drop poses are estimates. Run the robot and')
        print('check visually, then adjust joint_2 (+) and joint_3 (-)')
        print('to lower the arm further.')


def main():
    rclpy.init()
    node = CalibrationNode()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
