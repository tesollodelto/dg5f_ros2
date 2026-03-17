#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import rclpy
from rclpy.node import Node

from control_msgs.msg import MultiDOFCommand
from manus_ros2_msgs.msg import ManusGlove
# geometry_msgs는 입력 메시지 내부에서만 사용되므로 여기선 import 불필요

def d2r(deg: float) -> float:
    return deg * math.pi / 180.0

LEFT_JOINT_NAMES = [
    # Thumb (finger 1)
    "lj_dg_1_1", "lj_dg_1_2", "lj_dg_1_3", "lj_dg_1_4",
    # Index (finger 2)
    "lj_dg_2_1", "lj_dg_2_2", "lj_dg_2_3", "lj_dg_2_4",
    # Middle (finger 3)
    "lj_dg_3_1", "lj_dg_3_2", "lj_dg_3_3", "lj_dg_3_4",
    # Ring (finger 4)
    "lj_dg_4_1", "lj_dg_4_2", "lj_dg_4_3", "lj_dg_4_4",
    # Pinky (finger 5)
    "lj_dg_5_1", "lj_dg_5_2", "lj_dg_5_3", "lj_dg_5_4",
]

# ===== 오른손 조인트 이름 (lj_ -> rj_로 변환) =====
RIGHT_JOINT_NAMES = [name.replace("lj_", "rj_") for name in LEFT_JOINT_NAMES]

# ===== URDF에서 뽑은 limit(lower, upper) 그대로 반영 =====
LEFT_JOINT_LIMITS = {
    # Thumb (1)
    "lj_dg_1_1": (-0.8901179185171081, 0.3839724354387525),   # axis x
    "lj_dg_1_2": (0.0, math.pi),                             # axis z
    "lj_dg_1_3": (-math.pi/2, math.pi/2),                    # axis x
    "lj_dg_1_4": (-math.pi/2, math.pi/2),                    # axis x

    # Index (2)
    "lj_dg_2_1": (-0.6108652381980153, 0.4188790204786391),  # axis x
    "lj_dg_2_2": (0.0, 2.007128639793479),                   # axis y
    "lj_dg_2_3": (-math.pi/2, math.pi/2),                    # axis y
    "lj_dg_2_4": (-math.pi/2, math.pi/2),                    # axis y

    # Middle (3)
    "lj_dg_3_1": (-0.6108652381980153, 0.6108652381980153),  # axis x
    "lj_dg_3_2": (0.0, 1.9547687622336491),                  # axis y
    "lj_dg_3_3": (-math.pi/2, math.pi/2),                    # axis y
    "lj_dg_3_4": (-math.pi/2, math.pi/2),                    # axis y

    # Ring (4)
    "lj_dg_4_1": (-0.4188790204786391, 0.6108652381980153),  # axis x
    "lj_dg_4_2": (0.0, 1.9024088846738192),                  # axis y
    "lj_dg_4_3": (-math.pi/2, math.pi/2),                    # axis y
    "lj_dg_4_4": (-math.pi/2, math.pi/2),                    # axis y

    # Pinky (5)
    "lj_dg_5_1": (-1.0471975511965976, 0.017453292519943295),  # axis z
    "lj_dg_5_2": (-0.6108652381980153, 0.4188790204786391),    # axis x
    "lj_dg_5_3": (-math.pi/2, math.pi/2),                      # axis y
    "lj_dg_5_4": (-math.pi/2, math.pi/2),                      # axis y
}

# ===== 오른손 조인트 한계 (URDF에서 추출) =====
RIGHT_JOINT_LIMITS = {
    # Thumb (1) 
    "rj_dg_1_1": (-0.3839724354387525, 0.8901179185171081),   # axis x
    "rj_dg_1_2": (-math.pi, 0.0),                            # axis z
    "rj_dg_1_3": (-math.pi/2, math.pi/2),                    # axis x
    "rj_dg_1_4": (-math.pi/2, math.pi/2),                    # axis x

    # Index (2)
    "rj_dg_2_1": (-0.4188790204786391, 0.6108652381980153),  # axis x
    "rj_dg_2_2": (0.0, 2.007128639793479),                   # axis y
    "rj_dg_2_3": (-math.pi/2, math.pi/2),                    # axis y
    "rj_dg_2_4": (-math.pi/2, math.pi/2),                    # axis y

    # Middle (3)
    "rj_dg_3_1": (-0.6108652381980153, 0.6108652381980153),  # axis x
    "rj_dg_3_2": (0.0, 1.9547687622336491),                  # axis y
    "rj_dg_3_3": (-math.pi/2, math.pi/2),                    # axis y
    "rj_dg_3_4": (-math.pi/2, math.pi/2),                    # axis y

    # Ring (4)
    "rj_dg_4_1": (-0.6108652381980153, 0.4188790204786391),  # axis x
    "rj_dg_4_2": (0.0, 1.9024088846738192),                  # axis y
    "rj_dg_4_3": (-math.pi/2, math.pi/2),                    # axis y
    "rj_dg_4_4": (-math.pi/2, math.pi/2),                    # axis y

    # Pinky (5)
    "rj_dg_5_1": (-0.017453292519943295, 1.0471975511965976),  # axis z
    "rj_dg_5_2": (-0.4188790204786391, 0.6108652381980153),    # axis x
    "rj_dg_5_3": (-math.pi/2, math.pi/2),                      # axis y
    "rj_dg_5_4": (-math.pi/2, math.pi/2),                      # axis y
}



def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


class ManusBimanualRetarget(Node):
    def __init__(self):
        super().__init__('manus_bimanual_retarget')

        # 파라미터 설정
        self.left_input_topic = self.declare_parameter(
            'left_input_topic', '/manus_glove_0'
        ).get_parameter_value().string_value
        
        self.right_input_topic = self.declare_parameter(
            'right_input_topic', '/manus_glove_1'
        ).get_parameter_value().string_value
        
        self.left_output_topic = self.declare_parameter(
            'left_output_topic', '/dg5f_left/lj_dg_pospid/reference'
        ).get_parameter_value().string_value
        
        self.right_output_topic = self.declare_parameter(
            'right_output_topic', '/dg5f_right/rj_dg_pospid/reference'
        ).get_parameter_value().string_value

        # 구독자들
        self.left_sub = self.create_subscription(
            ManusGlove, self.left_input_topic, self.cb_glove, 10
        )
        self.right_sub = self.create_subscription(
            ManusGlove, self.right_input_topic, self.cb_glove, 10
        )

        # 퍼블리셔들
        self.left_pub = self.create_publisher(
            MultiDOFCommand, self.left_output_topic, 10
        )
        self.right_pub = self.create_publisher(
            MultiDOFCommand, self.right_output_topic, 10
        )

        self.get_logger().info(
            f'[BimanualRetarget] Left: {self.left_input_topic} -> '
            f'{self.left_output_topic}'
        )
        self.get_logger().info(
            f'[BimanualRetarget] Right: {self.right_input_topic} -> '
            f'{self.right_output_topic}'
        )

    def cb_glove(self, msg: ManusGlove):
        side = (msg.side or '').lower()
        
        if side == 'left':
            self._process_hand(msg, 'left')
        elif side == 'right':
            self._process_hand(msg, 'right')
        else:
            self.get_logger().warn(f'Unknown side: {side}')

    def _process_hand(self, msg: ManusGlove, hand_side: str):
        """한 손의 글러브 데이터를 처리하여 그리퍼 명령으로 변환"""
        
        # ergonomics 배열 → dict
        ergo = {}
        try:
            for e in msg.ergonomics:
                ergo[e.type] = float(e.value)  # deg  
        except Exception as ex:
            self.get_logger().warn(f'Invalid ergonomics entry: {ex}')
            return

        # q[0..19] (deg) 배열 구성 (현재 순서 그대로)
        q_deg = [
            ergo.get('ThumbMCPSpread', 0.0),
            ergo.get('ThumbMCPStretch', 0.0),
            ergo.get('ThumbPIPStretch', 0.0),
            ergo.get('ThumbDIPStretch', 0.0),
            
            ergo.get('IndexSpread', 0.0),
            ergo.get('IndexMCPStretch', 0.0),
            ergo.get('IndexPIPStretch', 0.0),
            ergo.get('IndexDIPStretch', 0.0),
            
            ergo.get('MiddleSpread', 0.0),
            ergo.get('MiddleMCPStretch', 0.0),
            ergo.get('MiddlePIPStretch', 0.0),
            ergo.get('MiddleDIPStretch', 0.0),
            
            ergo.get('RingSpread', 0.0),
            ergo.get('RingMCPStretch', 0.0),
            ergo.get('RingPIPStretch', 0.0),
            ergo.get('RingDIPStretch', 0.0),
            
            ergo.get('PinkySpread', 0.0),
            ergo.get('PinkyMCPStretch', 0.0),
            ergo.get('PinkyPIPStretch', 0.0),
            ergo.get('PinkyDIPStretch', 0.0),
        ]

        # 계산
        out_vals = self._compute_mqd_from_q(q_deg, hand_side)

        # 손에 따라 조인트 이름과 한계값 선택
        if hand_side == 'left':
            joint_names = LEFT_JOINT_NAMES
            joint_limits = LEFT_JOINT_LIMITS
            publisher = self.left_pub
        else:  # right
            joint_names = RIGHT_JOINT_NAMES
            joint_limits = RIGHT_JOINT_LIMITS
            publisher = self.right_pub

        # 조인트 한계값으로 클램핑
        clamped_vals = []
        for i, (name, val) in enumerate(zip(joint_names, out_vals)):
            if name in joint_limits:
                lo, hi = joint_limits[name]
                clamped_vals.append(clamp(val, lo, hi))
            else:
                clamped_vals.append(val)

        # 퍼블리시
        out = MultiDOFCommand()
        out.dof_names = joint_names
        out.values = out_vals
        out.values_dot = [0.0] * len(out_vals)
        publisher.publish(out)

    @staticmethod
    def _compute_mqd_from_q(q_deg, hand_side='left'):
        """C++ SetTargetLeft(q) / SetTargetRight(q) 
        입력 q_deg: 길이 20, degree 단위.
        입력 hand_side: 'left' 또는 'right'
        출력: rad 단위 리스트 길이 20.
        """
        MOTOR_COUNT = 20
        PI = math.pi
        
        # 안전: 길이 보정
        if q_deg is None:
            q_deg = [0.0] * MOTOR_COUNT
        elif len(q_deg) < MOTOR_COUNT:
            q_deg = list(q_deg) + [0.0] * (MOTOR_COUNT - len(q_deg))
        else:
            q_deg = list(q_deg[:MOTOR_COUNT])

        # 손에 따라 dir 배열 설정
        if hand_side == 'left':
            dir_arr = [-1, 1, -1, -1,
                       1, 1, 1, 1,
                       1, 1, 1, 1,
                       1, 1, 1, 1,
                       -1, 1, 1, 1]
        else:  # right
            dir_arr = [1, -1, 1, 1,
                       -1, 1, 1, 1,
                       -1, 1, 1, 1,
                       -1, 1, 1, 1,
                      1, -1, 1, 1]
        
        # 그리퍼 캘리브레이션 데이터 (양손 공통)
        calib = [1, 1.6, 1.3, 1.3,
                 1, 1, 1.3, 1.7,
                 1, 1, 1.3, 1.7,
                 1, 1, 1.3, 1.7,
                 1, 1, 1, 1]
        # qd 계산
        qd = [0.0] * MOTOR_COUNT
        
        qd[0] = (58.5 - q_deg[1]) * (PI / 180)
        qd[1] = (q_deg[0] + 20) * (PI / 180)
        qd[2] = q_deg[2] * (PI / 180)
        qd[3] = 0.5 * (q_deg[2] + q_deg[3]) * (PI / 180)
        
        qd[4] = (q_deg[4]) * (PI / 180)
        qd[5] = q_deg[5] * (PI / 180)
        qd[6] = (q_deg[6] -40.0 )* (PI / 180)
        qd[7] = q_deg[7] * (PI / 180)
        
        qd[8] = (q_deg[8]) * (PI / 180)
        qd[9] = q_deg[9] * (PI / 180)
        qd[10] = (q_deg[10] -30.0) * (PI / 180)
        qd[11] = q_deg[11] * (PI / 180)
        
        qd[12] = (q_deg[12]) * (PI / 180)
        qd[13] = q_deg[13] * (PI / 180)
        qd[14] = q_deg[14] * (PI / 180)
        qd[15] = q_deg[15] * (PI / 180)
        
        # Pinky 
        if q_deg[17] > 55 and q_deg[18] > 25 and q_deg[18] > 20:
            qd[16] = (abs(q_deg[16])) * 2 * (PI / 180)
        else:
            qd[16] =(abs(q_deg[16])) / 1.5 * (PI / 180)
        
        qd[17] = q_deg[16] * (PI / 180)
        qd[18] = q_deg[17] * (PI / 180)
        qd[19] = q_deg[18] * (PI / 180)
        
        # mQd 계산 (calibration과 direction 적용)
        mQd = [0.0] * MOTOR_COUNT
        for i in range(MOTOR_COUNT):
            mQd[i] = qd[i] * calib[i] * dir_arr[i]
        
        # 후처리: 뒤로 젖힘 방지
        for i in range(MOTOR_COUNT):
            # 스킵할 케이스들
            if i in [4, 8, 12, 17, 16]:
                continue
            
            if hand_side == 'left':
                # Left hand: case 0, 2, 3은 양수 금지
                if i in [0, 2, 3]:
                    if mQd[i] >= 0:
                        mQd[i] = 0.0
                # Left hand: case 1은 default에 포함 (음수 금지)
                else:
                    if mQd[i] <= 0:
                        mQd[i] = 0.0
            else:  # right
                # Right hand: case 1은 양수 금지
                if i == 1:
                    if mQd[i] >= 0:
                        mQd[i] = 0.0
                # Right hand: default는 음수 금지
                else:
                    if mQd[i] <= 0:
                        mQd[i] = 0.0

        return mQd


def main(args=None):
    rclpy.init(args=args)
    node = ManusBimanualRetarget()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
