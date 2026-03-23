# Copyright 2025 tesollo
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
#    * Neither the name of the tesollo nor the names of its
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
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
)
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_arguments = []

    # Per-finger tip type selection: "default" or "type1"
    for i in range(1, 6):
        declared_arguments.append(
            DeclareLaunchArgument(
                f"tip{i}_type",
                default_value="default",
                description=f"Fingertip type for finger {i} (default / type1)"
            )
        )

    declared_arguments.append(
        DeclareLaunchArgument(
            "base_type",
            default_value="default",
            description="Base type (default / short)"
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "with_mount",
            default_value="true",
            description="Include mount link (true / false)"
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "gui",
            default_value="true",
            description="Show joint_state_publisher_gui"
        )
    )

    # Launch configurations
    tip1_type = LaunchConfiguration("tip1_type")
    tip2_type = LaunchConfiguration("tip2_type")
    tip3_type = LaunchConfiguration("tip3_type")
    tip4_type = LaunchConfiguration("tip4_type")
    tip5_type = LaunchConfiguration("tip5_type")
    base_type = LaunchConfiguration("base_type")
    with_mount = LaunchConfiguration("with_mount")
    show_gui = LaunchConfiguration("gui")

    # Build robot description from xacro with per-finger tip types
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("dg5f_description"), "urdf",
                 "dg5f_right_display.xacro"]
            ),
            " ", "tip1_type:=", tip1_type,
            " ", "tip2_type:=", tip2_type,
            " ", "tip3_type:=", tip3_type,
            " ", "tip4_type:=", tip4_type,
            " ", "tip5_type:=", tip5_type,
            " ", "base_type:=", base_type,
            " ", "with_mount:=", with_mount,
        ]
    )

    robot_description = {"robot_description": robot_description_content}

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("dg5f_description"), "config",
         "dg5f_right_display.rviz"]
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[robot_description],
    )

    joint_state_publisher_node = Node(
        condition=UnlessCondition(show_gui),
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
    )

    joint_state_publisher_gui_node = Node(
        condition=IfCondition(show_gui),
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_file],
        output="screen",
    )

    return LaunchDescription(
        declared_arguments
        + [
            robot_state_publisher_node,
            joint_state_publisher_node,
            joint_state_publisher_gui_node,
            rviz_node,
        ]
    )
