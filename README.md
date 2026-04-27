
amr_teleop

This ROS 2 package provides the simulation bringup and teleoperation interface for a warehouse AMR using Gazebo Ignition and ROS 2 Humble.

## 🛠️ Components
- **Launch Files**: Handles Robot State Publisher and Gazebo Ignition Bridge.
- **Sensors**: Integrated 2D LiDAR, IMU, and Odometry.
- **URDF**: Modular Xacro with dynamic TF toggling.

## 🔧 Installation
1. Clone into your `src` folder:
   `git clone https://github.com/YOUR_USERNAME/amr_teleop.git`
2. Install dependencies:
   `rosdep install --from-paths . --ignore-src -y`
3. Build:
   `colcon build --packages-select amr_teleop`