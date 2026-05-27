"""Generate kymograph of pericycle auxin and cell height over time.

Mirrors VDB 2021 Figure 3A: upper panel = auxin, lower panel = cell height,
x-axis = simulation time (h), y-axis = distance from root tip (µm).

Each vertical column records a spatial snapshot of the left-side pericycle
at that time point. Colour encodes auxin (upper) or cell height (lower).

Run:
    uv run python3 scripts/make_kymograph.py
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.sim.simulation.sim import GrowingSim
from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum

BEST_PARAMS = pd.Series(
    [0.10974987654930562, 0.16372745814388645, 0.023203197888695095, 0.02],
    index=["ks_aux", "kd_aux", "k5", "k6"],
)

DT         = 1.0 / 9.0
MAX_HOURS  = 40.0
N_TICKS    = int(MAX_HOURS / DT)   # 360
SAMPLE_DT  = 5                     # record every 5 ticks (~0.56 h)

# y-grid for the kymograph (µm from root tip)
Y_MIN, Y_MAX, Y_STEP = 100, 1100, 5   # 5-µm bins
Y_BINS = np.arange(Y_MIN, Y_MAX, Y_STEP)

EVAL_DIR = REPO / "evaluation"


def build_sim():
    return GrowingSim(800, 600, "kymograph", timestep=DT, vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_NO_ARR,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=BEST_PARAMS, geometry="default")


def snap_left_peri(sim: GrowingSim) -> pd.DataFrame:
    """Return left-side pericycle cells with position, height, auxin."""
    rows = []
    all_cells = sim.cell_list
    min_y = min(v.get_y() for c in all_cells for v in c.get_quad_perimeter().get_vs())
    for c in all_cells:
        if c.get_cell_type() != "peri":
            continue
        qp = c.get_quad_perimeter()
        vs = qp.get_vs()
        ys = [v.get_y() for v in vs]
        xs = [v.get_x() for v in vs]
        cx = sum(xs) / 4
        cy = sum(ys) / 4
        dist_from_tip = cy - min_y
        rows.append({"dist": dist_from_tip, "cx": cx,
                     "height": qp.get_height(),
                     "auxin": c.get_circ_mod().auxin})
    df = pd.DataFrame(rows)
    # keep only left side (cx < median)
    if not df.empty:
        mid = df["cx"].median()
        df = df[df["cx"] < mid].reset_index(drop=True)
    return df


def fill_grid(df: pd.DataFrame, column: str) -> np.ndarray:
    """Map pericycle cells onto y-grid; NaN where no cell."""
    grid = np.full(len(Y_BINS), np.nan)
    for _, row in df.iterrows():
        idx = int((row["dist"] - Y_MIN) / Y_STEP)
        if 0 <= idx < len(Y_BINS):
            grid[idx] = row[column]
    return grid


def main():
    EVAL_DIR.mkdir(exist_ok=True)
    sim = build_sim()

    time_points = []   # hours
    auxin_cols  = []   # len(Y_BINS) arrays
    height_cols = []

    print(f"Running {N_TICKS} ticks ({MAX_HOURS} h), sampling every {SAMPLE_DT} ticks...")
    for t in range(N_TICKS + 1):
        sim.on_update(DT)
        if t % SAMPLE_DT == 0:
            df = snap_left_peri(sim)
            if df.empty:
                continue
            time_points.append(t * DT)
            auxin_cols.append(fill_grid(df, "auxin"))
            height_cols.append(fill_grid(df, "height"))
            if t % 50 == 0:
                print(f"  t={t*DT:.1f} h  ({len(df)} left peri cells)")

    # Assemble 2D arrays: rows = y-position, cols = time
    auxin_mat  = np.column_stack(auxin_cols)   # shape (n_ybins, n_times)
    height_mat = np.column_stack(height_cols)

    times = np.array(time_points)

    # ---- Figure ----
    fig, (ax_a, ax_h) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Auxin kymograph
    vmax_a = np.nanpercentile(auxin_mat, 98)
    im_a = ax_a.imshow(
        auxin_mat, aspect="auto", origin="lower",
        extent=[times[0], times[-1], Y_BINS[0], Y_BINS[-1]],
        cmap="hot", vmin=0, vmax=vmax_a,
    )
    plt.colorbar(im_a, ax=ax_a, label="Auxin (a.u.)", fraction=0.03, pad=0.01)
    ax_a.set_ylabel("Distance from tip (µm)")
    ax_a.set_title("ARORA pericycle kymograph — Auxin\n"
                   "(compare VDB 2021 Fig. 3A upper)")

    # Zone boundaries
    for ax in (ax_a, ax_h):
        ax.axhline(234, color="white", lw=0.8, ls="--", alpha=0.6)
        ax.axhline(414, color="white", lw=0.8, ls=":",  alpha=0.6)
        ax.axhline(1014, color="white", lw=0.8, ls="-.", alpha=0.6)
        ax.text(times[0]+0.3, 234+10, "MZ/TZ", color="white", fontsize=7, alpha=0.8)
        ax.text(times[0]+0.3, 414+10, "TZ/EZ", color="white", fontsize=7, alpha=0.8)

    # Height kymograph
    vmax_h = np.nanpercentile(height_mat, 98)
    im_h = ax_h.imshow(
        height_mat, aspect="auto", origin="lower",
        extent=[times[0], times[-1], Y_BINS[0], Y_BINS[-1]],
        cmap="viridis", vmin=0, vmax=vmax_h,
    )
    plt.colorbar(im_h, ax=ax_h, label="Cell height (µm)", fraction=0.03, pad=0.01)
    ax_h.set_xlabel("Simulation time (h)")
    ax_h.set_ylabel("Distance from tip (µm)")
    ax_h.set_title("ARORA pericycle kymograph — Cell Height\n"
                   "(compare VDB 2021 Fig. 3A lower)")

    fig.tight_layout()
    out = EVAL_DIR / "pericycle_kymograph.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"\n# wrote {out}")

    # Also plot: height of the cell nearest the TZ/EZ boundary over time
    TZ_EZ = 414.0
    boundary_heights = []
    boundary_auxins  = []
    dists_to_boundary = np.abs(Y_BINS - TZ_EZ)
    order = np.argsort(dists_to_boundary)
    for i, col_h in enumerate(height_cols):
        col_a = auxin_cols[i]
        val_h = np.nan
        val_a = np.nan
        for idx in order[:10]:
            if not np.isnan(col_h[idx]):
                val_h = col_h[idx]
                val_a = col_a[idx]
                break
        boundary_heights.append(val_h)
        boundary_auxins.append(val_a)

    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
    ax1.plot(times, boundary_heights, lw=1.2, color="steelblue")
    ax1.set_ylabel("Cell height at TZ/EZ boundary (µm)")
    ax1.set_title("Temporal variation in pericycle cell height at TZ/EZ boundary\n"
                  "(VDB predicts alternating tall/short cells → auxin oscillation)")
    ax1.grid(alpha=0.3)

    ax2.plot(times, boundary_auxins, lw=1.2, color="darkorange")
    ax2.set_ylabel("Auxin at TZ/EZ boundary (a.u.)")
    ax2.set_xlabel("Simulation time (h)")
    ax2.grid(alpha=0.3)

    fig2.tight_layout()
    out2 = EVAL_DIR / "tze_boundary_timeseries.png"
    fig2.savefig(out2, dpi=120)
    plt.close(fig2)
    print(f"# wrote {out2}")

    # Print summary statistics for the boundary time series
    bh = np.array(boundary_heights)
    bh = bh[~np.isnan(bh)]
    print(f"\n# TZ/EZ boundary height over time:")
    print(f"#   min={bh.min():.2f}  max={bh.max():.2f}  mean={bh.mean():.2f}  "
          f"CV={bh.std()/bh.mean():.3f}  range={bh.max()-bh.min():.2f} µm")
    print(f"# (VDB shows range ~8–20 µm, CV ~0.2–0.4 at TZ exit)")


if __name__ == "__main__":
    raise SystemExit(main())
