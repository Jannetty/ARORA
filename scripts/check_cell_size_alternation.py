"""Investigate whether ARORA produces cell-size alternation in OZ XPP cells.

VDB 2021 claims oscillation arises from meristematic cell-division cycles
creating alternating cell sizes in the TZ/EZ pericycle. As these alternating-
size cells pass through the auxin loading zone, the size difference translates
into alternating auxin levels — the spatial wave that becomes temporal
oscillation at a fixed location.

This script:
  1. Runs a GrowingSim to several checkpoints (tick 50, 100, 200)
  2. At each checkpoint extracts height + auxin for all pericycle cells in TZ+EZ
  3. Sorts by y-centroid (shootward order)
  4. Plots height vs position and auxin vs position side-by-side
  5. Quantifies the degree of size alternation (peak-to-peak pattern in height)

If ARORA reproduces VDB's mechanism, we expect:
  - Alternating tall/short cells in the TZ/EZ pericycle
  - Auxin levels that correlate with cell height (larger cell = more auxin)

Run:
    uv run python3 scripts/check_cell_size_alternation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.sim.simulation.sim import GrowingSim
from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum

PARAM_NAMES = ["ks_aux", "kd_aux", "k5", "k6"]
BEST_PARAMS = pd.Series(
    [0.10974987654930562, 0.16372745814388645, 0.023203197888695095, 0.02],
    index=PARAM_NAMES,
)

DT = 1.0 / 9.0
CHECKPOINTS = [50, 100, 150, 200]
EVAL_DIR = REPO / "evaluation"


def build_sim() -> GrowingSim:
    return GrowingSim(
        800, 600, "cell_size_check",
        timestep=DT,
        vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_NO_ARR,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=BEST_PARAMS,
        geometry="default",
    )


def extract_oz_xpp(sim: GrowingSim) -> pd.DataFrame:
    """Extract height, centroid_y, and auxin for all OZ pericycle cells."""
    rows = []
    for c in sim.cell_list:
        if c.get_dev_zone() not in ("transition", "elongation"):
            continue
        if c.get_cell_type() != "peri":
            continue
        qp = c.get_quad_perimeter()
        vs = qp.get_vs()  # [tl, tr, br, bl]
        ys = [v.get_y() for v in vs]
        xs = [v.get_x() for v in vs]
        centroid_y = sum(ys) / 4
        centroid_x = sum(xs) / 4
        height = qp.get_height()
        area = c.get_area()
        state = c.get_circ_mod().get_state()
        rows.append({
            "cell_id": c.get_c_id(),
            "dev_zone": c.get_dev_zone(),
            "centroid_y": centroid_y,
            "centroid_x": centroid_x,
            "height": height,
            "area": area,
            "auxin": state["auxin"],
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("centroid_y").reset_index(drop=True)
    return df


def alternation_score(heights: np.ndarray) -> float:
    """Quantify alternation: ratio of mean absolute difference between
    adjacent cells to overall mean height. Higher = more alternating."""
    if len(heights) < 3:
        return float("nan")
    diffs = np.abs(np.diff(heights))
    return float(np.mean(diffs) / np.mean(heights))


def main() -> int:
    EVAL_DIR.mkdir(exist_ok=True)
    print("# Building simulation...")
    sim = build_sim()
    print(f"# {len(sim.cell_list)} cells loaded")

    snapshots: dict[int, pd.DataFrame] = {}

    tick = 0
    next_check = 0
    while next_check < len(CHECKPOINTS):
        target = CHECKPOINTS[next_check]
        while tick < target:
            sim.on_update(DT)
            tick += 1
        df = extract_oz_xpp(sim)
        snapshots[target] = df
        alt = alternation_score(df["height"].values) if not df.empty else float("nan")
        height_cv = float(df["height"].std() / df["height"].mean()) if not df.empty else float("nan")
        corr = float(df["height"].corr(df["auxin"])) if len(df) > 2 else float("nan")
        print(f"# tick {target:3d} ({target*DT:.1f} h): "
              f"{len(df)} OZ XPP peri cells, "
              f"height CV={height_cv:.3f}, "
              f"alt_score={alt:.3f}, "
              f"height-auxin corr={corr:.3f}")
        next_check += 1

    # Figure 1: height profiles at each checkpoint
    fig, axes = plt.subplots(len(CHECKPOINTS), 2, figsize=(12, 3 * len(CHECKPOINTS)))
    for row_idx, tick_val in enumerate(CHECKPOINTS):
        df = snapshots[tick_val]
        ax_h = axes[row_idx, 0]
        ax_a = axes[row_idx, 1]
        if df.empty:
            continue

        y_pos = df["centroid_y"].values
        heights = df["height"].values
        auxins = df["auxin"].values

        ax_h.bar(range(len(heights)), heights, color="steelblue", width=0.8)
        ax_h.set_ylabel("cell height (µm)")
        ax_h.set_title(f"tick {tick_val} ({tick_val*DT:.1f} h) — OZ XPP peri heights\n"
                       f"(sorted shootward by centroid_y, {len(heights)} cells)")
        ax_h.set_xlabel("cell index (0 = most rootward)")

        ax_a.bar(range(len(auxins)), auxins, color="darkorange", width=0.8)
        ax_a.set_ylabel("auxin (a.u.)")
        ax_a.set_title(f"tick {tick_val} ({tick_val*DT:.1f} h) — OZ XPP peri auxin")
        ax_a.set_xlabel("cell index (0 = most rootward)")

    fig.tight_layout()
    out1 = EVAL_DIR / "cell_size_alternation_profiles.png"
    fig.savefig(out1, dpi=120)
    plt.close(fig)
    print(f"# wrote {out1}")

    # Figure 2: scatter height vs auxin at final checkpoint
    df_final = snapshots[CHECKPOINTS[-1]]
    if not df_final.empty:
        fig2, ax = plt.subplots(figsize=(6, 5))
        ax.scatter(df_final["height"], df_final["auxin"],
                   c=df_final["centroid_y"], cmap="viridis", s=50, edgecolor="k", linewidth=0.4)
        sm = plt.cm.ScalarMappable(cmap="viridis",
                                   norm=plt.Normalize(df_final["centroid_y"].min(),
                                                      df_final["centroid_y"].max()))
        fig2.colorbar(sm, ax=ax, label="centroid_y (µm, shootward →)")
        ax.set_xlabel("cell height (µm)")
        ax.set_ylabel("auxin (a.u.)")
        corr = df_final["height"].corr(df_final["auxin"])
        ax.set_title(f"OZ XPP: height vs auxin at tick {CHECKPOINTS[-1]}\n"
                     f"Pearson r = {corr:.3f}  (VDB predicts r > 0)")
        ax.grid(alpha=0.3)
        fig2.tight_layout()
        out2 = EVAL_DIR / "cell_size_vs_auxin_scatter.png"
        fig2.savefig(out2, dpi=120)
        plt.close(fig2)
        print(f"# wrote {out2}")

    # Figure 3: height profile with y-axis = actual µm position (spatial view)
    fig3, axes3 = plt.subplots(1, len(CHECKPOINTS), figsize=(4 * len(CHECKPOINTS), 7),
                                sharey=False)
    for col_idx, tick_val in enumerate(CHECKPOINTS):
        df = snapshots[tick_val]
        ax = axes3[col_idx]
        if df.empty:
            continue
        # horizontal bar chart: y-axis = µm position, bar length = height
        ax.barh(df["centroid_y"], df["height"], height=df["height"] * 0.8,
                color="steelblue", alpha=0.7, label="height")
        ax.set_xlabel("cell height (µm)")
        ax.set_ylabel("centroid_y (µm from tip)" if col_idx == 0 else "")
        ax.set_title(f"t={tick_val*DT:.1f} h")
        ax.axhline(234, color="grey", linestyle="--", linewidth=0.8, alpha=0.6)  # MZ/TZ boundary
        ax.axhline(414, color="grey", linestyle=":",  linewidth=0.8, alpha=0.6)  # TZ/EZ boundary
        ax.axhline(1014, color="grey", linestyle="-.", linewidth=0.8, alpha=0.6)  # EZ/DZ boundary
        if col_idx == 0:
            ax.text(0.02, 234, " MZ/TZ", fontsize=7, va="bottom", color="grey",
                    transform=ax.get_yaxis_transform())
            ax.text(0.02, 414, " TZ/EZ", fontsize=7, va="bottom", color="grey",
                    transform=ax.get_yaxis_transform())
    fig3.suptitle("OZ XPP pericycle cell heights vs root position\n"
                  "(dashed = zone boundaries; alternation → VDB mechanism present)", fontsize=10)
    fig3.tight_layout()
    out3 = EVAL_DIR / "cell_size_spatial_profile.png"
    fig3.savefig(out3, dpi=120)
    plt.close(fig3)
    print(f"# wrote {out3}")

    # Summary table
    print()
    print("# Summary of alternation metrics:")
    print(f"{'tick':>5}  {'t(h)':>6}  {'n_cells':>8}  {'height_CV':>10}  {'alt_score':>10}  {'h-aux_corr':>11}")
    for tick_val in CHECKPOINTS:
        df = snapshots[tick_val]
        if df.empty:
            continue
        alt = alternation_score(df["height"].values)
        cv = float(df["height"].std() / df["height"].mean())
        corr = float(df["height"].corr(df["auxin"])) if len(df) > 2 else float("nan")
        print(f"{tick_val:>5}  {tick_val*DT:>6.1f}  {len(df):>8}  {cv:>10.4f}  {alt:>10.4f}  {corr:>11.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
