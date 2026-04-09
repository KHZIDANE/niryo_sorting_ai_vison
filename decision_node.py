#!/usr/bin/env python3
"""
niryo_decision/decision_node.py
--------------------------------
Subscribes to /niryo/detection.
For each detected object: pick it from the inspection area,
route it to bin_good or bin_defective based on label.

World geometry (from sorting_world.sdf)
----------------------------------------
  Inspection area:  x=0.15  y=0.0   z=0.45  (bottle centre)
  bin_good:         x=0.45  y=-0.25 z=0.4
  bin_defective:    x=0.45  y=0.25  z=0.4
  Robot base:       x=0.0   y=0.0   z=0.4  (spawned at z=0.4)

Joint poses below were tuned for these positions.
Run `ros2 topic echo /joint_states` while positioning in RViz to refine.
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

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
GRIPPER_GRIP  = [0.002, 0.002]
GRIPPER_REST  = [0.0,   0.0]


class DecisionNode(Node):

    def __init__(self):
        super().__init__('niryo_decision_node')

        self._arm_client = ActionClient(self, MoveGroup, '/move_action')
        self._gripper_client = ActionClient(
            self, FollowJointTrajectory,
            '/gripper_controller/follow_joint_trajectory')

        self.get_logger().info('Waiting for action servers...')
        self._arm_client.wait_for_server()
        self._gripper_client.wait_for_server()
        self.get_logger().info('Action servers ready.')

        # Only process one object at a time
        self._busy = False

        self._sub = self.create_subscription(
            Detection, '/niryo/detection', self._detection_cb, 10)

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

        future = self._arm_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        gh = future.result()
        if not gh.accepted:
            self.get_logger().error(f'Arm goal rejected: {pose_name}')
            return False

        res_future = gh.get_result_async()
        rclpy.spin_until_future_complete(self, res_future)
        if res_future.result().result.error_code.val == MoveItErrorCodes.SUCCESS:
            self.get_logger().info(f'Arm reached: {pose_name}')
            return True
        self.get_logger().error(f'Arm failed: {pose_name}')
        return False

    # ── Gripper motion ────────────────────────────────────────────────────────

    def _move_gripper(self, positions: list, duration_sec: float = 1.5) -> bool:
        point = JointTrajectoryPoint()
        point.positions     = positions
        point.velocities    = [0.0, 0.0]
        point.accelerations = [0.0, 0.0]
        point.time_from_start = RosDuration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9))

        traj = JointTrajectory()
        traj.joint_names = GRIPPER_JOINTS
        traj.points      = [point]

        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj

        future = self._gripper_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        gh = future.result()
        if not gh.accepted:
            self.get_logger().error('Gripper goal rejected')
            return False

        res_future = gh.get_result_async()
        rclpy.spin_until_future_complete(self, res_future)
        ec = res_future.result().result.error_code
        if ec == FollowJointTrajectory.Result.SUCCESSFUL:
            return True
        self.get_logger().error(f'Gripper failed: error {ec}')
        return False

    # ── Pick-and-place sequence ───────────────────────────────────────────────

    def _sort_object(self, label: str):
        """Full pick-and-place sequence for one object."""
        is_good = (label == 'good')
        above   = 'good_above'   if is_good else 'defect_above'
        drop    = 'good_drop'    if is_good else 'defect_drop'
        bin_name = 'bin_good' if is_good else 'bin_defective'

        self.get_logger().info(f'Sorting: {label} → {bin_name}')

        steps = [
            ('inspect_above', lambda: self._move_arm('inspect_above')),
            ('open',          lambda: self._move_gripper(GRIPPER_OPEN)),
            ('inspect_pick',  lambda: self._move_arm('inspect_pick')),
            ('grip',          lambda: self._move_gripper(GRIPPER_GRIP)),
            ('inspect_above', lambda: self._move_arm('inspect_above')),  # lift
            (above,           lambda a=above: self._move_arm(a)),
            (drop,            lambda d=drop: self._move_arm(d)),
            ('open',          lambda: self._move_gripper(GRIPPER_OPEN)),
            (above,           lambda a=above: self._move_arm(a)),        # retract
            ('home',          lambda: self._move_arm('home')),
            ('rest',          lambda: self._move_gripper(GRIPPER_REST)),
        ]

        for name, action in steps:
            ok = action()
            if not ok:
                self.get_logger().error(f'Sequence aborted at: {name}')
                self._move_arm('home')
                return

        self.get_logger().info(f'Sort complete: {label}')

    # ── Detection callback ────────────────────────────────────────────────────

    def _detection_cb(self, msg: Detection):
        if self._busy:
            return   # robot is already working

        if msg.confidence < 0.3:
            self.get_logger().info(
                f'Detection confidence too low ({msg.confidence:.2f}), skipping')
            return

        self._busy = True
        self.get_logger().info(
            f'Detection received: {msg.label} ({msg.color}) '
            f'at ({msg.x:.3f}, {msg.y:.3f}, {msg.z:.3f}) '
            f'confidence={msg.confidence:.2f}')

        try:
            self._sort_object(msg.label)
        finally:
            self._busy = False


def main(args=None):
    rclpy.init(args=args)
    node = DecisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
