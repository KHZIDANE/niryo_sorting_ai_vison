#!/usr/bin/env python3
"""
niryo_moveit_test.py
--------------------
Drives the Niryo Ned2 arm and gripper through MoveIt2.

Sequence
--------
1. Move arm to HOME pose (all zeros)
2. Open gripper
3. Move arm to PICK pose (above the sorting area)
4. Close gripper
5. Move arm to PLACE pose (drop-off side)
6. Open gripper
7. Return arm to HOME pose

Run
---
  python3 niryo_moveit_test.py
(with Gazebo + MoveIt both running)
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.duration import Duration

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest,
    JointConstraint,
    Constraints,
    MoveItErrorCodes,
)
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration as RosDuration


# ── Joint names ──────────────────────────────────────────────────────────────
ARM_JOINTS    = ['joint_1', 'joint_2', 'joint_3',
                 'joint_4', 'joint_5', 'joint_6']
GRIPPER_JOINTS = ['joint_base_to_mors_1', 'joint_base_to_mors_2']

# ── Named poses (joint angles in radians) ────────────────────────────────────
POSES = {
    #               j1      j2      j3      j4      j5      j6
    'home':        [0.0,    0.0,    0.0,    0.0,    0.0,    0.0],
    'pick_above':  [0.0,    0.3,   -0.5,    0.0,   -0.8,    0.0],
    'pick_down':   [0.0,    0.6,   -0.8,    0.0,   -0.8,    0.0],
    'place_above': [1.57,   0.3,   -0.5,    0.0,   -0.8,    0.0],
    'place_down':  [1.57,   0.6,   -0.8,    0.0,   -0.8,    0.0],
}

GRIPPER_OPEN   = [0.008,  0.008]   # fully open  (prismatic limit +0.01 m)
GRIPPER_CLOSE  = [0.002,  0.002]   # gripping    (adjust to object size)
GRIPPER_REST   = [0.0,    0.0]     # fully closed / rest


class NiryoMoveItTest(Node):

    def __init__(self):
        super().__init__('niryo_moveit_test')

        # MoveGroup action (arm planning + execution)
        self._arm_client = ActionClient(self, MoveGroup, '/move_action')

        # Direct trajectory action for gripper (bypasses planning — gripper
        # is a simple open/close, no obstacle avoidance needed)
        self._gripper_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/gripper_controller/follow_joint_trajectory',
        )

        self.get_logger().info('Waiting for action servers...')
        self._arm_client.wait_for_server()
        self._gripper_client.wait_for_server()
        self.get_logger().info('Action servers ready.')

    # ── Arm helpers ──────────────────────────────────────────────────────────

    def _build_arm_goal(self, joint_positions: list, tol: float = 0.01) -> MoveGroup.Goal:
        """Build a MoveGroup goal from a list of 6 joint positions."""
        constraints = Constraints()
        for name, pos in zip(ARM_JOINTS, joint_positions):
            jc = JointConstraint()
            jc.joint_name        = name
            jc.position          = pos
            jc.tolerance_above   = tol
            jc.tolerance_below   = tol
            jc.weight            = 1.0
            constraints.joint_constraints.append(jc)

        request = MotionPlanRequest()
        request.group_name              = 'arm'
        request.goal_constraints        = [constraints]
        request.num_planning_attempts   = 10
        request.allowed_planning_time   = 5.0
        request.max_velocity_scaling_factor     = 0.3
        request.max_acceleration_scaling_factor = 0.3

        goal = MoveGroup.Goal()
        goal.request    = request
        goal.planning_options.plan_only         = False
        goal.planning_options.replan            = True
        goal.planning_options.replan_attempts   = 3
        return goal

    def move_arm(self, pose_name: str) -> bool:
        """Plan and execute arm motion to a named pose. Returns True on success."""
        positions = POSES[pose_name]
        self.get_logger().info(f'Moving arm → {pose_name}')
        goal = self._build_arm_goal(positions)

        future = self._arm_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error(f'Arm goal rejected for pose: {pose_name}')
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result

        if result.error_code.val == MoveItErrorCodes.SUCCESS:
            self.get_logger().info(f'Arm reached: {pose_name}')
            return True
        else:
            self.get_logger().error(
                f'Arm motion failed: error code {result.error_code.val}')
            return False

    # ── Gripper helpers ──────────────────────────────────────────────────────

    def move_gripper(self, positions: list, duration_sec: float = 1.5) -> bool:
        """Send gripper to [mors_1_pos, mors_2_pos]. Returns True on success."""
        label = 'open' if positions[0] > 0.004 else \
                'close' if positions[0] < 0.001 else 'grip'
        self.get_logger().info(f'Gripper → {label} ({positions})')

        point = JointTrajectoryPoint()
        point.positions      = positions
        point.velocities     = [0.0, 0.0]
        point.accelerations  = [0.0, 0.0]
        point.time_from_start = RosDuration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9)
        )

        traj = JointTrajectory()
        traj.joint_names = GRIPPER_JOINTS
        traj.points      = [point]

        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj

        future = self._gripper_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Gripper goal rejected')
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        error_code = result_future.result().result.error_code

        if error_code == FollowJointTrajectory.Result.SUCCESSFUL:
            self.get_logger().info(f'Gripper reached: {label}')
            return True
        else:
            self.get_logger().error(f'Gripper motion failed: error code {error_code}')
            return False

    def open_gripper(self)  -> bool: return self.move_gripper(GRIPPER_OPEN)
    def close_gripper(self) -> bool: return self.move_gripper(GRIPPER_CLOSE)
    def rest_gripper(self)  -> bool: return self.move_gripper(GRIPPER_REST)

    # ── Full pick-and-place sequence ─────────────────────────────────────────

    def run_sequence(self):
        steps = [
            ('home',        lambda: self.move_arm('home')),
            ('open',        self.open_gripper),
            ('pick_above',  lambda: self.move_arm('pick_above')),
            ('pick_down',   lambda: self.move_arm('pick_down')),
            ('close',       self.close_gripper),
            ('pick_above',  lambda: self.move_arm('pick_above')),   # lift
            ('place_above', lambda: self.move_arm('place_above')),
            ('place_down',  lambda: self.move_arm('place_down')),
            ('open',        self.open_gripper),
            ('place_above', lambda: self.move_arm('place_above')),  # retract
            ('home',        lambda: self.move_arm('home')),
            ('rest',        self.rest_gripper),
        ]

        self.get_logger().info('=== Starting pick-and-place sequence ===')
        for name, action in steps:
            self.get_logger().info(f'--- Step: {name} ---')
            ok = action()
            if not ok:
                self.get_logger().error(f'Sequence aborted at step: {name}')
                return
        self.get_logger().info('=== Sequence complete ===')


def main():
    rclpy.init()
    node = NiryoMoveItTest()
    node.run_sequence()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
