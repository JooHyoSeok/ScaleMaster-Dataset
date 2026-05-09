# ScaleMaster Dataset

**Have We Mastered Scale in Deep Monocular Visual SLAM? The ScaleMaster Dataset and Benchmark**

[Project Page](https://scalemaster-dataset.github.io) | [Paper](https://scalemaster-dataset.github.io/aprl_icra26_hsju.pdf) | [Request Access](https://forms.gle/C7jjz3hiT5JHppJ87)

Hyoseok Ju, Bokeon Suh, and Giseop Kim — DGIST, Republic of Korea

---

## Abstract

Recent advances in deep monocular visual SLAM have achieved impressive accuracy and dense reconstruction capabilities, yet their robustness to scale inconsistency in large-scale indoor environments remains largely unexplored. Existing benchmarks are limited to room-scale or structurally simple settings, leaving critical issues of intra-session scale drift and inter-session scale ambiguity insufficiently addressed. To fill this gap, we introduce the **ScaleMaster Dataset**, the first benchmark explicitly designed to evaluate scale consistency under challenging scenarios such as multi-floor structures, long trajectories, repetitive views, and low-texture regions. We systematically analyze the vulnerability of state-of-the-art deep monocular visual SLAM systems to scale inconsistency, providing both qualitative and quantitative evaluations. Crucially, our analysis extends beyond traditional trajectory metrics to include a direct map-to-map quality assessment using metrics like Chamfer distance against high-fidelity 3D ground truth.

---

## Comparison with Existing Benchmarks

| Dataset | Sequences | Avg. Length | Resolution | Multi-floor & Elevation | Pure Rotation | Complex Indoor | Scale Study |
|---------|-----------|-------------|------------|------------------------|---------------|----------------|-------------|
| EuRoC | 11 | 81.2 m | 752×480 | △ | ✓ | ✗ | ✗ |
| TUM-RGBD | ~39 | 12.2 m | 640×480 | ✗ | ✓ | ✓ | ✗ |
| 7-Scenes | 7 | 64.3 m | 640×480 | ✗ | ✓ | ✓ | ✗ |
| ARKitScenes | >5,000 | <100 m | 1920×1440 | ✗ | ○ | ✓ | ✗ |
| **ScaleMaster (Ours)** | **25** | **152.2 m** | **1920×1440** | **✓** | **✓** | **✓** | **✓** |

---

## Dataset Sequences

| Sequence | Frames | Length (m) | Duration (s) | Environment | Tags |
|----------|--------|-----------|--------------|-------------|------|
| Basement_01 | 2036 | 29.11 | 67 | Basement area followed by staircase ascent | Indoor, Short trajectory, 3D Map |
| HotelRoom_01 | 4217 | 29.07 | 141 | Interior traversal of a hotel room | Indoor, Repetitive view, Short trajectory |
| Lab_01 | 2167 | 25.85 | 72 | In-place rotations inside a lab room | Indoor, Repetitive view, Short trajectory |
| LargeHall_01 | 22830 | 884.12 | 761 | Full loop covering the entire LargeHall | Indoor, Very long trajectory |
| LargeHall_02 | 6576 | 241.89 | 219 | Evening traversal of a large open hall, low-light | Indoor, Long trajectory, 3D Map |
| LargeHall_03 | 2764 | 109.89 | 92 | Short loop inside the LargeHall at night | Indoor, Low-texture risk, Medium trajectory |
| LargeHall_04 | 4331 | 179.69 | 144 | Loop around the E1 section of LargeHall | Indoor, Medium trajectory |
| LargeHall_05 | 1912 | 54.21 | 63 | Traversal under low-light conditions | Indoor, Short trajectory, 3D Map |
| Library_01 | 6515 | 254.98 | 217 | Multi-floor descent from 5F to 3F with loops per floor | Indoor, Long trajectory, Repetitive view, 3D Map |
| Library_02 | 5001 | 163.58 | 166 | Single-floor loop on 4F with repetitive bookshelves | Indoor, Medium trajectory, 3D Map |
| Library_03 | 3136 | 105.81 | 105 | Loop on the 3rd floor of the library | Indoor, Medium trajectory |
| Library_04 | 5450 | 146.22 | 182 | Walking paths between library bookshelves | Indoor, Repetitive view, Medium trajectory |
| Library_05 | 2540 | 78.24 | 85 | Large open central atrium (depth sensor limitation) | Indoor, Low-texture risk, Short trajectory |
| Library_06 | 2026 | 13.27 | 67 | 360-degree in-place rotation at the library center | Indoor, Short trajectory, 3D Map |
| Library_07 | 1580 | 5.23 | 52 | Static panoramic survey from the 1st floor | Indoor, Short trajectory, 3D Map |
| Library_08 | 2241 | 3.51 | 75 | Short traversal around the open central viewpoint | Indoor, Low-texture risk, Short trajectory |
| Library_09 | 2303 | 20.65 | 77 | In-place rotation in front of a 3F glass room | Indoor, Repetitive view, Short trajectory |
| Lobby_01 | 2893 | 104.83 | 96 | Traversal inside a lobby | Indoor, Medium trajectory |
| Lounge_01 | 6823 | 199.09 | 228 | Loop trajectory inside a lounge area | Indoor, Medium trajectory |
| Office_01 | 6009 | 154.50 | 200 | Traversal inside a repetitive office view | Indoor, Repetitive view, Medium trajectory |
| Parking_01 | 8218 | 323.01 | 274 | Full loop inside the underground parking lot (B2) | Underground, Long trajectory |
| Parking_02 | 2270 | 88.06 | 76 | Loop in an indoor parking area | Indoor, Short trajectory |
| Stairs_01 | 9394 | 298.42 | 313 | Ascending from 2F to 6F; then looping on 6F | Indoor, Vertical motion, Repetitive view, Long trajectory |
| Stairs_02 | 4143 | 122.23 | 139 | Repeated ascending and descending of stairs | Indoor, Vertical motion, Repetitive view, Medium trajectory |
| Station_01 | 1715 | 170.84 | 229 | Escalator traversal inside a train station | Indoor/Outdoor, Vertical motion, Repetitive view, Medium trajectory |

Trajectory length tags: 0–100 m = Short; 100–200 m = Medium; >200 m = Long.

---

## Hardware

Data was collected using a custom handheld rig equipped with:
- **iPhone 14 Pro** — RGB images (1920×1440), ARKit VIO odometry, ARKit depth maps
- **Livox HAP LiDAR** — dense 3D point cloud ground truth
- **Orbbec Gemini 335L** — auxiliary RGB-D camera

---

## Ground Truth Pipeline

Raw ARKit trajectories are refined through the following pipeline:

1. **ARKit VIO** — 6-DoF poses from Apple ARKit
2. **HLoc loop closure** — NetVLAD retrieval + SuperPoint/LightGlue geometric verification
3. **Manual verification** — interactive accept/reject of loop closure candidates
4. **SE(3) pose refinement** — metric depth from Depth Anything V3 to compute 6-DoF relative transforms between loop pairs
5. **GTSAM PGO** — pose graph optimization over odometry and loop closure edges

The final refined trajectory is provided as `optimized_odometry.csv`.

---

## Data Format

Each sequence is distributed as a `.tar.gz` archive with the following structure:

```
SequenceName/
├── camera_matrix.csv        # 3×3 camera intrinsics
├── frames/                  # RGB images (frame_00000.jpg, ...)  [1920×1440]
├── depth/                   # ARKit depth maps (000000.png, ...)
├── confidence/              # ARKit depth confidence maps (000000.png, ...)
├── imu.csv                  # IMU measurements
├── odometry.csv             # Raw ARKit trajectory
├── optimized_odometry.csv   # SE(3)-refined trajectory (ground truth poses)
├── rgb.mp4                  # Original video
└── SequenceName.pcd         # LiDAR point cloud GT (7 sequences only)
```

### Trajectory Format (`odometry.csv`, `optimized_odometry.csv`)

```
timestamp, frame, x, y, z, qx, qy, qz, qw
```

- Position in meters, quaternion in scalar-last format
- Coordinate frame: ARKit world frame (Y-up)

### IMU Format (`imu.csv`)

```
timestamp, a_x, a_y, a_z, alpha_x, alpha_y, alpha_z
```

- Linear acceleration (m/s²) and angular velocity (rad/s)

### LiDAR Ground Truth (`.pcd`)

Available for 7 sequences: `Basement_01`, `LargeHall_02`, `LargeHall_05`, `Library_01`, `Library_02`, `Library_06`, `Library_07`

---

## Download

Dataset access is provided upon request:

**[Request Access via Google Form](https://forms.gle/C7jjz3hiT5JHppJ87)**

---

## Citation

```bibtex
@inproceedings{ju2026scalemaster,
  title={Have We Mastered Scale in Deep Monocular Visual SLAM? The ScaleMaster Dataset and Benchmark},
  author={Ju, Hyoseok and Suh, Bokeon and Kim, Giseop},
  booktitle={Proceedings of the IEEE International Conference on Robotics and Automation (ICRA)},
  year={2026},
  note={To appear}
}
```

---

## License

This dataset is released for non-commercial research use only.
