# Manus Glove to DG5F Retargeting

This package provides a ROS2 node that receives Manus glove data and retargets it to control the DG5F gripper.

## Overview

The `manus_retarget.py` node subscribes to Manus glove topics, processes the ergonomic finger data, and publishes joint commands to the DG5F PID controller.

### System Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  manus_ros2         │     │  manus_retarget.py   │     │  DG5F Controller    │
│  (manus_data_       │────▶│  (Retargeting Node)  │────▶│  (pid_all_controller│
│   publisher)        │     │                      │     │   .launch.py)       │
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
      /manus_glove_0           /dg5f_left/lj_dg_pospid/reference
      /manus_glove_1           /dg5f_right/rj_dg_pospid/reference
```

## Prerequisites

- ROS2 (Humble or later)
- `manus_ros2` package installed
- `manus_ros2_msgs` package installed
- DG5F driver package (`dg5f_driver`)

## Usage

### Step 1: Launch the DG5F PID Controller

First, start the DG5F PID all controller for the hand(s) you want to control:

**For left hand**
```bash
ros2 launch dg5f_driver dg5f_left_pid_all_controller.launch.py
```

**For right hand**
```bash
ros2 launch dg5f_driver dg5f_right_pid_all_controller.launch.py
```


### Step 2: Start the Manus Data Publisher

Run the Manus glove data publisher node:

```bash
ros2 run manus_ros2 manus_data_publisher
```

### Step 3: Run the Retargeting Node

Run the retargeting node to bridge the Manus glove data to the DG5F controller:

```bash
ros2 run dg5f_driver manus_retarget.py
```

Or with custom topic parameters:

```bash
ros2 run dg5f_driver manus_retarget.py \
    --ros-args \
    -p left_input_topic:=/manus_glove_0 \
    -p right_input_topic:=/manus_glove_1 \
    -p left_output_topic:=/dg5f_left/lj_dg_pospid/reference \
    -p right_output_topic:=/dg5f_right/rj_dg_pospid/reference
```

## Topics

### Subscribed Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/manus_glove_0` | `manus_ros2_msgs/ManusGlove` | Left hand glove data |
| `/manus_glove_1` | `manus_ros2_msgs/ManusGlove` | Right hand glove data |

### Published Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/dg5f_left/lj_dg_pospid/reference` | `control_msgs/MultiDOFCommand` | Left gripper joint commands |
| `/dg5f_right/rj_dg_pospid/reference` | `control_msgs/MultiDOFCommand` | Right gripper joint commands |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `left_input_topic` | `/manus_glove_0` | Topic for left hand Manus glove data |
| `right_input_topic` | `/manus_glove_1` | Topic for right hand Manus glove data |
| `left_output_topic` | `/dg5f_left/lj_dg_pospid/reference` | Topic for left gripper commands |
| `right_output_topic` | `/dg5f_right/rj_dg_pospid/reference` | Topic for right gripper commands |

## Joint Mapping

The node maps 20 ergonomic values from the Manus glove to 20 DG5F joints (4 joints per finger × 5 fingers):

| Finger | Joint 1 (Spread) | Joint 2 (MCP) | Joint 3 (PIP) | Joint 4 (DIP) |
|--------|------------------|---------------|---------------|---------------|
| Thumb  | `*j_dg_1_1` | `*j_dg_1_2` | `*j_dg_1_3` | `*j_dg_1_4` |
| Index  | `*j_dg_2_1` | `*j_dg_2_2` | `*j_dg_2_3` | `*j_dg_2_4` |
| Middle | `*j_dg_3_1` | `*j_dg_3_2` | `*j_dg_3_3` | `*j_dg_3_4` |
| Ring   | `*j_dg_4_1` | `*j_dg_4_2` | `*j_dg_4_3` | `*j_dg_4_4` |
| Pinky  | `*j_dg_5_1` | `*j_dg_5_2` | `*j_dg_5_3` | `*j_dg_5_4` |

> Note: `*` is `l` for left hand and `r` for right hand.

## Important Notes on Retargeting

### Rule-Based Heuristic Approach

This retargeting implementation uses a **rule-based heuristic approach** rather than a learned model. This means:

1. **Manus Calibration Dependency**: The quality of retargeting heavily depends on how well the Manus glove is calibrated. Poor calibration will result in inaccurate finger tracking and gripper control.

2. **Joint Space Mapping**: Since the retargeting operates in **joint space** (not task space), the mapping is direct but may require manual tuning for specific use cases.

3. **Calibration Values May Need Adjustment**: The `calib` array in the code contains scaling factors that may need to be adjusted based on:
   - Individual user's hand size and finger proportions
   - Desired gripper behavior for specific tasks
   - Differences between human hand kinematics and DG5F gripper kinematics

### Tuning the Calibration

The calibration values in `manus_retarget.py` can be modified:

```python
# Gripper calibration data (common for both hands)
calib = [1, 1.6, 1.3, 1.3,    # Thumb
         1, 1, 1.3, 1.7,      # Index
         1, 1, 1.3, 1.7,      # Middle
         1, 1, 1.3, 1.7,      # Ring
         1, 1, 1, 1]          # Pinky
```

- **Values > 1.0**: Amplify the joint movement (gripper moves more than the human finger)
- **Values < 1.0**: Reduce the joint movement (gripper moves less than the human finger)
- **Values = 1.0**: 1:1 mapping

### Best Practices

1. **Always calibrate the Manus glove** before using this retargeting node (use Manus Core software)
2. **Test with slow movements first** to verify the mapping is working correctly
3. **Adjust calibration values** if certain fingers are over/under-responding
4. **Check joint limits** - values are automatically clamped to URDF-defined limits

## Quick Start (All Commands)

```bash
# Terminal 1: Start DG5F controller (choose one)
ros2 launch dg5f_driver dg5f_left_pid_all_controller.launch.py

# Terminal 2: Start Manus data publisher
ros2 run manus_ros2 manus_data_publisher

# Terminal 3: Start retargeting node
ros2 run dg5f_driver manus_retarget.py
```
