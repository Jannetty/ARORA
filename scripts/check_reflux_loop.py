"""Spatial auxin profile by cell type at steady state — reflux loop diagnostic.

Runs chromosome #6 from the E4_noARR sensitivity sweep (high auxin,
ks_aux=6.693, kd_aux=0.09805) for 26h under IMPOSED_PIN_NO_ARR.
At the final tick, plots auxin vs distance from root tip, separately for
each cell type (vasc, peri, endo, cortex, epidermis).

VDB predicts a functioning reflux loop produces:
  - vasc/peri: high auxin near tip, decreasing shootward
  - epidermis/cortex: low auxin near tip, increasing shootward (shootward flow)
  - possible auxin accumulation peak at TZ/EZ boundary (~414 µm) in peri

Run:
    uv run python3 scripts/check_reflux_loop.py
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

# E4 chromosome #6 (random_4) — highest steady-state auxin in the sweep
CHR6_PARAMS = pd.Series(
    [6.693, 0.09805, 0.2063, 0.02047],
    index=["ks_aux", "kd_aux", "k5", "k6"],
)

DT       = 1.0 / 9.0
N_TICKS  = 234   # 26 h

ZONE_COLORS = {
    "roottip":        "grey",
    "meristematic":   "steelblue",
    "transition":     "darkorange",
    "elongation":     "firebrick",
    "differentiation":"purple",
}
TYPE_MARKERS = {
    "vasc":      ("o", 5),
    "peri":      ("s", 5),
    "endo":      ("^", 4),
    "cortex":    ("D", 4),
    "epidermis": ("v", 4),
    "roottip":   ("x", 3),
}
TYPE_COLORS = {
    "vasc":      "#1f77b4",
    "peri":      "#ff7f0e",
    "endo":      "#2ca02c",
    "cortex":    "#d62728",
    "epidermis": "#9467bd",
    "roottip":   "#8c564b",
}

EVAL_DIR = REPO / "evaluation"


def build_sim():
    return GrowingSim(800, 600, "reflux_check", timestep=DT, vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_NO_ARR,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=CHR6_PARAMS, geometry="default")


def extract_all(sim: GrowingSim) -> pd.DataFrame:
    rows = []
    all_cells = sim.cell_list
    min_y = min(v.get_y() for c in all_cells for v in c.get_quad_perimeter().get_vs())
    for c in all_cells:
        qp = c.get_quad_perimeter()
        vs = qp.get_vs()
        cy = sum(v.get_y() for v in vs) / 4
        cx = sum(v.get_x() for v in vs) / 4
        rows.append({
            "cell_id":  c.get_c_id(),
            "cell_type": c.get_cell_type(),
            "dev_zone":  c.get_dev_zone(),
            "dist":      cy - min_y,
            "cx":        cx,
            "auxin":     float(c.get_circ_mod().auxin),
            "height":    qp.get_height(),
        })
    return pd.DataFrame(rows)


def main():
    EVAL_DIR.mkdir(exist_ok=True)
    print("Building sim with chr #6 params (high-auxin E4 chromosome)…")
    sim = build_sim()
    print(f"  {len(sim.cell_list)} cells")

    for t in range(N_TICKS):
        sim.on_update(DT)
        if t % 50 == 0:
            print(f"  tick {t}/{N_TICKS}", flush=True)
    print(f"  tick {N_TICKS} — done")

    df = extract_all(sim)
    # left side only
    mid_x = df["cx"].median()
    df = df[df["cx"] <= mid_x].copy()

    print(f"\nLeft-side cells at tick {N_TICKS} ({N_TICKS*DT:.1f} h): {len(df)}")
    print(f"Auxin range: {df['auxin'].min():.2f} – {df['auxin'].max():.2f} a.u.")

    # ── Figure 1: auxin vs dist from tip, one panel per cell type ────────────
    cell_types = ["vasc", "peri", "endo", "cortex", "epidermis"]
    fig, axes = plt.subplots(1, len(cell_types), figsize=(16, 5), sharey=False)

    for ax, ct in zip(axes, cell_types):
        sub = df[df["cell_type"] == ct].sort_values("dist")
        if sub.empty:
            ax.set_visible(False)
            continue
        color = TYPE_COLORS.get(ct, "grey")
        ax.scatter(sub["dist"], sub["auxin"], c=sub["dev_zone"].map(ZONE_COLORS),
                   s=20, zorder=3, edgecolors="none")
        ax.plot(sub["dist"], sub["auxin"], color=color, lw=0.8, alpha=0.5)
        ax.axvline(234,  color="grey", lw=0.8, ls="--", alpha=0.6)
        ax.axvline(414,  color="grey", lw=0.8, ls=":",  alpha=0.6)
        ax.axvline(1014, color="grey", lw=0.8, ls="-.", alpha=0.6)
        ax.set_xlabel("Distance from tip (µm)")
        ax.set_title(ct)
        ax.grid(alpha=0.3)
        if ax is axes[0]:
            ax.set_ylabel("Auxin (a.u.)")

    # legend for dev zone colours
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=z) for z, c in ZONE_COLORS.items()
                       if z != "differentiation"]
    axes[-1].legend(handles=legend_elements, fontsize=7, loc="upper right",
                    title="dev zone")

    fig.suptitle(
        f"Spatial auxin profile by cell type — left side, t={N_TICKS*DT:.0f} h\n"
        f"chr #6: ks_aux={CHR6_PARAMS['ks_aux']}, kd_aux={CHR6_PARAMS['kd_aux']}, "
        f"k5={CHR6_PARAMS['k5']}, k6={CHR6_PARAMS['k6']}\n"
        "VDB reflux: vasc/peri high near tip → low in EZ; epidermis/cortex low near tip → high in EZ",
        fontsize=9,
    )
    fig.tight_layout()
    out1 = EVAL_DIR / "reflux_loop_spatial_profile.png"
    fig.savefig(out1, dpi=130)
    plt.close(fig)
    print(f"\n# wrote {out1}")

    # ── Figure 2: all cell types on one plot, colour = cell type ─────────────
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for ct in cell_types:
        sub = df[df["cell_type"] == ct].sort_values("dist")
        if sub.empty:
            continue
        mk, ms = TYPE_MARKERS.get(ct, ("o", 4))
        ax2.scatter(sub["dist"], sub["auxin"],
                    color=TYPE_COLORS[ct], marker=mk, s=ms**2,
                    label=ct, alpha=0.8, edgecolors="none", zorder=3)
        # smoothed line
        ax2.plot(sub["dist"], sub["auxin"],
                 color=TYPE_COLORS[ct], lw=1.0, alpha=0.5)

    ax2.axvline(234,  color="grey", lw=0.8, ls="--", alpha=0.7, label="MZ/TZ")
    ax2.axvline(414,  color="grey", lw=0.8, ls=":",  alpha=0.7, label="TZ/EZ")
    ax2.axvline(1014, color="grey", lw=0.8, ls="-.", alpha=0.7, label="EZ/DZ")
    ax2.set_xlabel("Distance from tip (µm)")
    ax2.set_ylabel("Auxin (a.u.)")
    ax2.set_title(
        f"Reflux loop check — auxin vs position, all cell types (left side, t={N_TICKS*DT:.0f} h)\n"
        "VDB: vasc/peri slope negative; epidermis/cortex slope positive"
    )
    ax2.legend(fontsize=8, ncol=2)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    out2 = EVAL_DIR / "reflux_loop_overlay.png"
    fig2.savefig(out2, dpi=130)
    plt.close(fig2)
    print(f"# wrote {out2}")

    # ── Print per-type stats ──────────────────────────────────────────────────
    print("\nPer-type auxin summary (left side, all dev zones):")
    print(f"  {'type':10s}  {'n':>4}  {'min':>6}  {'mean':>6}  {'max':>6}  slope-sign")
    for ct in cell_types:
        sub = df[df["cell_type"] == ct].sort_values("dist")
        if sub.empty:
            continue
        n = len(sub)
        mn, mu, mx = sub["auxin"].min(), sub["auxin"].mean(), sub["auxin"].max()
        # rough slope: correlation of auxin with dist
        r = float(np.corrcoef(sub["dist"], sub["auxin"])[0, 1]) if n > 2 else float("nan")
        sign = "neg (rootward flow ✓)" if r < -0.3 else ("pos (shootward flow ✓)" if r > 0.3 else "flat")
        print(f"  {ct:10s}  {n:4d}  {mn:6.2f}  {mu:6.2f}  {mx:6.2f}  r={r:+.3f} {sign}")


if __name__ == "__main__":
    raise SystemExit(main())
