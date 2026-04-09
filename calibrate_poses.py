#!/usr/bin/env python3
"""
calibrate_poses.py — joint-space sweep calibration
Moves the robot through candidate joint poses, prints what it achieved.
No IK, no Cartesian constraints — just direct joint targets.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
import time

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest, Constraints,
    JointConstraint, MoveItErrorCodes,
)
from sensor_msgs.msg import JointState

ARM_JOINTS = ['joint_1', 'joint_2', 'joint_3',
              'joint_4', 'joint_5', 'joint_6']

# Candidate joint poses to try — tuned for Niryo Ned2 workspace
# j1=base rotation, j2=shoulder, j3=elbow, j4=wrist_roll, j5=wrist_pitch, j6=wrist_spin
# Positive j2 = arm forward, negative j3 = elbow up
CANDIDATES = {
    # Above inspection area (x≈0.15, y≈0, z≈table+0.15)
    'inspect_above':  [ 0.00,  0.50, -0.30,  0.00, -1.20,  0.00],
    # Lower — pick height (z≈table+0.02)
    'inspect_pick':   [ 0.00,  0.80, -0.55,  0.00, -1.20,  0.00],
    # Above good bin (x≈0.35, y≈-0.25) — rotate j1 negative (clockwise)
    'good_above':     [-0.60,  0.50, -0.30,  0.00, -1.20,  0.00],
    # Lower into good bin
    'good_drop':      [-0.60,  0.80, -0.55,  0.00, -1.20,  0.00],
    # Above defective bin (x≈0.35, y≈+0.25) — rotate j1 positive
    'defect_above':   [ 0.60,  0.50, -0.30,  0.00, -1.20,  0.00],
    # Lower into defective bin
    'defect_drop':    [ 0.60,  0.80, -0.55,  0.00, -1.20,  0.00],
}


class CalibNode(Node):

    def __init__(self):
        super().__init__('calib_node')
        self._client = ActionClient(self, MoveGroup, '/move_action')
        self._js = None
        self.create_subscription(JointState, '/joint_states', self._js_cb, 10)
        self.get_logger().info('Waiting for MoveGroup...')
        self._client.wait_for_server()
        self.get_logger().info('Ready.')

    def _js_cb(self, msg):
        self._js = msg

    def _get_joints(self):
        for _ in range(40):
            rclpy.spin_once(self, timeout_sec=0.05)
        if not self._js:
            return {}
        return {n: p for n, p in zip(self._js.name, self._js.position)}

    def _move_joints(self, name, positions, tol=0.02) -> bool:
        constraints = Constraints()
        for jname, pos in zip(ARM_JOINTS, positions):
            jc = JointConstraint()
            jc.joint_name      = jname
            jc.position        = pos
            jc.tolerance_above = tol
            jc.tolerance_below = tol
            jc.weight          = 1.0
            constraints.joint_constraints.append(jc)

        req = MotionPlanRequest()
        req.group_name                      = 'arm'
        req.goal_constraints                = [constraints]
        req.num_planning_attempts           = 10
        req.allowed_planning_time           = 5.0
        req.max_velocity_scaling_factor     = 0.3
        req.max_acceleration_scaling_factor = 0.3

        goal = MoveGroup.Goal()
        goal.request                          = req
        goal.planning_options.plan_only       = False
        goal.planning_options.replan          = True
        goal.planning_options.replan_attempts = 2

        fut = self._client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, fut)
        gh = fut.result()
        if not gh.accepted:
            self.get_logger().error(f'Rejected: {name}')
            return False

        res = gh.get_result_async()
        rclpy.spin_until_future_complete(self, res)
        val = res.result().result.error_code.val
        if val == MoveItErrorCodes.SUCCESS:
            self.get_logger().info(f'✓ {name}')
            return True
        self.get_logger().error(f'✗ {name}: code {val}')
        return False

    def run(self):
        results = {}

        for name, joints in CANDIDATES.items():
            self.get_logger().info(f'\n--- {name} ---')
            ok = self._move_joints(name, joints)
            time.sleep(1.2)
            actual = self._get_joints()
            if actual:
                vals = [round(actual.get(j, 0.0), 4) for j in ARM_JOINTS]
                results[name] = (ok, vals)
                status = '✓' if ok else '✗ (best effort)'
                self.get_logger().info(f'  {status} actual joints: {vals}')
            # Pause so you can visually check in Gazebo
            self.get_logger().info('  [check Gazebo — continuing in 2s]')
            time.sleep(2.0)

        # Return home
        self._move_joints('home', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        print('\n\n' + '=' * 66)
        print('  POSES — paste into decision_node.py')
        print('=' * 66)
        print('POSES = {')
        print("    'home':              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],")
        for name, (ok, vals) in results.items():
            pad  = ' ' * max(1, 20 - len(name))
            flag = '' if ok else '  # UNREACHED — adjust!'
            print(f"    '{name}':{pad}{vals},{flag}")
        print('}')
        print('=' * 66)
        print()
        print('Unreached poses (marked above) need joint angle adjustments.')
        print('Increase joint_2 to reach further forward/down.')
        print('Adjust joint_1 to rotate to the correct bin side.')


def main():
    rclpy.init()
    node = CalibNode()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
