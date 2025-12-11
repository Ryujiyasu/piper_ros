# Piper Robot Simulation Operation Manual

This document provides instructions on how to launch and operate the Piper robot simulation in Gazebo with MoveIt2.

## 1. Environment Setup

Ensure you have sourced the workspace:

```bash
cd ~/piper
source install/setup.bash
```

## 2. Launching the Simulation

To start Gazebo and MoveIt2 together:

```bash
ros2 launch piper_with_gripper_moveit piper_gazebo_moveit.launch.py
```

### What to expect:
1.  **Gazebo** window will open, showing the robot in an empty world.
    -   *Note*: The simulation starts automatically. If the robot appears frozen and the clock (bottom left) is 0, press the **Play** button.
2.  **RViz** window will open, showing the robot model and planning interface.

### Launch Arguments

You can customize the launch by appending arguments:

| Argument | Default | Description |
| :--- | :--- | :--- |
| `use_orbbec_camera` | `true` | Attach Orbbec camera to the robot. |
| `orbbec_parent_link` | `link6` | Link to attach the camera to. |
| `orbbec_xyz` | `-0.05 0.025 0` | XYZ offset of the camera mount. |
| `orbbec_rpy` | `0 -1.57 0` | Rotation (Roll/Pitch/Yaw) of the camera mount. |
| `orbbec_mesh_dir` | (path) | Directory containing camera meshes. |
| `world` | `empty` | World to load: `empty` or `strawberry_field`. |

**Example 1:** Launch without camera:
```bash
ros2 launch piper_with_gripper_moveit piper_gazebo_moveit.launch.py use_orbbec_camera:=false
```

**Example 2:** Launch Strawberry Harvesting World:
```bash
ros2 launch piper_with_gripper_moveit piper_gazebo_moveit.launch.py world:=strawberry_field
```

## 3. Operating the Robot (RViz)

1.  **Planning**:
    -   In the "MotionPlanning" panel (usually bottom left), go to the **Planning** tab.
    -   Drag the interactive marker (ball/arrows) on the robot's end-effector in the 3D view to a desired target pose.
    -   Alternatively, use the **Joints** tab to set specific joint angles.
2.  **Execution**:
    -   Click the **Plan** button to visualize the trajectory.
    -   Click the **Execute** button to move the actual robot in Gazebo.

## 4. Camera Usage

The Orbbec camera is attached to the robot's arm by default.

-   **View Camera Feed**:
    -   In RViz, click "Add" -> "By Topic" -> Select `/orbbec/rgb/image` or `/orbbec/depth/image`.
-   **Topic Names**:
    -   RGB Image: `/orbbec/rgb/image`
    -   Depth Image: `/orbbec/depth/image`
    -   Camera Info: `/orbbec/rgb/camera_info`

## 5. Troubleshooting

-   **Robot doesn't move in Gazebo**:
    -   Check if the simulation is paused (Time = 0). Press Play.
-   **"TIMED_OUT" error in MoveIt**:
    -   Usually harmless if the robot actually moved. The execution tolerance has been relaxed to minimize this.
-   **Animation loops forever**:
    -   Uncheck "Loop Animation" in the "Planned Path" section of the MotionPlanning panel. (Default is now OFF).
