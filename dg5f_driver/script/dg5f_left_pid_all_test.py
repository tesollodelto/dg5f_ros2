#!/usr/bin/env python3

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


import rclpy
from rclpy.node import Node
from control_msgs.msg import MultiDOFCommand
import time
import math


def d2r(deg):
    return deg * 3.141592 / 180.0


angles = [

    [0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0],


    [0.0, 0.0, 0.0, 1.5708,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0],
]

global index
index = 0


class PIDControlTestAll(Node):
    def __init__(self):
        super().__init__('pid_control_test_all')

        # Create publishers for each joint PID controller
        self.joint_names = ["lj_dg_1_1", "lj_dg_1_2", "lj_dg_1_3", "lj_dg_1_4",
                            "lj_dg_2_1", "lj_dg_2_2", "lj_dg_2_3", "lj_dg_2_4",
                            "lj_dg_3_1", "lj_dg_3_2", "lj_dg_3_3", "lj_dg_3_4",
                            "lj_dg_4_1", "lj_dg_4_2", "lj_dg_4_3", "lj_dg_4_4",
                            "lj_dg_5_1", "lj_dg_5_2", "lj_dg_5_3", "lj_dg_5_4"]

        topic_name = '/dg5f_left/lj_dg_pospid/reference'
        self.joint_publisher = self.create_publisher(
            MultiDOFCommand,
            topic_name,
            10
        )
        self.get_logger().info(f'Created publisher for {topic_name}')

        # Timer for sending commands
        # 100Hz for smoother control
        self.timer = self.create_timer(5.0, self.timer_callback)
        self.start_time = time.time()

    def timer_callback(self):
        global index
        # Different motion patterns for different joints

        msg = MultiDOFCommand()
        msg.dof_names = self.joint_names

        position = angles[index % len(angles)]

        msg.values = position
        msg.values_dot = [0.0] * len(position)  # Same length as position array

        index = index + 1  # Increment index to alternate between angle sets

        self.joint_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = PIDControlTestAll()

    try:
        node.get_logger().info('Starting PID control test for ALL joints...')
        node.get_logger().info('All joints will move simultaneously with different phases')
        node.get_logger().info('Press Ctrl+C to stop')
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Test stopped by user')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
