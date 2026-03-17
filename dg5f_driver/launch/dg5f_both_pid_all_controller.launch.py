# Copyright 2025 TESOLLO
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the TESOLLO nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


from launch import LaunchDescription
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
)
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Namespace for this driver (both hands)
    ns = "dg5f_both"

    # Declare arguments
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "dg5f_right_ip",
            default_value="10.10.20.72",
            description="DG5F right gripper IP address",
        )
    )
    
    declared_arguments.append(
        DeclareLaunchArgument(
            "dg5f_right_port",
            default_value="502",
            description="DG5F right gripper port",
        )
    )
    
    # DG5F Left gripper connection params
    declared_arguments.append(
        DeclareLaunchArgument(
            "dg5f_left_ip",
            default_value="10.10.20.73",
            description="DG5F left gripper IP address",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "dg5f_left_port",
            default_value="502",
            description="DG5F left gripper port",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "fingertip_sensor",
            default_value="false",
            description="Enable fingertip force/torque sensors"
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "io",
            default_value="false",
            description="Enable IO interface"
        )
    )


    # Get XACRO arguments
    dg5f_right_ip = LaunchConfiguration("dg5f_right_ip")
    dg5f_right_port = LaunchConfiguration("dg5f_right_port")
    dg5f_left_ip = LaunchConfiguration("dg5f_left_ip")
    dg5f_left_port = LaunchConfiguration("dg5f_left_port")
    fingertip_sensor = LaunchConfiguration("fingertip_sensor")
    io = LaunchConfiguration("io")

    # Get paths to config files
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("dg5f_driver"), "urdf",
                 "dg5f_both_ros2_control.xacro"]
            ),
            " ",
            "dg5f_right_ip:=",
            dg5f_right_ip,
            " ",
            "dg5f_right_port:=",
            dg5f_right_port,
            " ",
            "dg5f_left_ip:=",
            dg5f_left_ip,
            " ",
            "dg5f_left_port:=",
            dg5f_left_port,
            " ",
            "fingertip_sensor:=",
            fingertip_sensor,
            " ",
            "io:=",
            io,
        ]
    )

    robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
        [FindPackageShare("dg5f_driver"), "config",
         "dg5f_both_pid_all_controller.yaml"]
    )

    ft_broadcaster_config = PathJoinSubstitution(
        [FindPackageShare("dg5f_driver"), "config",
         "dg5f_both_ft_broadcaster.yaml"]
    )

    # ROS2 Control Node (without FT broadcaster)
    control_node = Node(
        namespace=ns,
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers],
        remappings=[
            ("~/robot_description", "/" + ns + "/robot_description"),
        ],
        output="screen",
        condition=UnlessCondition(fingertip_sensor),
    )

    # ROS2 Control Node with FT Broadcaster (conditional)
    control_node_with_ft = Node(
        namespace=ns,
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers, ft_broadcaster_config],
        remappings=[
            ("~/robot_description", "/" + ns + "/robot_description"),
        ],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )

    # Robot State Publisher
    robot_state_pub_node = Node(
        namespace=ns,
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    # Joint State Broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "dg5f_joint_state_broadcaster",
            "-c", "/" + ns + "/controller_manager"
        ],
        output="screen",
    )

    # Spawn all individual PID controllers for each joint
    pid_controllers = [
        "rj_dg_pospid",
        "lj_dg_pospid"
    ]

    pid_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=pid_controllers + ["-c", "/" + ns + "/controller_manager"],
        output="screen",
    )

    # Right hand fingertip sensor broadcasters (conditionally loaded)
    right_fingertip_1_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_fingertip_1_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )
    right_fingertip_2_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_fingertip_2_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )
    right_fingertip_3_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_fingertip_3_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )
    right_fingertip_4_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_fingertip_4_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )
    right_fingertip_5_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_fingertip_5_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )

    # Left hand fingertip sensor broadcasters (conditionally loaded)
    left_fingertip_1_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_fingertip_1_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )
    left_fingertip_2_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_fingertip_2_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )
    left_fingertip_3_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_fingertip_3_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )
    left_fingertip_4_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_fingertip_4_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )
    left_fingertip_5_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_fingertip_5_broadcaster", "-c", "/" + ns + "/controller_manager"],
        output="screen",
        condition=IfCondition(fingertip_sensor),
    )

    # List all nodes to start
    nodes = [
        control_node,
        control_node_with_ft,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        pid_controller_spawner,
        # Right hand FT broadcasters
        right_fingertip_1_broadcaster_spawner,
        right_fingertip_2_broadcaster_spawner,
        right_fingertip_3_broadcaster_spawner,
        right_fingertip_4_broadcaster_spawner,
        right_fingertip_5_broadcaster_spawner,
        # Left hand FT broadcasters
        left_fingertip_1_broadcaster_spawner,
        left_fingertip_2_broadcaster_spawner,
        left_fingertip_3_broadcaster_spawner,
        left_fingertip_4_broadcaster_spawner,
        left_fingertip_5_broadcaster_spawner,
    ]

    return LaunchDescription(declared_arguments + nodes)
