# DG5F ROS 2

ROS 2 packages for the **Delto Gripper DG5F** (5-finger robotic hand, left/right).

## Packages

| Package | Description |
|---|---|
| `dg5f_description` | URDF/xacro model, meshes, and RViz display launch |
| `dg5f_driver` | ros2_control hardware driver and controller launch files |
| `dg5f_gz` | Gazebo simulation |

## Dependencies

This repository requires the following packages to build:

```bash
# Clone into your ROS 2 workspace src directory
git clone https://github.com/tesollodelto/dg_hardware.git
git clone https://github.com/tesollodelto/dg_tcp_comm.git
```

- [`delto_hardware`](https://github.com/tesollodelto/dg_hardware) — Unified hardware interface for Delto grippers
- [`delto_tcp_comm`](https://github.com/tesollodelto/dg_tcp_comm) — TCP communication library for Delto grippers

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select dg5f_description dg5f_driver dg5f_gz
source install/setup.bash
```

## Launch

```bash
# RViz display
ros2 launch dg5f_description dg5f_right_display.launch.py
ros2 launch dg5f_description dg5f_left_display.launch.py

# Hardware driver
ros2 launch dg5f_driver dg5f_right_driver.launch.py
ros2 launch dg5f_driver dg5f_left_driver.launch.py

# Effort controller
ros2 launch dg5f_driver dg5f_right_effort_controller.launch.py
ros2 launch dg5f_driver dg5f_left_effort_controller.launch.py

# Gazebo simulation
ros2 launch dg5f_gz dg5f_right_gz.launch.py
ros2 launch dg5f_gz dg5f_left_gz.launch.py
ros2 launch dg5f_gz dg5f_both_gz.launch.py
```
