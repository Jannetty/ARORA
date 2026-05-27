"""Track individual left-pericycle XPP cells as they traverse the OZ.

For each cell that spends time in transition or elongation zone, record
(height, auxin, dist_from_tip, t) at every sample tick. Plot each cell's
trajectory as a line in (height, auxin) space — this mirrors VDB's
proposed mechanism: a tall cell entering the loading zone should accumulate
more auxin than a short cell.

Run:
    uv run python3 scripts/track_xpp_oz_trajectories.py
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.sim.simulation.sim import GrowingSim
from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum

BEST_PARAMS = pd.Series(
    [0.10974987654930562, 0.16372745814388645, 0.023203197888695095, 0.02],
    index=["ks_aux", "kd_aux", "k5", "k6"],
)

DT        = 1.0 / 9.0
MAX_HOURS = 40.0
N_TICKS   = int(MAX_HOURS / DT)
SAMPLE_DT = 5   # every 5 ticks (~0.56 h)

EVAL_DIR  = REPO / "evaluation"


def build_sim():
    return GrowingSim(800, 600, "xpp_traj", timestep=DT, vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_NO_ARR,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=BEST_PARAMS, geometry="default")


def snap_left_peri_oz(sim: GrowingSim) -> pd.DataFrame:
    """Left-side pericycle cells currently in TZ or EZ."""
    rows = []
    all_cells = sim.cell_list
    min_y = min(v.get_y() for c in all_cells for v in c.get_quad_perimeter().get_vs())
    for c in all_cells:
        if c.get_cell_type() != "peri":
            continue
        if c.get_dev_zone() not in ("transition", "elongation"):
            continue
        qp = c.get_quad_perimeter()
        vs = qp.get_vs()
        ys = [v.get_y() for v in vs]
        xs = [v.get_x() for v in vs]
        cx = sum(xs) / 4
        cy = sum(ys) / 4
        rows.append({
            "cell_id":  c.get_c_id(),
            "dev_zone": c.get_dev_zone(),
            "dist":     cy - min_y,
            "cx":       cx,
            "height":   qp.get_height(),
            "auxin":    c.get_circ_mod().auxin,
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        mid = df["cx"].median()
        df = df[df["cx"] < mid].reset_index(drop=True)
    return df


def main():
    EVAL_DIR.mkdir(exist_ok=True)
    sim = build_sim()

    # cell_id → list of (t, height, auxin, dist, dev_zone)
    trajectories: dict[int, list] = {}

    print(f"Running {N_TICKS} ticks ({MAX_HOURS} h)…")
    for tick in range(N_TICKS + 1):
        sim.on_update(DT)
        if tick % SAMPLE_DT == 0:
            t = tick * DT
            df = snap_left_peri_oz(sim)
            for _, row in df.iterrows():
                cid = int(row["cell_id"])
                trajectories.setdefault(cid, []).append(
                    (t, float(row["height"]), float(row["auxin"]),
                     float(row["dist"]), row["dev_zone"])
                )
            if tick % 50 == 0:
                print(f"  t={t:.1f} h  ({len(df)} left OZ peri cells tracked)")

    # Keep only cells seen at ≥ 4 sample points (meaningful trajectory)
    long_traj = {cid: pts for cid, pts in trajectories.items() if len(pts) >= 4}
    print(f"\n{len(long_traj)} cells with ≥4 OZ time points")

    # ── Figure 1: height vs auxin trajectories (one line per cell) ──────────
    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = cm.get_cmap("plasma")
    cell_ids = sorted(long_traj.keys())
    colors = cmap(np.linspace(0, 1, max(len(cell_ids), 1)))

    for color, cid in zip(colors, cell_ids):
        pts = long_traj[cid]
        ts      = [p[0] for p in pts]
        heights = [p[1] for p in pts]
        auxins  = [p[2] for p in pts]
        ax.plot(heights, auxins, color=color, lw=1.2, alpha=0.7)
        # mark entry (first OZ point) with a circle, exit with a triangle
        ax.scatter(heights[0],  auxins[0],  marker="o", color=color, s=30, zorder=5)
        ax.scatter(heights[-1], auxins[-1], marker="^", color=color, s=30, zorder=5)

    ax.set_xlabel("Cell height (µm)")
    ax.set_ylabel("Auxin (a.u.)")
    ax.set_title("Left XPP cell trajectories through OZ\n"
                 "circle = OZ entry, triangle = OZ exit; color = cell identity\n"
                 "VDB predicts: taller cells → more auxin (positive slope)")
    ax.grid(alpha=0.3)

    # Compute overall height–auxin correlation across all trajectory points
    all_h, all_a = [], []
    for pts in long_traj.values():
        all_h.extend(p[1] for p in pts)
        all_a.extend(p[2] for p in pts)
    if len(all_h) > 2:
        r = float(np.corrcoef(all_h, all_a)[0, 1])
        ax.text(0.02, 0.97, f"Pearson r (all traj. pts) = {r:.3f}",
                transform=ax.transAxes, va="top", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7))

    fig.tight_layout()
    out = EVAL_DIR / "xpp_oz_height_auxin_trajectories.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"# wrote {out}")

    # ── Figure 2: height and auxin vs time for same cells ───────────────────
    n = min(len(long_traj), 12)   # show up to 12 cells
    sampled_ids = list(long_traj.keys())[:n]
    colors12 = cmap(np.linspace(0, 1, max(n, 1)))

    fig2, (ax_h, ax_a) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for color, cid in zip(colors12, sampled_ids):
        pts = long_traj[cid]
        ts      = [p[0] for p in pts]
        heights = [p[1] for p in pts]
        auxins  = [p[2] for p in pts]
        ax_h.plot(ts, heights, color=color, lw=1.2, label=f"c{cid}")
        ax_a.plot(ts, auxins,  color=color, lw=1.2)

    ax_h.set_ylabel("Cell height (µm)")
    ax_h.set_title("Individual XPP cell height and auxin while in OZ")
    ax_h.grid(alpha=0.3)
    ax_h.legend(fontsize=6, ncol=3, loc="upper right")

    ax_a.set_ylabel("Auxin (a.u.)")
    ax_a.set_xlabel("Simulation time (h)")
    ax_a.grid(alpha=0.3)

    fig2.tight_layout()
    out2 = EVAL_DIR / "xpp_oz_timeseries_per_cell.png"
    fig2.savefig(out2, dpi=130)
    plt.close(fig2)
    print(f"# wrote {out2}")

    # ── Summary stats ────────────────────────────────────────────────────────
    print(f"\nHeight–auxin correlation across all OZ trajectory points: r={r:.3f}")
    print(f"  (VDB predicts r > 0; r < 0 means tall cells have LESS auxin)")
    entry_heights = [long_traj[cid][0][1] for cid in long_traj]
    print(f"\nEntry heights into OZ: "
          f"min={min(entry_heights):.1f}  max={max(entry_heights):.1f}  "
          f"mean={np.mean(entry_heights):.1f}  CV={np.std(entry_heights)/np.mean(entry_heights):.3f} µm")


if __name__ == "__main__":
    raise SystemExit(main())
