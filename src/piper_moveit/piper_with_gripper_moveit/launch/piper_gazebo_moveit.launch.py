import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument(
            'use_orbbec_camera',
            default_value='true',
            description='Attach the Orbbec camera model in simulation'),
    ]

    def launch_setup(context, *args, **kwargs):
        use_sim_time = LaunchConfiguration('use_sim_time')
        # We need to explicitly pass this because piper_moveit.launch.py might not use it by default correctly
        # or we want to ensure consistency.

        # 1. Launch Gazebo Simulation
        piper_gazebo_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    FindPackageShare("piper_gazebo").find("piper_gazebo"),
                    "launch",
                    "piper_with_gripper",
                    "piper_gazebo.launch.py"
                )
            ),
            launch_arguments={
                'use_orbbec_camera': LaunchConfiguration('use_orbbec_camera'),
                'use_sim_time': use_sim_time,
            }.items()
        )

        # 2. Launch MoveIt
        # We use the piper_moveit.launch.py which starts move_group and rviz
        piper_moveit_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    FindPackageShare("piper_with_gripper_moveit").find("piper_with_gripper_moveit"),
                    "launch",
                    "piper_moveit.launch.py"
                )
            ),
            launch_arguments={
                'use_sim_time': use_sim_time,
                # Ensure we don't start another robot_state_publisher if possible, 
                # but piper_moveit.launch.py usually starts move_group which listens to joint_states.
                # piper_gazebo.launch.py already starts robot_state_publisher and joint_state_broadcaster.
            }.items()
        )

        return [
            piper_gazebo_launch,
            piper_moveit_launch
        ]

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
