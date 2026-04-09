import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription, ExecuteProcess,
    RegisterEventHandler, SetEnvironmentVariable,
    TimerAction, DeclareLaunchArgument,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():

    gazebo_pkg      = get_package_share_directory('niryo_gazebo')
    description_pkg = get_package_share_directory('niryo_ned_description')
    moveit_pkg      = get_package_share_directory('niryo_ned2_moveit_config')

    world_file   = os.path.join(gazebo_pkg, 'worlds', 'sorting_world.sdf')
    gz_urdf_file = os.path.join(gazebo_pkg, 'urdf', 'niryo_ned2_gz.urdf.xacro')
    urdf_file         = os.path.join(moveit_pkg, 'config', 'niryo_ned2.urdf.xacro')
    initial_positions = os.path.join(moveit_pkg, 'config', 'initial_positions.yaml')

    # ── Launch arguments ──────────────────────────────────────────────────────
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value='moveit.rviz',
        description='RViz configuration file',
    )

    # ── MoveIt config (shared by move_group + rviz) ───────────────────────────
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

    # ── Environment ───────────────────────────────────────────────────────────
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.join(description_pkg, '..', '..') + ':' +
              os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    )

    # ── Gazebo ────────────────────────────────────────────────────────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    # ── Robot state publisher (Gazebo URDF — includes gripper + ros2_control) ─
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': Command(['xacro ', gz_urdf_file])},
            {'use_sim_time': True},
        ],
    )

    # ── Spawn robot into Gazebo ───────────────────────────────────────────────
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'niryo_ned2',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '0.4',
        ],
        output='screen',
    )

    # ── Bridges ───────────────────────────────────────────────────────────────
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    camera_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image'],
        output='screen',
    )

    # ── Controllers (chained: jsb → arm → gripper) ────────────────────────────
    spawn_jsb = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller',
             '--set-state', 'active', 'joint_state_broadcaster'],
        output='screen',
    )

    spawn_arm = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller',
             '--set-state', 'active',
             'niryo_robot_follow_joint_trajectory_controller'],
        output='screen',
    )

    spawn_gripper = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller',
             '--set-state', 'active', 'gripper_controller'],
        output='screen',
    )

    load_arm_after_jsb = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_jsb,
            on_exit=[spawn_arm],
        )
    )

    load_gripper_after_arm = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_arm,
            on_exit=[spawn_gripper],
        )
    )

    # ── MoveIt move_group ─────────────────────────────────────────────────────
    # Delayed 4 s to ensure ros2_control is fully active first
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[moveit_config.to_dict(), {'use_sim_time': True}],
        arguments=['--ros-args', '--log-level', 'info'],
    )

    delayed_moveit = TimerAction(
        period=4.0,
        actions=[move_group_node],
    )

    # ── RViz ──────────────────────────────────────────────────────────────────
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        arguments=['-d', PathJoinSubstitution(
            [FindPackageShare('niryo_ned2_moveit_config'), 'config',
             LaunchConfiguration('rviz_config')]
        )],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            {'use_sim_time': True},
        ],
    )

    # ── Vision node ───────────────────────────────────────────────────────────
    vision_node = Node(
        package='niryo_vision',
        executable='vision_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # ── Decision node ─────────────────────────────────────────────────────────
    decision_node = Node(
        package='niryo_decision',
        executable='decision_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    # Vision + decision delayed 8 s: Gazebo + controllers + MoveIt must be up
    delayed_pipeline = TimerAction(
        period=8.0,
        actions=[vision_node],#desision_node],teporarely diabled 
    )

    return LaunchDescription([
        rviz_config_arg,
        gz_resource_path,
        gazebo,
        robot_state_publisher,
        spawn_robot,
        clock_bridge,
        camera_bridge,
        spawn_jsb,
        load_arm_after_jsb,
        load_gripper_after_arm,
        delayed_moveit,       # move_group starts at t+4s
        rviz_node,
        delayed_pipeline,     # vision + decision start at t+8s
    ])
