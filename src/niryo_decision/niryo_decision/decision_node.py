#!/usr/bin/env python3
"""
niryo_decision/decision_node.py
--------------------------------
Subscribes to /niryo/detection.
For each detected object: pick it from the inspection area,
route it to bin_good or bin_defective based on label.

Fix: pick-and-place runs in a separate thread so the ROS2 executor
is never blocked and spin_until_future_complete works correctly.
"""
import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest, JointConstraint, Constraints, MoveItErrorCodes)
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration as RosDuration
from niryo_interfaces.msg import Detection

# ── Joint names ───────────────────────────────────────────────────────────────
ARM_JOINTS     = ['joint_1', 'joint_2', 'joint_3',
                  'joint_4', 'joint_5', 'joint_6']
GRIPPER_JOINTS = ['joint_base_to_mors_1', 'joint_base_to_mors_2']

# ── Named arm poses ───────────────────────────────────────────────────────────
#                      j1      j2     j3      j4     j5      j6
POSES = {
    'home':           [0.0,    0.0,   0.0,    0.0,   0.0,    0.0],
    # Above inspection marker (x=0.15, y=0.0)
    'inspect_above':  [0.0,    0.3,  -0.5,    0.0,  -0.8,    0.0],
    'inspect_pick':   [0.0,    0.6,  -0.8,    0.0,  -0.8,    0.0],
    # Above good bin (x=0.45, y=-0.25)
    'good_above':     [-0.52,  0.3,  -0.5,    0.0,  -0.8,    0.0],
    'good_drop':      [-0.52,  0.6,  -0.8,    0.0,  -0.8,    0.0],
    # Above defective bin (x=0.45, y=+0.25)
    'defect_above':   [0.52,   0.3,  -0.5,    0.0,  -0.8,    0.0],
    'defect_drop':    [0.52,   0.6,  -0.8,    0.0,  -0.8,    0.0],
}

GRIPPER_OPEN  = [0.008, 0.008]
GRIPPER_GRIP  = [-0.01, -0.01]
GRIPPER_REST  = [0.0,   0.0]


class DecisionNode(Node):
    def __init__(self):
        super().__init__('niryo_decision_node')

        # ReentrantCallbackGroup allows callbacks + action clients to coexist
        self._cb_group = ReentrantCallbackGroup()

        self._arm_client = ActionClient(
            self, MoveGroup, '/move_action',
            callback_group=self._cb_group)
        self._gripper_client = ActionClient(
            self, FollowJointTrajectory,
            '/gripper_controller/follow_joint_trajectory',
            callback_group=self._cb_group)

        self.get_logger().info('Waiting for action servers...')
        self._arm_client.wait_for_server()
        self._gripper_client.wait_for_server()
        self.get_logger().info('Action servers ready.')

        # Only process one object at a time
        self._busy = False
        self._lock = threading.Lock()

        self._sub = self.create_subscription(
            Detection, '/niryo/detection',
            self._detection_cb, 10,
            callback_group=self._cb_group)

        self.get_logger().info('Decision node ready — waiting for detections.')

    # ── Arm motion ────────────────────────────────────────────────────────────
    def _move_arm(self, pose_name: str, tol: float = 0.01) -> bool:
        positions = POSES[pose_name]
        self.get_logger().info(f'Arm → {pose_name}')

        constraints = Constraints()
        for name, pos in zip(ARM_JOINTS, positions):
            jc = JointConstraint()
            jc.joint_name      = name
            jc.position        = pos
            jc.tolerance_above = tol
            jc.tolerance_below = tol
            jc.weight          = 1.0
            constraints.joint_constraints.append(jc)

        request = MotionPlanRequest()
        request.group_name                      = 'arm'
        request.goal_constraints                = [constraints]
        request.num_planning_attempts           = 10
        request.allowed_planning_time           = 5.0
        request.max_velocity_scaling_factor     = 0.4
        request.max_acceleration_scaling_factor = 0.4

        goal = MoveGroup.Goal()
        goal.request                          = request
        goal.planning_options.plan_only       = False
        goal.planning_options.replan          = True
        goal.planning_options.replan_attempts = 3

        # Use threading.Event to wait without blocking the executor
        done_event = threading.Event()
        result_holder = [None]

        def goal_response_cb(future):
            gh = future.result()
            if not gh.accepted:
                self.get_logger().error(f'Arm goal rejected: {pose_name}')
                result_holder[0] = False
                done_event.set()
                return
            res_future = gh.get_result_async()
            res_future.add_done_callback(result_cb)

        def result_cb(future):
            code = future.result().result.error_code.val
            result_holder[0] = (code == MoveItErrorCodes.SUCCESS)
            if not result_holder[0]:
                self.get_logger().error(
                    f'Arm failed at {pose_name}: error code {code}')
            else:
                self.get_logger().info(f'Arm reached: {pose_name}')
            done_event.set()

        future = self._arm_client.send_goal_async(goal)
        future.add_done_callback(goal_response_cb)
        done_event.wait()   # blocks the worker thread only, not the executor
        return result_holder[0]

    # ── Gripper motion ────────────────────────────────────────────────────────
    def _move_gripper(self, positions: list, duration_sec: float = 1.5) -> bool:
        point = JointTrajectoryPoint()
        point.positions       = positions
        point.velocities      = [0.0, 0.0]
        point.accelerations   = [0.0, 0.0]
        point.time_from_start = RosDuration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9))

        traj = JointTrajectory()
        traj.joint_names = GRIPPER_JOINTS
        traj.points      = [point]

        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj

        done_event    = threading.Event()
        result_holder = [None]

        def goal_response_cb(future):
            gh = future.result()
            if not gh.accepted:
                self.get_logger().error('Gripper goal rejected')
                result_holder[0] = False
                done_event.set()
                return
            res_future = gh.get_result_async()
            res_future.add_done_callback(result_cb)

        def result_cb(future):
            ec = future.result().result.error_code
            result_holder[0] = (ec == FollowJointTrajectory.Result.SUCCESSFUL)
            if not result_holder[0]:
                self.get_logger().error(f'Gripper failed: error {ec}')
            done_event.set()

        future = self._gripper_client.send_goal_async(goal)
        future.add_done_callback(goal_response_cb)
        done_event.wait()
        return result_holder[0]

    # ── Pick-and-place sequence ───────────────────────────────────────────────
    def _sort_object(self, label: str):
        """Full pick-and-place sequence for one object."""
        is_good  = (label == 'good')
        above    = 'good_above'   if is_good else 'defect_above'
        drop     = 'good_drop'    if is_good else 'defect_drop'
        bin_name = 'bin_good'     if is_good else 'bin_defective'

        self.get_logger().info(f'Sorting: {label} → {bin_name}')

        steps = [
            ('inspect_above', lambda: self._move_arm('inspect_above')),
            ('open',          lambda: self._move_gripper(GRIPPER_OPEN)),
            ('inspect_pick',  lambda: self._move_arm('inspect_pick')),
            ('grip',          lambda: self._move_gripper(GRIPPER_GRIP)),
            ('lift',          lambda: self._move_arm('inspect_above')),
            (above,           lambda a=above: self._move_arm(a)),
            (drop,            lambda d=drop: self._move_arm(d)),
            ('open',          lambda: self._move_gripper(GRIPPER_OPEN)),
            ('retract',       lambda a=above: self._move_arm(a)),
            ('home',          lambda: self._move_arm('home')),
            ('rest',          lambda: self._move_gripper(GRIPPER_REST)),
        ]

        for name, action in steps:
            if not action():
                self.get_logger().error(f'Sequence aborted at: {name}')
                self._move_arm('home')
                return

        self.get_logger().info(f'Sort complete: {label}')

    # ── Detection callback — dispatches to worker thread ─────────────────────
    def _detection_cb(self, msg: Detection):
        with self._lock:
            if self._busy:
                return
            if msg.confidence < 0.3:
                self.get_logger().info(
                    f'Low confidence ({msg.confidence:.2f}), skipping')
                return
            self._busy = True

        self.get_logger().info(
            f'Detection: {msg.label} ({msg.color}) '
            f'at ({msg.x:.3f}, {msg.y:.3f}, {msg.z:.3f}) '
            f'conf={msg.confidence:.2f}')

        # Run pick-and-place in a separate thread so the executor stays free
        t = threading.Thread(target=self._worker, args=(msg.label,), daemon=True)
        t.start()

    def _worker(self, label: str):
        try:
            self._sort_object(label)
        except Exception as e:
            self.get_logger().error(f'Worker exception: {e}')
        finally:
            with self._lock:
                self._busy = False


def main(args=None):
    rclpy.init(args=args)
    node = DecisionNode()
    # MultiThreadedExecutor lets callbacks and action responses run concurrently
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
