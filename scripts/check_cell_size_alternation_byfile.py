"""Check cell-size alternation separately for left and right pericycle files.

The first pass (check_cell_size_alternation.py) mixed left and right files,
which could mask within-file alternation. This script separates them and
also focuses on TZ cells specifically (where VDB's mechanism predicts the
alternation is established before elongation smooths it).

Run:
    uv run python3 scripts/check_cell_size_alternation_byfile.py
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.sim.simulation.sim import GrowingSim
from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum

BEST_PARAMS = pd.Series(
    [0.10974987654930562, 0.16372745814388645, 0.023203197888695095, 0.02],
    index=["ks_aux", "kd_aux", "k5", "k6"],
)
DT = 1.0 / 9.0
EVAL_DIR = REPO / "evaluation"


def build_sim():
    return GrowingSim(800, 600, "alt_check_byfile", timestep=DT, vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_NO_ARR,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=BEST_PARAMS, geometry="default")


def extract(sim):
    rows = []
    for c in sim.cell_list:
        if c.get_dev_zone() not in ("transition", "elongation", "meristematic"):
            continue
        if c.get_cell_type() != "peri":
            continue
        qp = c.get_quad_perimeter()
        vs = qp.get_vs()
        ys = [v.get_y() for v in vs]; xs = [v.get_x() for v in vs]
        rows.append({
            "cell_id": c.get_c_id(), "dev_zone": c.get_dev_zone(),
            "cy": sum(ys)/4, "cx": sum(xs)/4,
            "height": qp.get_height(), "auxin": c.get_circ_mod().auxin,
        })
    return pd.DataFrame(rows)


def main():
    EVAL_DIR.mkdir(exist_ok=True)

    sim = build_sim()
    for t in range(200):
        if t % 50 == 0:
            print(f"  tick {t}...", flush=True)
        sim.on_update(DT)
    print("  tick 200 done")

    df = extract(sim)
    midx = df["cx"].median()
    left  = df[df["cx"] < midx].sort_values("cy").reset_index(drop=True)
    right = df[df["cx"] > midx].sort_values("cy").reset_index(drop=True)

    print(f"\nOZ + MZ XPP peri cells at tick 200: {len(df)} total (left={len(left)}, right={len(right)})")
    print()

    # Metrics per file per zone
    print(f"{'file':5s} {'zone':6s}: {'n':>4}  {'CV':>6}  {'alt':>6}  {'h-aux_r':>8}  "
          f"{'h_min':>6} {'h_mean':>7} {'h_max':>6} µm")
    print("-"*70)
    for name, side in [("LEFT", left), ("RIGHT", right)]:
        for zone_name, zone_df in [
            ("MZ",    side[side["dev_zone"] == "meristematic"]),
            ("TZ",    side[side["dev_zone"] == "transition"]),
            ("EZ",    side[side["dev_zone"] == "elongation"]),
            ("TZ+EZ", side[side["dev_zone"].isin(["transition","elongation"])]),
        ]:
            if len(zone_df) < 3:
                continue
            h = zone_df["height"].values
            a = zone_df["auxin"].values
            alt = float(np.mean(np.abs(np.diff(h))) / np.mean(h))
            cv  = float(h.std() / h.mean())
            corr = float(np.corrcoef(h, a)[0,1]) if len(h) > 2 else float("nan")
            print(f"{name:5s} {zone_name:6s}: {len(zone_df):4d}  {cv:6.3f}  {alt:6.3f}  {corr:8.3f}  "
                  f"{h.min():6.1f} {h.mean():7.1f} {h.max():6.1f}")
        print()

    # Print actual TZ heights for left file
    left_tz = left[left["dev_zone"] == "transition"].sort_values("cy")
    print(f"LEFT TZ peri cell heights at tick 200 (rootward → shootward):")
    print(f"  {'cell':>6}  {'cy µm':>8}  {'height µm':>10}  {'auxin':>8}")
    for _, r in left_tz.iterrows():
        print(f"  c{int(r.cell_id):5d}  {r.cy:8.1f}  {r.height:10.2f}  {r.auxin:8.3f}")

    # Figure: height profile per file, TZ and EZ separated
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for col, (name, side) in enumerate([("LEFT", left), ("RIGHT", right)]):
        for row, zone_label in enumerate(["transition", "elongation"]):
            zone_df = side[side["dev_zone"] == zone_label].sort_values("cy")
            ax = axes[row, col]
            if zone_df.empty:
                ax.set_visible(False)
                continue
            idxs = range(len(zone_df))
            ax2 = ax.twinx()
            ax.bar(idxs, zone_df["height"].values, color="steelblue", alpha=0.7, label="height")
            ax2.plot(idxs, zone_df["auxin"].values, "o-", color="darkorange",
                     markersize=4, linewidth=1.2, label="auxin")
            ax.set_ylabel("height (µm)", color="steelblue")
            ax2.set_ylabel("auxin (a.u.)", color="darkorange")
            ax.set_xlabel("cell index (0 = most rootward)")
            alt = float(np.mean(np.abs(np.diff(zone_df["height"].values)))
                        / np.mean(zone_df["height"].values))
            corr = float(np.corrcoef(zone_df["height"].values, zone_df["auxin"].values)[0,1])
            ax.set_title(f"{name} file — {zone_label} zone\n"
                         f"alt={alt:.3f}, h–aux r={corr:.3f}, n={len(zone_df)}")
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax2.get_legend_handles_labels()
            ax.legend(h1+h2, l1+l2, fontsize=8, loc="upper right")

    fig.suptitle("ARORA: OZ pericycle cell heights and auxin at tick 200 (~22h)\n"
                 "VDB predicts: alternating heights in TZ, positive height–auxin correlation",
                 fontsize=10)
    fig.tight_layout()
    out = EVAL_DIR / "cell_size_alternation_byfile.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"\n# wrote {out}")


if __name__ == "__main__":
    raise SystemExit(main())
