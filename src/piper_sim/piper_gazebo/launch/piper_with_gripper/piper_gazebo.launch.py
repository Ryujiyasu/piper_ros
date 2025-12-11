import os
import re

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler, SetEnvironmentVariable, ExecuteProcess, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import xacro


def remove_comments(text: str) -> str:
    pattern = r'<!--(.*?)-->'
    return re.sub(pattern, '', text, flags=re.DOTALL)


def generate_launch_description():
    robot_name_in_model = 'piper'
    package_name = 'piper_description'
    urdf_name = "piper_description_gazebo.xacro"

    pkg_share = FindPackageShare(package=package_name).find(package_name)
    gazebo_pkg_share = FindPackageShare(package='piper_gazebo').find('piper_gazebo')
    urdf_model_path = os.path.join(pkg_share, f'urdf/{urdf_name}')
    empty_world = os.path.join(gazebo_pkg_share, 'worlds', 'empty.sdf')
    world_name = 'empty'

    resource_path = [
        os.path.join(pkg_share, 'meshes'),
        os.path.join(
            FindPackageShare(package='orbbec_description').find('orbbec_description'),
            'meshes',
        ),
    ]

    gz_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                FindPackageShare(package='ros_gz_sim').find('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py',
            )
        ),
        launch_arguments={'gz_args': f'-r -v 2 {empty_world}'}.items(),
    )

    default_orbbec_mesh_dir = os.path.join(
        FindPackageShare(package='orbbec_description').find('orbbec_description'),
        'meshes',
        'gemini2')

    declared_arguments = [
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument(
            'use_orbbec_camera',
            default_value='true',
            description='Attach the Orbbec camera model to the wrist in simulation.',
        ),
        DeclareLaunchArgument(
            'orbbec_parent_link',
            default_value='link6',
            description='Robot link to use as the camera mount parent.',
        ),
        DeclareLaunchArgument(
            'orbbec_xyz',
            default_value='-0.05 0.025 0',
            description='Camera mount xyz offset (meters) from the parent frame.',
        ),
        DeclareLaunchArgument(
            'orbbec_rpy',
            default_value='0 -1.57 0',
            description='Camera mount rpy (radians) from the parent frame.',
        ),
        DeclareLaunchArgument(
            'orbbec_mesh_dir',
            default_value=default_orbbec_mesh_dir,
            description='Mesh directory to use for the Orbbec model (absolute path).',
        ),
    ]

    def launch_setup(context, *args, **kwargs):
        mappings = {
            'use_gz': 'true',
            'use_orbbec_camera': LaunchConfiguration('use_orbbec_camera').perform(context),
            'orbbec_parent_link': LaunchConfiguration('orbbec_parent_link').perform(context),
            'orbbec_xyz': LaunchConfiguration('orbbec_xyz').perform(context),
            'orbbec_rpy': LaunchConfiguration('orbbec_rpy').perform(context),
            'orbbec_mesh_dir': LaunchConfiguration('orbbec_mesh_dir').perform(context),
        }

        doc = xacro.process_file(urdf_model_path, mappings=mappings)
        robot_description_xml = remove_comments(doc.toxml())
        params = {'robot_description': robot_description_xml}

        node_robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}, params, {"publish_frequency": 15.0}],
            output='screen'
        )

        spawn_entity_cmd = Node(
            package='ros_gz_sim',
            executable='create',
            output='screen',
            parameters=[{
                'world': world_name,
                'string': robot_description_xml,
                'name': robot_name_in_model,
                'allow_renaming': False,
            }],
        )

        load_joint_state_controller = Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
            output='screen'
        )

        load_joint_trajectory_controller = Node(
            package='controller_manager',
            executable='spawner',
            arguments=['arm_controller', '--controller-manager', '/controller_manager'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
            output='screen'
            )

        # load_gripper_trajectory_controller = Node(
        #     package='controller_manager',
        #     executable='spawner',
        #     arguments=['gripper_controller', '--controller-manager', '/controller_manager'],
        #     parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        #     output='screen'
        #     )
        
        # load_gripper8_trajectory_controller = Node(
        #     package='controller_manager',
        #     executable='spawner',
        #     arguments=['gripper8_controller', '--controller-manager', '/controller_manager'],
        #     parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        #     output='screen'
        #     )

        close_evt1 = RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity_cmd,
                on_exit=[load_joint_state_controller],
            )
        )

        close_evt2 = RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_controller,
                on_exit=[
                    load_joint_trajectory_controller,
                    # load_gripper_trajectory_controller,
                    # load_gripper8_trajectory_controller
                    ],
            )
        )

        node_gripper_mirror_controller = Node(
            package='piper_gazebo',
            executable='joint8_ctrl.py',
            output='screen'
        )

        bridge_topics = [
            '/orbbec/rgb/image@sensor_msgs/msg/Image@ignition.msgs.Image',
            '/orbbec/rgb/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo',
            '/orbbec/depth/image@sensor_msgs/msg/Image@ignition.msgs.Image',
            '/orbbec/depth/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
        ]

        bridge_cmd = ExecuteProcess(
            cmd=['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge'] + bridge_topics,
            output='screen'
        )

        bridge_with_delay = TimerAction(
            period=5.0,
            actions=[bridge_cmd]
        )

        return [
            close_evt1,
            close_evt2,
            SetEnvironmentVariable(
                name='GZ_SIM_RESOURCE_PATH',
                value=':'.join(resource_path + [os.environ.get('GZ_SIM_RESOURCE_PATH', '')]),
            ),
            gz_sim_launch,
            node_gripper_mirror_controller,
            node_robot_state_publisher,
            spawn_entity_cmd,
            bridge_with_delay,
        ]

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
