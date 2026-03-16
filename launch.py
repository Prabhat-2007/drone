from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Node 1: The Altitude Controller (The Server/Publisher)
        Node(
            package='my_python_pkg',
            executable='talker',
            name='drone_operator',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ),
        # Node 2: A second instance or a different node
        # For this example, we run the same executable with a different name
        Node(
            package='my_python_pkg',
            executable='talker',
            name='altitude_monitor',
            output='screen'
        )
    ])
