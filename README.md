# ScaleMaster Dataset

### Have We Mastered Scale in Deep Monocular Visual SLAM?

[![Project Page](https://img.shields.io/badge/Project_Page-scalemaster--dataset.github.io-4285F4?style=flat-square&logo=googlechrome&logoColor=white)](https://scalemaster-dataset.github.io)
[![Paper](https://img.shields.io/badge/Paper-ICRA_2026-B31B1B?style=flat-square&logo=readthedocs&logoColor=white)](https://scalemaster-dataset.github.io/aprl_icra26_hsju.pdf)
[![Download Dataset](https://img.shields.io/badge/Download_Dataset-Google_Form-34A853?style=flat-square&logo=google&logoColor=white)](https://forms.gle/C7jjz3hiT5JHppJ87)
[![License](https://img.shields.io/badge/License-Non--Commercial-FFB300?style=flat-square)](https://forms.gle/C7jjz3hiT5JHppJ87)

Hyoseok Ju, Bokeon Suh, and Giseop Kim — DGIST, Republic of Korea

---

## 📄 Abstract

Recent advances in deep monocular visual SLAM have achieved impressive accuracy and dense reconstruction capabilities, yet their robustness to scale inconsistency in large-scale indoor environments remains largely unexplored. Existing benchmarks are limited to room-scale or structurally simple settings, leaving critical issues of intra-session scale drift and inter-session scale ambiguity insufficiently addressed. To fill this gap, we introduce the **ScaleMaster Dataset**, the first benchmark explicitly designed to evaluate scale consistency under challenging scenarios such as multi-floor structures, long trajectories, repetitive views, and low-texture regions. We systematically analyze the vulnerability of state-of-the-art deep monocular visual SLAM systems to scale inconsistency, providing both qualitative and quantitative evaluations. Crucially, our analysis extends beyond traditional trajectory metrics to include a direct map-to-map quality assessment using Chamfer distance against high-fidelity LiDAR reference maps.

---

## 📊 Comparison with Existing Benchmarks

| Dataset | Sequences | Avg. Length | Resolution | Multi-floor & Elevation | Pure Rotation | Complex Indoor | Scale Study |
|---------|-----------|-------------|------------|:---:|:---:|:---:|:---:|
| EuRoC | 11 | 81.2 m | 752×480 | △ | ✓ | ✗ | ✗ |
| TUM-RGBD | ~39 | 12.2 m | 640×480 | ✗ | ✓ | ✓ | ✗ |
| 7-Scenes | 7 | 64.3 m | 640×480 | ✗ | ✓ | ✓ | ✗ |
| ARKitScenes | >5,000 | <100 m | 1920×1440 | ✗ | ○ | ✓ | ✗ |
| **ScaleMaster (Ours)** | **25** | **152.2 m** | **1920×1440** | **✓** | **✓** | **✓** | **✓** |

![Scale Comparison](assets/fig3_scale_comparison.png)
*Fig. 3 — ScaleMaster trajectories are orders of magnitude larger than existing benchmarks, exposing long-term scale inconsistency that room-scale datasets cannot reveal.*

---

## 🗂️ Dataset Sequences

25 sequences across diverse large-scale indoor environments. Trajectory length tags: Short < 100 m · Medium 100–200 m · Long > 200 m.

### 📚 Library (9 sequences)

| Sequence | Frames | Length (m) | Duration (s) | Description | Tags |
|----------|--------|-----------|--------------|-------------|------|
| Library_01 | 6515 | 254.98 | 217 | Multi-floor descent from 5F to 3F with loops per floor | Long, Repetitive view, LiDAR ref. |
| Library_02 | 5001 | 163.58 | 166 | Single-floor loop on 4F with repetitive bookshelves | Medium, LiDAR ref. |
| Library_03 | 3136 | 105.81 | 105 | Loop on the 3rd floor | Medium |
| Library_04 | 5450 | 146.22 | 182 | Walking paths between bookshelves | Medium, Repetitive view |
| Library_05 | 2540 | 78.24 | 85 | Large open atrium (depth sensor limitation) | Short, Low-texture |
| Library_06 | 2026 | 13.27 | 67 | 360° in-place rotation at library center | Short, LiDAR ref. |
| Library_07 | 1580 | 5.23 | 52 | Static panoramic survey from 1F | Short, LiDAR ref. |
| Library_08 | 2241 | 3.51 | 75 | Short traversal around open central viewpoint | Short, Low-texture |
| Library_09 | 2303 | 20.65 | 77 | In-place rotation in front of 3F glass room | Short, Repetitive view |

### 🏢 Large Hall (5 sequences)

| Sequence | Frames | Length (m) | Duration (s) | Description | Tags |
|----------|--------|-----------|--------------|-------------|------|
| LargeHall_01 | 22830 | 884.12 | 761 | Full loop covering the entire hall | Very Long |
| LargeHall_02 | 6576 | 241.89 | 219 | Evening traversal, low-light | Long, LiDAR ref. |
| LargeHall_03 | 2764 | 109.89 | 92 | Short loop at night | Medium, Low-texture |
| LargeHall_04 | 4331 | 179.69 | 144 | Loop around the E1 section | Medium |
| LargeHall_05 | 1912 | 54.21 | 63 | Traversal under low-light conditions | Short, LiDAR ref. |

### 🅿️ Parking & Basement (3 sequences)

| Sequence | Frames | Length (m) | Duration (s) | Description | Tags |
|----------|--------|-----------|--------------|-------------|------|
| Basement_01 | 2036 | 29.11 | 67 | Basement area followed by staircase ascent | Short, LiDAR ref. |
| Parking_01 | 8218 | 323.01 | 274 | Full loop in underground parking lot (B2) | Long |
| Parking_02 | 2270 | 88.06 | 76 | Loop in indoor parking area | Short |

### 🪜 Stairs & Station (3 sequences)

| Sequence | Frames | Length (m) | Duration (s) | Description | Tags |
|----------|--------|-----------|--------------|-------------|------|
| Stairs_01 | 9394 | 298.42 | 313 | Ascending 2F→6F then looping on 6F | Long, Vertical, Repetitive view |
| Stairs_02 | 4143 | 122.23 | 139 | Repeated ascending and descending | Medium, Vertical, Repetitive view |
| Station_01 | 1715 | 170.84 | 229 | Escalator traversal in a train station | Medium, Vertical, Repetitive view |

### 🏨 Other Indoor (5 sequences)

| Sequence | Frames | Length (m) | Duration (s) | Description | Tags |
|----------|--------|-----------|--------------|-------------|------|
| HotelRoom_01 | 4217 | 29.07 | 141 | Interior traversal of a hotel room | Short, Repetitive view |
| Lab_01 | 2167 | 25.85 | 72 | In-place rotations inside a lab room | Short, Repetitive view |
| Lobby_01 | 2893 | 104.83 | 96 | Traversal inside a lobby | Medium |
| Lounge_01 | 6823 | 199.09 | 228 | Loop trajectory inside a lounge | Medium |
| Office_01 | 6009 | 154.50 | 200 | Traversal in a repetitive office | Medium, Repetitive view |

---

## 🔧 Hardware

Data collected using a custom handheld rig:

- **iPhone 14 Pro** — RGB images (1920×1440), ARKit VIO odometry, ARKit depth maps
- **Livox HAP LiDAR** — dense 3D LiDAR reference maps (7 sequences)
- **Orbbec Gemini 335L** — auxiliary RGB-D camera

---

## 🔄 Pose Refinement Pipeline

Raw ARKit trajectories are refined through a 5-stage pipeline:

![Pipeline](assets/fig4_pipeline.png)

1. **ARKit VIO** — 6-DoF poses from Apple ARKit
2. **HLoc loop closure** — NetVLAD retrieval + SuperPoint/LightGlue geometric verification
3. **Manual verification** — interactive accept/reject of loop closure candidates
4. **SE(3) pose refinement** — metric depth from Depth Anything V3 computes 6-DoF relative transforms between loop pairs
5. **GTSAM PGO** — pose graph optimization over odometry and loop closure edges

The refined trajectory is provided as `optimized_odometry.csv`.

---

## 📁 Data Format

Each sequence is distributed as a `.tar.gz` archive:

```
SequenceName/
├── camera_matrix.csv        # 3×3 camera intrinsics
├── frames/                  # RGB images (frame_00000.jpg, ...)  [1920×1440]
├── depth/                   # ARKit depth maps (000000.png, ...)
├── confidence/              # ARKit depth confidence maps (000000.png, ...)
├── imu.csv                  # IMU measurements
├── odometry.csv             # Raw ARKit trajectory
├── optimized_odometry.csv   # SE(3)-refined trajectory
├── rgb.mp4                  # Original video
└── SequenceName.pcd         # LiDAR reference map (7 sequences only)
```

### Trajectory format (`odometry.csv`, `optimized_odometry.csv`)

```
timestamp, frame, x, y, z, qx, qy, qz, qw
```

Position in meters; quaternion in scalar-last (x, y, z, w) format; ARKit world frame (Y-up).

### IMU format (`imu.csv`)

```
timestamp, a_x, a_y, a_z, w_x, w_y, w_z
```

Linear acceleration in m/s²; angular velocity in rad/s.

### LiDAR reference maps (`.pcd`)

Available for 7 sequences: `Basement_01`, `LargeHall_02`, `LargeHall_05`, `Library_01`, `Library_02`, `Library_06`, `Library_07`

---

## 📈 Qualitative Results

Scale inconsistency failures revealed by the ScaleMaster benchmark:

![Qualitative](assets/fig5_qualitative.png)

*Fig. 5 — Left: LiDAR reference map of Library_06. Right: MASt3R-SLAM reconstruction aligned to the reference. The distance error map (warmer = larger error) reveals geometric inconsistencies invisible to trajectory-only metrics.*

---

## ⬇️ Download

Access is provided upon request:

[![Download Dataset](https://img.shields.io/badge/Download_Dataset-Google_Form-34A853?style=for-the-badge&logo=google&logoColor=white)](https://forms.gle/C7jjz3hiT5JHppJ87)

---

## 📝 Citation

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

## 📜 License

This dataset is released for non-commercial research use only.
