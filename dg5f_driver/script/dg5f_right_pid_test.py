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


class PIDControlTestAll(Node):
    def __init__(self):
        super().__init__('pid_control_test_all')

        # Create publishers for each joint PID controller
        self.joint_publishers = {}
        self.joint_names = ["rj_dg_1_1", "rj_dg_1_2", "rj_dg_1_3", "rj_dg_1_4",
                            "rj_dg_2_1", "rj_dg_2_2", "rj_dg_2_3", "rj_dg_2_4",
                            "rj_dg_3_1", "rj_dg_3_2", "rj_dg_3_3", "rj_dg_3_4",
                            "rj_dg_4_1", "rj_dg_4_2", "rj_dg_4_3", "rj_dg_4_4",
                            "rj_dg_5_1", "rj_dg_5_2", "rj_dg_5_3", "rj_dg_5_4"]

        for joint_name in self.joint_names:
            topic_name = f'/dg5f_right/{joint_name}_pospid/reference'
            self.joint_publishers[joint_name] = self.create_publisher(
                MultiDOFCommand,
                topic_name,
                10
            )
            self.get_logger().info(f'Created publisher for {topic_name}')

        # Timer for sending commands
        # 100Hz for smoother control
        self.timer = self.create_timer(0.005, self.timer_callback)
        self.start_time = time.time()

    def timer_callback(self):
        current_time = time.time()
        elapsed = current_time - self.start_time

        # Different motion patterns for different joints
        for i, joint_name in enumerate(self.joint_names):
            msg = MultiDOFCommand()
            msg.dof_names = [joint_name]

            if 'j_dg_5_4' in joint_name:
                amplitude = 1.00
                frequency = 1
                phase = 0
            else:
                amplitude = 0.0
                frequency = 0.0
                phase = 0

            # Generate sinusoidal position command
            position = amplitude * \
                (math.sin(2 * math.pi * frequency * elapsed + phase))

            msg.values = [position]
            msg.values_dot = [0.0]

            self.joint_publishers[joint_name].publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = PIDControlTestAll()

    try:
        node.get_logger().info('Starting PID control test for ALL joints...')
        node.get_logger().info('All joints will move simultaneously with different phases')
        node.get_logger().info('Press Ctrl+C to stop')
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Send zero commands to all joints before stopping
        node.get_logger().info('Stopping all joints...')
        for joint_name in node.joint_names:
            zero_msg = MultiDOFCommand()
            zero_msg.dof_names = [joint_name]
            zero_msg.values = [0.0]
            zero_msg.values_dot = [0.0]
            node.joint_publishers[joint_name].publish(zero_msg)
        time.sleep(0.5)
        node.get_logger().info('Test stopped by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
