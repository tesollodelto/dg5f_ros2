# Manus 글러브 → DG5F 리타게팅

이 패키지는 Manus 글러브 데이터를 받아서 DG5F 그리퍼를 제어하는 ROS2 노드를 제공합니다.

## 개요

`manus_retarget.py` 노드는 Manus 글러브 토픽을 구독하고, 손가락 인체공학적(ergonomic) 데이터를 처리하여 DG5F PID 제어기에 조인트 명령을 발행합니다.

### 시스템 구조

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  manus_ros2         │     │  manus_retarget.py   │     │  DG5F Controller    │
│  (manus_data_       │────▶│  (리타게팅 노드)      │────▶│  (pid_all_controller│
│   publisher)        │     │                      │     │   .launch.py)       │
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
      /manus_glove_0           /dg5f_left/lj_dg_pospid/reference
      /manus_glove_1           /dg5f_right/rj_dg_pospid/reference
```

## 사전 요구사항

- ROS2 (Humble 이상)
- `manus_ros2` 패키지 설치
- `manus_ros2_msgs` 패키지 설치
- DG5F 드라이버 패키지 (`dg5f_driver`)

## 사용 방법

### Step 1: DG5F PID 제어기 실행

먼저 제어하려는 손에 맞는 DG5F PID all 제어기를 실행합니다:

**왼손 사용 시**
```bash
ros2 launch dg5f_driver dg5f_left_pid_all_controller.launch.py
```

**오른손 사용 시**
```bash
ros2 launch dg5f_driver dg5f_right_pid_all_controller.launch.py
```

### Step 2: Manus 데이터 퍼블리셔 실행

Manus 글러브 데이터 퍼블리셔 노드를 실행합니다:

```bash
ros2 run manus_ros2 manus_data_publisher
```

### Step 3: 리타게팅 노드 실행

Manus 글러브 데이터를 DG5F 제어기로 전달하는 리타게팅 노드를 실행합니다:

```bash
ros2 run dg5f_driver manus_retarget.py
```

토픽을 커스텀 설정하려면:

```bash
ros2 run dg5f_driver manus_retarget.py \
    --ros-args \
    -p left_input_topic:=/manus_glove_0 \
    -p right_input_topic:=/manus_glove_1 \
    -p left_output_topic:=/dg5f_left/lj_dg_pospid/reference \
    -p right_output_topic:=/dg5f_right/rj_dg_pospid/reference
```

## 토픽

### 구독 토픽

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/manus_glove_0` | `manus_ros2_msgs/ManusGlove` | 왼손 글러브 데이터 |
| `/manus_glove_1` | `manus_ros2_msgs/ManusGlove` | 오른손 글러브 데이터 |

### 발행 토픽

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/dg5f_left/lj_dg_pospid/reference` | `control_msgs/MultiDOFCommand` | 왼손 그리퍼 조인트 명령 |
| `/dg5f_right/rj_dg_pospid/reference` | `control_msgs/MultiDOFCommand` | 오른손 그리퍼 조인트 명령 |

## 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `left_input_topic` | `/manus_glove_0` | 왼손 Manus 글러브 데이터 토픽 |
| `right_input_topic` | `/manus_glove_1` | 오른손 Manus 글러브 데이터 토픽 |
| `left_output_topic` | `/dg5f_left/lj_dg_pospid/reference` | 왼손 그리퍼 명령 토픽 |
| `right_output_topic` | `/dg5f_right/rj_dg_pospid/reference` | 오른손 그리퍼 명령 토픽 |

## 조인트 매핑

이 노드는 Manus 글러브의 20개 인체공학적 값을 DG5F의 20개 조인트(손가락당 4개 × 5개 손가락)로 매핑합니다:

| 손가락 | Joint 1 (벌림) | Joint 2 (MCP) | Joint 3 (PIP) | Joint 4 (DIP) |
|--------|----------------|---------------|---------------|---------------|
| 엄지   | `*j_dg_1_1` | `*j_dg_1_2` | `*j_dg_1_3` | `*j_dg_1_4` |
| 검지   | `*j_dg_2_1` | `*j_dg_2_2` | `*j_dg_2_3` | `*j_dg_2_4` |
| 중지   | `*j_dg_3_1` | `*j_dg_3_2` | `*j_dg_3_3` | `*j_dg_3_4` |
| 약지   | `*j_dg_4_1` | `*j_dg_4_2` | `*j_dg_4_3` | `*j_dg_4_4` |
| 소지   | `*j_dg_5_1` | `*j_dg_5_2` | `*j_dg_5_3` | `*j_dg_5_4` |

> 참고: `*`는 왼손은 `l`, 오른손은 `r`입니다.

## 리타게팅 관련 중요 사항

### 룰 베이스 휴리스틱 방식

이 리타게팅 구현은 학습된 모델이 아닌 **룰 베이스 휴리스틱 방식**을 사용합니다. 따라서:

1. **Manus 캘리브레이션 의존성**: 리타게팅 품질은 Manus 글러브의 캘리브레이션 상태에 크게 의존합니다. 캘리브레이션이 잘못되면 손가락 추적과 그리퍼 제어가 부정확해집니다.

2. **조인트 스페이스 매핑**: 리타게팅이 **조인트 스페이스**(태스크 스페이스가 아님)에서 동작하므로, 직접적인 매핑이지만 특정 용도에 따라 수동 튜닝이 필요할 수 있습니다.

3. **캘리브레이션 값 조정 필요**: 코드 내 `calib` 배열의 스케일링 팩터는 다음에 따라 조정이 필요할 수 있습니다:
   - 사용자의 손 크기와 손가락 비율
   - 특정 작업에 대한 원하는 그리퍼 동작
   - 인간 손의 기구학과 DG5F 그리퍼 기구학의 차이

### 캘리브레이션 튜닝

`manus_retarget.py`의 캘리브레이션 값을 수정할 수 있습니다:

```python
# 그리퍼 캘리브레이션 데이터 (양손 공통)
calib = [1, 1.6, 1.3, 1.3,    # 엄지
         1, 1, 1.3, 1.7,      # 검지
         1, 1, 1.3, 1.7,      # 중지
         1, 1, 1.3, 1.7,      # 약지
         1, 1, 1, 1]          # 소지
```

- **값 > 1.0**: 조인트 움직임 증폭 (그리퍼가 사람 손가락보다 더 많이 움직임)
- **값 < 1.0**: 조인트 움직임 감소 (그리퍼가 사람 손가락보다 덜 움직임)
- **값 = 1.0**: 1:1 매핑

### 모범 사용법

1. **Manus 글러브를 반드시 캘리브레이션** 하고 사용하세요 (Manus Core 소프트웨어 사용)
2. **느린 움직임으로 먼저 테스트**하여 매핑이 올바르게 작동하는지 확인하세요
3. 특정 손가락이 과도하게/부족하게 반응하면 **캘리브레이션 값을 조정**하세요
4. **조인트 한계 확인** - 값은 URDF에 정의된 한계로 자동 클램핑됩니다

## 빠른 시작 (전체 명령어)

```bash
# 터미널 1: DG5F 제어기 실행 (하나 선택)
ros2 launch dg5f_driver dg5f_left_pid_all_controller.launch.py

# 터미널 2: Manus 데이터 퍼블리셔 실행
ros2 run manus_ros2 manus_data_publisher

# 터미널 3: 리타게팅 노드 실행
ros2 run dg5f_driver manus_retarget.py
```
