import os
from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from launch.event_handlers import OnProcessExit

import xacro

import re
def remove_comments(text):
    pattern = r'<!--(.*?)-->'
    return re.sub(pattern, '', text, flags=re.DOTALL)

def generate_launch_description():
    robot_name_in_model = 'piper'
    package_name = 'piper_description'
    urdf_name = "piper_description_gazebo.xacro"

    pkg_share = FindPackageShare(package=package_name).find(package_name)
    urdf_model_path = os.path.join(pkg_share, f'urdf/{urdf_name}')
    empty_world = '/usr/local/share/gz/gz-sim9/worlds/empty.sdf'
    world_name = 'empty'

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

    # Render xacro with Gazebo Sim-specific plugins
    doc = xacro.process_file(urdf_model_path, mappings={'use_gz': 'true'})
    robot_description_xml = remove_comments(doc.toxml())
    params = {'robot_description': robot_description_xml}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'use_sim_time': True}, params, {"publish_frequency":15.0}],
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
        output='screen'
    )

    load_joint_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller', '--controller-manager', '/controller_manager'],
        output='screen'
        )

    load_gripper_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller', '--controller-manager', '/controller_manager'],
        output='screen'
        )
    
    load_gripper8_trajectory_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper8_controller', '--controller-manager', '/controller_manager'],
        output='screen'
        )

    close_evt1 =  RegisterEventHandler( 
            event_handler=OnProcessExit(
                target_action=spawn_entity_cmd,
                on_exit=[load_joint_state_controller],
            )
    )

    close_evt2 = RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_controller,
                on_exit=[load_joint_trajectory_controller, 
                         load_gripper_trajectory_controller,
                         load_gripper8_trajectory_controller],
            )
    )

    node_gripper_mirror_controller = Node(
        package='piper_gazebo',
        executable='joint8_ctrl.py',
        output='screen'
    )

    ld = LaunchDescription()

    ld.add_action(close_evt1)
    ld.add_action(close_evt2)
    ld.add_action(gz_sim_launch)
    ld.add_action(node_gripper_mirror_controller)
    ld.add_action(node_robot_state_publisher)
    ld.add_action(spawn_entity_cmd)

    return ld
