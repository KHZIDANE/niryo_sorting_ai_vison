import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():

    moveit_config_pkg = get_package_share_directory('niryo_ned2_moveit_config')

    # ── Use the moveit-config URDF (includes gripper + ros2_control) ──────────
    urdf_file      = os.path.join(moveit_config_pkg, 'config', 'niryo_ned2.urdf.xacro')
    initial_positions = os.path.join(moveit_config_pkg, 'config', 'initial_positions.yaml')

    moveit_config = (
        MoveItConfigsBuilder('niryo_ned2')
        .robot_description(
            file_path=urdf_file,
            mappings={'initial_positions_file': initial_positions},
        )
        .joint_limits(file_path='config/joint_limits.yaml')
        .robot_description_semantic(file_path='config/niryo_ned2.srdf')
        .robot_description_kinematics(file_path='config/kinematics.yaml')
        .trajectory_execution(file_path='config/moveit_controllers.yaml')
        .planning_pipelines(
            pipelines=['ompl', 'chomp', 'pilz_industrial_motion_planner', 'stomp']
        )
        .to_moveit_configs()
    )

    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[moveit_config.to_dict(), {'use_sim_time': True}],
        arguments=['--ros-args', '--log-level', 'info'],
    )

    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value='moveit.rviz',
        description='RViz configuration file',
    )

    rviz_config = PathJoinSubstitution(
        [FindPackageShare('niryo_ned2_moveit_config'), 'config',
         LaunchConfiguration('rviz_config')]
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        arguments=['-d', rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            {'use_sim_time': True},
        ],
    )

    return LaunchDescription([
        rviz_config_arg,
        move_group_node,
        rviz_node,
    ])
