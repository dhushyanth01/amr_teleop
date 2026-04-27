import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():

    # 1. Specify the package and URDF file
    pkg_name = 'amr_teleop'
    file_subpath = 'urdf/core_robot.xacro'

    # 2. Process Xacro into raw XML
    xacro_file = os.path.join(get_package_share_directory(pkg_name), file_subpath)
    robot_description_raw = xacro.process_file(xacro_file).toxml()
    world_path = os.path.join(get_package_share_directory(pkg_name), 'worlds', 'obstacles.sdf')

    # 3. Start the Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw, 'use_sim_time': True}]
    )

    # 4. Launch Gazebo Ignition 
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': f'-r {world_path}'}.items()
    )

    # 5. Spawn the Robot into the 3D world
    spawn_entity = Node(
        package='ros_gz_sim', 
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'my_amr_teleop'
        ],
        output='screen'
    )
    
    # 6. EKF Configuration Path
    ekf_config_path = os.path.join(
        get_package_share_directory('amr_teleop'),
        'config',
        'ekf.yaml'
    )

    # 7. Create the EKF Node
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_path,{'use_sim_time': True} ]
    )

    # 8. THE BRIDGE: Translates ROS 2 topics to Ignition topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU'
        ],
        remappings=[
            ('/model/my_amr_teleop/tf', '/tf')
        ],
        output='screen'
    )

    # Boot everything up!
    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
        bridge,
        ekf_node
    ])