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
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


def d2r(deg):
    return deg * 3.141592 / 180.0


class JointTrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('joint_trajectory_publisher')
        self.publisher_ = self.create_publisher(
            JointTrajectory, '/dg5f_left/dg5f_left_controller/joint_trajectory', 10)
        timer_period = 2.0
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.joint_names = ["lj_dg_1_1", "lj_dg_1_2", "lj_dg_1_3", "lj_dg_1_4",
                            "lj_dg_2_1", "lj_dg_2_2", "lj_dg_2_3", "lj_dg_2_4",
                            "lj_dg_3_1", "lj_dg_3_2", "lj_dg_3_3", "lj_dg_3_4",
                            "lj_dg_4_1", "lj_dg_4_2", "lj_dg_4_3", "lj_dg_4_4",
                            "lj_dg_5_1", "lj_dg_5_2", "lj_dg_5_3", "lj_dg_5_4"]


# 초기값
# position:
# - -0.1954768762233649
# - 0.04363323129985824
# - -0.6457718232379019
# - 0.45727626402251437
# - 0.5951572749300664
# - 1.1641346110802178
# - 0.43982297150257105
# - -0.8726646259971648
# - 0.26878070480712674
# - 0.6562437987498679
# - 0.8115781021773633
# - -0.41015237421866746
# - -0.08726646259971647
# - 0.8377580409572782
# - 1.2112585008840648
# - -1.3316862192716734
# - 0.4852015320544236
# - 0.20245819323134223
# - 0.07853981633974483
# - 0.5846852994181004
# position:
# - 0.0942477796076938    # 1_1
# - 0.010471975511965978  # 1_2
# - 0.03490658503988659   # 1_3
# - 0.054105206811824215  # 1_4
# - 0.153588974175501     # 2_1
# - 1.4259339988793673    # 2_2
# - 1.6126842288427605    # 2_3
# - 0.6422811647339133    # 2_4
# - 0.019198621771937624  # 3_1
# - 1.3805554383275147    # 3_2
# - 1.5812683023068625    # 3_3
# - 0.7347836150896128    # 3_4
# - -0.006981317007977318  # 4_1
# - 1.4433872913993107    # 4_2
# - 1.6126842288427605    # 4_3
# - 0.8604473212332044    # 4_4
# - 0.012217304763960306  # 5_1
# - -0.10821041362364843  # 5_2
# - 1.541125729510993     # 5_3
# - 1.6580627893946132    # 5_4

        self.angles = [

            [0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0],


            [0.0942477796076938, 0.010471975511965978, 0.03490658503988659, 0.054105206811824215,
             0.153588974175501, 1.4259339988793673, 1.6126842288427605, 0.6422811647339133,
             0.019198621771937624, 1.3805554383275147, 1.5812683023068625, 0.7347836150896128,
             -0.006981317007977318, 1.4433872913993107, 1.6126842288427605, 0.8604473212332044,
             0.012217304763960306, -0.10821041362364843, 1.541125729510993, 1.6580627893946132],
        ]

        self.index = 0

    def timer_callback(self):
        message = JointTrajectory()
        message.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = self.angles[self.index]
        point.time_from_start = Duration(sec=2, nanosec=0)

        message.points.append(point)
        self.get_logger().info("Joint Trajectory  #{} publish : {}".format(
            self.index, self.angles[self.index]))
        self.publisher_.publish(message)

        self.index += 1
        if self.index >= len(self.angles):
            self.index = 0


def main(args=None):
    rclpy.init(args=args)
    joint_trajectory_publisher = JointTrajectoryPublisher()
    rclpy.spin(joint_trajectory_publisher)
    joint_trajectory_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
