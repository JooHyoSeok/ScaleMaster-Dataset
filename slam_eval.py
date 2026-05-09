# SLAM Map Quality Evaluator 

import os, csv, threading
import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
from scipy.spatial.transform import Rotation as R
import sys, subprocess

INIT_DIR = os.path.dirname(os.path.abspath(__file__))

def _pick_file_dialog(initial_dir: str) -> str:
    """Spawn tkinter file dialog in subprocess → returns path or ''."""
    script = (
        "import tkinter as tk, tkinter.filedialog as fd\n"
        "root=tk.Tk(); root.withdraw(); root.wm_attributes('-topmost',1)\n"
        f"p=fd.askopenfilename(initialdir={repr(initial_dir)})\n"
        "print(p)"
    )
    r = subprocess.run([sys.executable, "-c", script],
                       capture_output=True, text=True)
    return r.stdout.strip()


# ──────────────────────────────────────────────
# Core math
# ──────────────────────────────────────────────

def load_odometry(path: str) -> dict:
    """Load trajectory → {frame_idx: 4x4 pose}.

    CSV (ARKit): timestamp, frame, x, y, z, qx, qy, qz, qw  (scalar-last)
    TXT (SLAM):  timestamp x y z qw qx qy qz                 (scalar-first, space-sep)
    """
    poses = {}
    if path.endswith('.csv'):
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            fn_lower = {k.strip().lower(): k for k in reader.fieldnames}
            fk = fn_lower.get('frame')
            if fk is None:
                raise ValueError(f"No 'frame' column in {path}")
            xk, yk, zk = fn_lower['x'], fn_lower['y'], fn_lower['z']
            qxk, qyk, qzk, qwk = fn_lower['qx'], fn_lower['qy'], fn_lower['qz'], fn_lower['qw']
            for row in reader:
                try:
                    fi = int(row[fk].strip())
                    x, y, z = float(row[xk]), float(row[yk]), float(row[zk])
                    qx, qy, qz, qw = float(row[qxk]), float(row[qyk]), float(row[qzk]), float(row[qwk])
                    rot = R.from_quat([qx, qy, qz, qw]).as_matrix()
                    T = np.eye(4); T[:3, :3] = rot; T[:3, 3] = [x, y, z]
                    poses[fi] = T
                except (ValueError, KeyError):
                    continue
    else:
        # TXT (space-separated, no frame column)
        # _arkit.txt: timestamp x y z qx qy qz qw  (scalar-last)
        # other .txt:  timestamp x y z qw qx qy qz  (scalar-first, SLAM output)
        scalar_last = '_arkit' in os.path.basename(path)
        with open(path, 'r') as f:
            for fi, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) < 8:
                    continue
                try:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    if scalar_last:
                        qx, qy, qz, qw = float(parts[4]), float(parts[5]), float(parts[6]), float(parts[7])
                    else:
                        qw, qx, qy, qz = float(parts[4]), float(parts[5]), float(parts[6]), float(parts[7])
                    rot = R.from_quat([qx, qy, qz, qw]).as_matrix()
                    T = np.eye(4); T[:3, :3] = rot; T[:3, 3] = [x, y, z]
                    poses[fi] = T
                except ValueError:
                    continue
    return poses


def extract_translations(poses: dict) -> np.ndarray:
    """Sorted by frame index → (N,3)"""
    keys = sorted(poses.keys())
    return np.array([poses[k][:3, 3] for k in keys])


def compute_sim3(slam_traj_path: str, ref_traj_path: str):
    """Timestamp-matched Sim(3) via evo. Returns (s, R 3x3, t 3)."""
    from evo.tools import file_interface
    from evo.core import sync, geometry
    est = file_interface.read_tum_trajectory_file(slam_traj_path)
    ref = file_interface.read_tum_trajectory_file(ref_traj_path)
    ref_sync, est_sync = sync.associate_trajectories(ref, est)
    r, t, s = geometry.umeyama_alignment(
        est_sync.positions_xyz.T,
        ref_sync.positions_xyz.T,
        with_scale=True,
    )
    return s, r, t


def apply_sim3(pcd: o3d.geometry.PointCloud, s: float, rot: np.ndarray, t: np.ndarray):
    pts = np.asarray(pcd.points)
    pts_new = (s * rot @ pts.T).T + t
    out = o3d.geometry.PointCloud()
    out.points = o3d.utility.Vector3dVector(pts_new)
    if pcd.has_colors():
        out.colors = pcd.colors
    if pcd.has_normals():
        out.normals = pcd.normals
    return out


def jet_color(v: float) -> np.ndarray:
    """Scalar 0-1 → RGB jet"""
    r = np.clip(1.5 - abs(4 * v - 3), 0, 1)
    g = np.clip(1.5 - abs(4 * v - 2), 0, 1)
    b = np.clip(1.5 - abs(4 * v - 1), 0, 1)
    return np.array([r, g, b])


def remove_outliers(pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
    """SOR (20, 1.0) → Radius outlier removal (6, 0.06)"""
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=1.0)
    pcd, _ = pcd.remove_radius_outlier(nb_points=6, radius=0.06)
    return pcd


def compute_metrics_and_colors(slam_pcd, ref_pcd, threshold: float):
    """Returns (chamfer, drop_rate_pct, colored_slam_pcd).
    Drop rate  = % of src pts with d_src→tgt > threshold
    Chamfer    = mean(d_src_in→tgt²) + mean(d_tgt_in→src_in²)
                 computed only on matched inlier pairs (d ≤ threshold)
                 — matches paper pipeline exactly
    """
    from scipy.spatial import cKDTree

    src_pts = np.asarray(slam_pcd.points)
    tgt_pts = np.asarray(ref_pcd.points)

    kdt_tgt = cKDTree(tgt_pts)
    d_src2tgt, j = kdt_tgt.query(src_pts, k=1, workers=-1)

    drop_rate = float((d_src2tgt > threshold).mean() * 100)

    # inlier pairs only
    mask = d_src2tgt <= threshold
    src_in = src_pts[mask]
    tgt_in = tgt_pts[j[mask]]

    if len(src_in) == 0:
        chamfer = float('inf')
    else:
        kdt_src_in = cKDTree(src_in)
        d_tgt2src_in, _ = kdt_src_in.query(tgt_in, k=1, workers=-1)
        chamfer = float((d_src2tgt[mask] ** 2).mean() + (d_tgt2src_in ** 2).mean())

    norm = np.clip(d_src2tgt / threshold, 0, 1)
    colors = np.stack([
        np.clip(1.5 - np.abs(4 * norm - 3), 0, 1),
        np.clip(1.5 - np.abs(4 * norm - 2), 0, 1),
        np.clip(1.5 - np.abs(4 * norm - 1), 0, 1),
    ], axis=1)
    colored = o3d.geometry.PointCloud()
    colored.points = slam_pcd.points
    colored.colors = o3d.utility.Vector3dVector(colors)
    return chamfer, drop_rate, colored


# ──────────────────────────────────────────────
# GUI
# ──────────────────────────────────────────────

class SlamEvalApp:
    PANEL_W = 340
    EM = 14  # font em size

    def __init__(self):
        self.app = gui.Application.instance
        self.app.initialize()

        em = self.EM
        self.win = self.app.create_window("SLAM Map Quality Evaluator", 1400, 800)
        self.win.set_on_layout(self._on_layout)
        self.win.set_on_close(self._on_close)

        # ── 3D scene ──
        self.scene = gui.SceneWidget()
        self.scene.scene = rendering.Open3DScene(self.win.renderer)
        self.scene.scene.set_background([0.15, 0.15, 0.15, 1])
        self.win.add_child(self.scene)

        # ── side panel ──
        self.panel = gui.ScrollableVert(em * 0.4, gui.Margins(em * 0.5, em * 0.5, em * 0.5, em * 0.5))

        def section(title):
            cv = gui.CollapsableVert(title, em * 0.25, gui.Margins(em * 0.5, 0, 0, 0))
            cv.set_is_open(True)
            return cv

        # -- file pickers --
        fs = section("Input Files")
        self._source_edit, sb = self._file_row("Source (SLAM map PLY/PCD)", fs)
        self._target_edit, tb = self._file_row("Target (LiDAR ref PCD)", fs)
        self._slam_traj_edit, stb = self._file_row("SLAM trajectory CSV (opt.)", fs)
        self._ref_traj_edit, rtb = self._file_row("Ref trajectory CSV (opt.)", fs)
        sb.set_on_clicked(lambda: self._pick_file(self._source_edit, []))
        tb.set_on_clicked(lambda: self._pick_file(self._target_edit, []))
        stb.set_on_clicked(lambda: self._pick_file(self._slam_traj_edit, []))
        rtb.set_on_clicked(lambda: self._pick_file(self._ref_traj_edit, []))
        self.panel.add_child(fs)

        # -- threshold --
        ts = section("Threshold")
        th_row = gui.Horiz(em * 0.4)
        th_row.add_child(gui.Label("T (m):"))
        self._thresh_edit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        self._thresh_edit.set_value(1.0)
        self._thresh_edit.set_limits(0.01, 100.0)
        th_row.add_child(self._thresh_edit)
        ts.add_child(th_row)
        self._also_10 = gui.Checkbox("Also run at 10 m")
        self._also_10.checked = True
        ts.add_child(self._also_10)
        self.panel.add_child(ts)

        # -- max points --
        mp = section("Subsampling")
        self._use_maxpts = gui.Checkbox("Limit max points")
        self._use_maxpts.checked = False
        mp.add_child(self._use_maxpts)
        mp_row = gui.Horiz(em * 0.4)
        mp_row.add_child(gui.Label("Max pts:"))
        self._maxpts_edit = gui.NumberEdit(gui.NumberEdit.INT)
        self._maxpts_edit.set_value(100000)
        self._maxpts_edit.set_limits(1000, 10000000)
        mp_row.add_child(self._maxpts_edit)
        mp.add_child(mp_row)
        self.panel.add_child(mp)

        # -- actions --
        act = section("Actions")
        load_btn = gui.Button("Load & Show")
        load_btn.set_on_clicked(self._on_load)
        act.add_child(load_btn)
        run_btn = gui.Button("Run Evaluation")
        run_btn.set_on_clicked(self._on_run)
        act.add_child(run_btn)
        self.panel.add_child(act)

        # -- results --
        rs = section("Results")
        self._result_label = gui.Label("—")
        rs.add_child(self._result_label)
        self.panel.add_child(rs)

        # -- status --
        self._status = gui.Label("Ready.")
        self.panel.add_child(self._status)

        self.win.add_child(self.panel)

        # internal state
        self._source_pcd = None
        self._target_pcd = None
        self._aligned_pcd = None
        self._file_dlg_callback = None

    # ── layout ──────────────────────────────

    def _on_layout(self, layout_context):
        r = self.win.content_rect
        self.panel.frame = gui.Rect(r.x, r.y, self.PANEL_W, r.height)
        self.scene.frame = gui.Rect(r.x + self.PANEL_W, r.y,
                                    r.width - self.PANEL_W, r.height)

    def _on_close(self):
        return True

    # ── file row helper ──────────────────────

    def _file_row(self, label_text, parent):
        parent.add_child(gui.Label(label_text))
        row = gui.Horiz(4)
        edit = gui.TextEdit()
        edit.placeholder_text = "Select file…"
        row.add_child(edit)
        row.add_stretch()
        btn = gui.Button("Browse")
        row.add_child(btn)
        parent.add_child(row)
        return edit, btn

    # ── file dialog ──────────────────────────

    def _pick_file(self, target_edit, extensions):
        def _open():
            init = target_edit.text_value.strip()
            init_dir = os.path.dirname(init) if init else INIT_DIR
            if not os.path.isdir(init_dir):
                init_dir = os.path.expanduser("~")
            path = _pick_file_dialog(init_dir)
            if path:
                self.app.post_to_main_thread(
                    self.win, lambda p=path: setattr(target_edit, 'text_value', p)
                )
        threading.Thread(target=_open, daemon=True).start()

    # ── load & show ──────────────────────────

    def _on_load(self):
        src_path = self._source_edit.text_value.strip()
        tgt_path = self._target_edit.text_value.strip()
        if not src_path or not tgt_path:
            self._set_status("Select both source and target files first.")
            return
        self._set_status("Loading…")

        slam_traj_path = self._slam_traj_edit.text_value.strip()
        ref_traj_path  = self._ref_traj_edit.text_value.strip()

        def _load():
            try:
                src = o3d.io.read_point_cloud(src_path)
                n0 = len(src.points)
                src = src.voxel_down_sample(0.05)
                src = remove_outliers(src)
                n1 = len(src.points)
                print(f"[load] source: {n0:,} → {n1:,} pts (voxel+SOR+radius)")

                tgt = o3d.io.read_point_cloud(tgt_path)
                m0 = len(tgt.points)
                tgt = tgt.voxel_down_sample(0.01)
                tgt = remove_outliers(tgt)
                m1 = len(tgt.points)
                print(f"[load] target: {m0:,} → {m1:,} pts (voxel+SOR+radius)")

                # Sim(3) align at load time if trajectories provided
                if slam_traj_path and ref_traj_path:
                    print(f"[load] computing Sim(3) via evo…")
                    s, rot, t = compute_sim3(slam_traj_path, ref_traj_path)
                    src = apply_sim3(src, s, rot, t)
                    print(f"[load] Sim(3) done — scale={s:.4f}")
                    align_info = f"  (Sim3 scale={s:.3f})"
                else:
                    align_info = "  (no alignment)"

                msg = f"Source {n1:,} pts | Target {m1:,} pts{align_info}"
                self.app.post_to_main_thread(self.win, lambda s=src, t=tgt, m=msg: (
                    self._show_clouds(s, t), self._set_status(m)
                ))
            except Exception as e:
                import traceback; traceback.print_exc()
                self.app.post_to_main_thread(self.win, lambda err=str(e): self._set_status(f"Load error: {err}"))

        threading.Thread(target=_load, daemon=True).start()

    def _show_clouds(self, src, tgt, aligned=None):
        self._source_pcd = src
        self._target_pcd = tgt
        sc = self.scene.scene
        sc.clear_geometry()

        mat_src = rendering.MaterialRecord()
        mat_src.shader = "defaultUnlit"
        mat_src.point_size = 2.0

        mat_tgt = rendering.MaterialRecord()
        mat_tgt.shader = "defaultUnlit"
        mat_tgt.point_size = 2.0

        display_src = aligned if aligned is not None else src

        # target: grey
        tgt_copy = o3d.geometry.PointCloud(tgt)
        tgt_copy.paint_uniform_color([0.6, 0.6, 0.6])
        sc.add_geometry("target", tgt_copy, mat_tgt)

        # source: if no colors, paint cyan
        if not display_src.has_colors():
            src_copy = o3d.geometry.PointCloud(display_src)
            src_copy.paint_uniform_color([0.2, 0.8, 1.0])
            sc.add_geometry("source", src_copy, mat_src)
        else:
            sc.add_geometry("source", display_src, mat_src)

        # fit camera
        bounds = sc.bounding_box
        self.scene.setup_camera(60.0, bounds, bounds.get_center())
        self._set_status(f"Loaded. Source: {len(src.points):,} pts | Target: {len(tgt.points):,} pts")

    # ── run evaluation ───────────────────────

    def _on_run(self):
        src_path = self._source_edit.text_value.strip()
        tgt_path = self._target_edit.text_value.strip()
        if not src_path or not tgt_path:
            self._set_status("ERROR: select source and target files first.")
            print("[run] ERROR: no files selected")
            return

        T = self._thresh_edit.double_value
        also_10 = self._also_10.checked
        slam_traj_path = self._slam_traj_edit.text_value.strip()
        ref_traj_path  = self._ref_traj_edit.text_value.strip()
        max_pts = int(self._maxpts_edit.int_value) if self._use_maxpts.checked else None

        def post(msg):
            print(f"[run] {msg}")
            self.app.post_to_main_thread(self.win, lambda m=msg: self._set_status(m))

        def _run():
            try:
                post(f"Loading source: {os.path.basename(src_path)}")
                slam_pcd = o3d.io.read_point_cloud(src_path)
                print(f"[run] source pts: {len(slam_pcd.points)}")

                post(f"Loading target: {os.path.basename(tgt_path)}")
                ref_pcd = o3d.io.read_point_cloud(tgt_path)
                print(f"[run] target pts: {len(ref_pcd.points)}")

                if len(slam_pcd.points) == 0:
                    post("ERROR: source point cloud is empty (wrong file?)"); return
                if len(ref_pcd.points) == 0:
                    post("ERROR: target point cloud is empty (wrong file?)"); return

                # Sim(3) alignment
                if slam_traj_path and ref_traj_path:
                    post("Computing Sim(3) via evo…")
                    s, rot, t = compute_sim3(slam_traj_path, ref_traj_path)
                    slam_pcd = apply_sim3(slam_pcd, s, rot, t)
                    print(f"[run] Sim(3): scale={s:.4f}")
                    post(f"Sim(3) done — scale={s:.4f}")
                else:
                    post("No trajectories — skipping alignment (maps must share coord frame).")

                # random subsample
                if max_pts is not None:
                    def _subsample(pcd, n):
                        pts = np.asarray(pcd.points)
                        if len(pts) > n:
                            rng = np.random.default_rng(seed=42)
                            idx = rng.choice(len(pts), n, replace=False)
                            out = o3d.geometry.PointCloud()
                            out.points = o3d.utility.Vector3dVector(pts[idx])
                            if pcd.has_colors():
                                out.colors = o3d.utility.Vector3dVector(np.asarray(pcd.colors)[idx])
                            return out
                        return pcd
                    slam_pcd = _subsample(slam_pcd, max_pts)
                    ref_pcd  = _subsample(ref_pcd,  max_pts)
                    post(f"Subsampled to ≤{max_pts:,} pts each")

                thresholds = [T]
                if also_10 and abs(T - 10.0) > 0.01:
                    thresholds.append(10.0)

                lines = []
                colored_pcd = None
                for th in thresholds:
                    post(f"Computing metrics at T={th} m…")
                    chamfer, drop, col = compute_metrics_and_colors(slam_pcd, ref_pcd, th)
                    lines.append(f"T={th:.1f}m  Chamfer={chamfer:.4f}m  Drop={drop:.1f}%")
                    print(f"[run] T={th}m → chamfer={chamfer:.4f}m drop={drop:.1f}%")
                    if abs(th - T) < 0.001:
                        colored_pcd = col

                self._aligned_pcd = slam_pcd
                result_text = "\n".join(lines)
                _col = colored_pcd
                _ref = ref_pcd
                self.app.post_to_main_thread(
                    self.win,
                    lambda rt=result_text, c=_col, r=_ref: self._show_results(rt, c, r)
                )
            except Exception as e:
                import traceback; traceback.print_exc()
                post(f"ERROR: {e}")

        threading.Thread(target=_run, daemon=True).start()
        self._set_status("Started — see terminal for progress.")

    def _show_results(self, text, colored, ref_pcd):
        self._result_label.text = text
        self._target_pcd = ref_pcd
        if colored is not None:
            self._source_pcd = colored
            self._show_clouds(colored, ref_pcd, aligned=colored)
        self._set_status("Done. " + text.replace("\n", "  |  "))

    # ── helpers ─────────────────────────────

    def _set_status(self, msg):
        self._status.text = msg

    def run(self):
        self.app.run()


if __name__ == "__main__":
    app = gui.Application.instance
    SlamEvalApp().run()
