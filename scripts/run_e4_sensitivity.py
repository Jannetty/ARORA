"""Plan 2 §8 E4 — sensitivity sweep on the LRC-geometry-extension branch.

Runs the §8 E3 intervention diagnostic across 10 parameter chromosomes
and reports, for each, whether the geometry-extended ARORA produces
oscillation in OZ XPP cells.

Chromosome plan (intervention-only — E2 baseline skipped per Sophia
2026-05-21):

  1. osc_search_03 best (re-runs E3 for consistency in the data table)
  2. Plan-§8 fallback midpoints (geometric means of GA ranges)
  3-10. 8 log-uniform random samples from the GA paramspace

Parameter ranges follow `make_paramspace_imposed_pin_arr_activity`
in the GA runner:
  ks_aux ∈ [0.1, 10]       (log)
  kd_aux ∈ [0.05, 0.5]     (log)
  ks_arr ∈ [0.01, 1.0]     (log)
  kd_arr ∈ [0.01, 1.0]     (log)
  k1     ∈ [1.0, 200.0]    (log)
  k5     ∈ [0.02, 1.0]     (log)
  k6     ∈ [0.02, 1.0]     (log)
  tau    ∈ {5, ..., 36}    (uniform int)

Outputs:
  - evaluation/e4_sensitivity.csv          (one row per chromosome)
  - evaluation/e4_scatter.png              (oscillation_score vs legacy FFT)
  - evaluation/e4_chrom_<i>_auxin.png      (c693 trace per chromosome)
  - evaluation/e4_summary.txt              (verdict text)

Run:
    uv run python3 scripts/run_e4_sensitivity.py
"""

from __future__ import annotations

import io
import contextlib
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
from param_est.fitness_functions import oscillation_score_from_csv

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

MAX_HOURS = 144.0
DT_HOURS = 1.0 / 9.0
N_TICKS = int(MAX_HOURS / DT_HOURS)   # 234
N_CHROMOSOMES = 10
RNG_SEED = 20260521

PARAM_NAMES = ["ks_aux", "kd_aux", "ks_arr", "kd_arr", "k1", "k5", "k6", "tau"]

# GA paramspace (mirrors make_paramspace_imposed_pin_arr_activity in
# param_est/ARORA_genetic_alg_imposed_auxsyndegexport.py)
PARAM_RANGES = {
    "ks_aux": ("log",   0.1,   10.0),
    "kd_aux": ("log",   0.05,  0.5),
    "ks_arr": ("log",   0.01,  1.0),
    "kd_arr": ("log",   0.01,  1.0),
    "k1":     ("log",   1.0,   200.0),
    "k5":     ("log",   0.02,  1.0),
    "k6":     ("log",   0.02,  1.0),
    "tau":    ("int",   5,     36),
}

OSC_SEARCH_03_BEST = pd.Series(
    [0.10974987654930562, 0.16372745814388645,
     0.23644894126454083, 0.43287612810830595,
     5.347786360722666,   0.023203197888695095,
     0.02,                8],
    index=PARAM_NAMES,
)

# Geometric/arithmetic midpoints of each range
PLAN_FALLBACK_MIDPOINTS = pd.Series(
    [np.sqrt(0.1 * 10),     # ks_aux  = 1.0
     np.sqrt(0.05 * 0.5),   # kd_aux  ≈ 0.158
     np.sqrt(0.01 * 1.0),   # ks_arr  = 0.1
     np.sqrt(0.01 * 1.0),   # kd_arr  = 0.1
     np.sqrt(1.0 * 200.0),  # k1      ≈ 14.14
     np.sqrt(0.02 * 1.0),   # k5      ≈ 0.141
     np.sqrt(0.02 * 1.0),   # k6      ≈ 0.141
     20],                   # tau     = 20
    index=PARAM_NAMES,
)


def sample_chromosome(rng: np.random.Generator) -> pd.Series:
    vals = []
    for name in PARAM_NAMES:
        kind, lo, hi = PARAM_RANGES[name]
        if kind == "log":
            v = float(np.exp(rng.uniform(np.log(lo), np.log(hi))))
        elif kind == "int":
            v = int(rng.integers(lo, hi + 1))
        else:
            v = float(rng.uniform(lo, hi))
        vals.append(v)
    return pd.Series(vals, index=PARAM_NAMES)


def chromosomes() -> list[tuple[str, pd.Series]]:
    rng = np.random.default_rng(RNG_SEED)
    out: list[tuple[str, pd.Series]] = []
    out.append(("osc_search_03_best", OSC_SEARCH_03_BEST))
    out.append(("plan_fallback_midpoints", PLAN_FALLBACK_MIDPOINTS))
    for i in range(N_CHROMOSOMES - 2):
        out.append((f"random_{i+1}", sample_chromosome(rng)))
    return out


# ----------------------------------------------------------------------
# Sim runner
# ----------------------------------------------------------------------

EVAL_DIR = REPO / "evaluation"
RAW_BASE = REPO / "param_est" / "e4_chrom_output"


def build_sim(params: pd.Series, chrom_idx: int) -> GrowingSim:
    return GrowingSim(
        800, 600, f"E4-{chrom_idx}",
        timestep=DT_HOURS,
        vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_ARR_ACTIVITY,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=params,
        geometry="default",
        output_file=f"param_est/e4_chrom_{chrom_idx}_output",
        max_hours=MAX_HOURS,
        output_frequency=1,
    )


def cleanup_artifacts(chrom_idx: int) -> None:
    base = REPO / "param_est"
    for f in base.glob(f"e4_chrom_{chrom_idx}_output*.json"):
        f.unlink(missing_ok=True)


def cleanup_csv(chrom_idx: int) -> None:
    csv_path = REPO / "param_est" / f"e4_chrom_{chrom_idx}_output.csv"
    csv_path.unlink(missing_ok=True)


def run_one(chrom_idx: int, params: pd.Series) -> dict:
    """Run one 26-hour simulation, return a results dict."""
    cleanup_csv(chrom_idx)
    cleanup_artifacts(chrom_idx)

    sim = build_sim(params, chrom_idx)

    # Suppress per-tick stdout
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        for _ in range(N_TICKS + 1):
            sim.on_update(DT_HOURS)

    csv_path = REPO / "param_est" / f"e4_chrom_{chrom_idx}_output.csv"
    if not csv_path.exists():
        return {"chrom_idx": chrom_idx, "error": "no CSV produced"}

    # Oscillation score
    osc = oscillation_score_from_csv(str(csv_path))

    # Legacy FFT at final tick
    df = pd.read_csv(csv_path, usecols=["tick", "cell", "dev_zone", "cell_type", "auxin"])
    oz_xpp = df[
        df["dev_zone"].isin(["transition", "elongation"]) &
        (df["cell_type"] == "peri")
    ]
    final_tick = int(df["tick"].max())
    final_aux = oz_xpp[oz_xpp["tick"] == final_tick]["auxin"].values
    if len(final_aux) >= 2:
        amps = np.abs(np.fft.fft(final_aux))
        freqs = np.fft.fftfreq(len(final_aux))
        amps[np.abs(freqs) > 0.1] = 0
        legacy_fft = float(np.max(amps))
    else:
        legacy_fft = 0.0

    # c693 trace + per-tick mean
    c693 = df[df["cell"] == 693].sort_values("tick")
    agg = (
        oz_xpp.groupby("tick")["auxin"]
        .agg(["mean", "std"])
        .sort_index()
        .reset_index()
    )

    # Mean auxin at start/end (sanity)
    mean_first = float(agg["mean"].iloc[0]) if not agg.empty else float("nan")
    mean_last = float(agg["mean"].iloc[-1]) if not agg.empty else float("nan")
    c693_first = float(c693["auxin"].iloc[0]) if not c693.empty else float("nan")
    c693_last = float(c693["auxin"].iloc[-1]) if not c693.empty else float("nan")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(c693["tick"] * DT_HOURS, c693["auxin"], label="c693 auxin")
    ax.plot(agg["tick"] * DT_HOURS, agg["mean"], label="mean OZ XPP auxin", color="C1")
    ax.fill_between(
        agg["tick"] * DT_HOURS,
        agg["mean"] - agg["std"], agg["mean"] + agg["std"],
        alpha=0.15, color="C1",
    )
    ax.set_xlabel("time (h)")
    ax.set_ylabel("auxin")
    label = ", ".join(f"{k}={params[k]:.3g}" for k in PARAM_NAMES)
    ax.set_title(f"E4 chrom #{chrom_idx} — osc={osc:.3f}, fft={legacy_fft:.2f}\n"
                 f"{label}", fontsize=8)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    plot_path = EVAL_DIR / f"e4_chrom_{chrom_idx}_auxin.png"
    fig.savefig(plot_path, dpi=100)
    plt.close(fig)

    cleanup_artifacts(chrom_idx)
    cleanup_csv(chrom_idx)

    return {
        "chrom_idx": chrom_idx,
        **{k: float(v) for k, v in params.items()},
        "oscillation_score": float(osc),
        "legacy_fft_peak": legacy_fft,
        "mean_aux_t0": mean_first,
        "mean_aux_tf": mean_last,
        "c693_aux_t0": c693_first,
        "c693_aux_tf": c693_last,
        "plot": str(plot_path.relative_to(REPO)),
    }


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> int:
    EVAL_DIR.mkdir(exist_ok=True)

    rows = []
    chroms = chromosomes()
    print(f"# E4 sensitivity sweep — {len(chroms)} chromosomes, "
          f"{N_TICKS} ticks each at dt={DT_HOURS:.4f} h ({MAX_HOURS} h total)")
    print()

    for i, (label, params) in enumerate(chroms, start=1):
        print(f"# === chromosome #{i} ({label}) ===")
        print("# params: " + ", ".join(f"{k}={params[k]:.4g}" for k in PARAM_NAMES))
        result = run_one(i, params)
        result["label"] = label
        rows.append(result)
        print(f"# -> oscillation_score = {result.get('oscillation_score', 'ERR'):.4f}, "
              f"legacy_fft = {result.get('legacy_fft_peak', 'ERR'):.4f}, "
              f"mean_aux: t0={result.get('mean_aux_t0', 'ERR'):.2f} -> "
              f"tf={result.get('mean_aux_tf', 'ERR'):.2f}")
        print()

    # --- Save full table --------------------------------------------------
    table = pd.DataFrame(rows)
    out_csv = EVAL_DIR / "e4_sensitivity.csv"
    table.to_csv(out_csv, index=False)
    print(f"# wrote table to {out_csv}")

    # --- Scatter plot of overall sweep ------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(table["legacy_fft_peak"], table["oscillation_score"],
               s=80, c="C0", edgecolor="k")
    for _, row in table.iterrows():
        ax.annotate(f"#{int(row['chrom_idx'])}",
                    (row["legacy_fft_peak"], row["oscillation_score"]),
                    fontsize=8, xytext=(5, 5), textcoords="offset points")
    ax.axhline(0.3, color="grey", linestyle="--", alpha=0.5,
               label="oscillation_score = 0.3 (rough 'has cycles' threshold)")
    ax.axvline(10, color="orange", linestyle="--", alpha=0.5,
               label="legacy FFT = 10 (CLAUDE.md threshold)")
    ax.set_xlabel("legacy FFT peak (spatial alternation at final tick)")
    ax.set_ylabel("oscillation_score (cycle + CoV, [0,1])")
    ax.set_title("E4 sensitivity sweep — 10 chromosomes on lrc-geometry-extension")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(EVAL_DIR / "e4_scatter.png", dpi=120)
    plt.close(fig)
    print(f"# wrote scatter plot to {EVAL_DIR / 'e4_scatter.png'}")

    # --- Summary verdict --------------------------------------------------
    n_above_osc = int((table["oscillation_score"] >= 0.3).sum())
    n_above_fft = int((table["legacy_fft_peak"] > 10).sum())
    n_aux_collapse = int((table["mean_aux_tf"] < 1.0).sum())
    n_temporal_osc = int(((table["oscillation_score"] >= 0.3) &
                          (table["mean_aux_tf"] >= 1.0)).sum())

    best_osc_row = table.loc[table["oscillation_score"].idxmax()]

    summary = [
        f"E4 sensitivity sweep — verdict",
        f"  chromosomes run: {len(table)}",
        f"  branch: lrc-geometry-extension",
        f"  circ_mod: IMPOSED_PIN_ARR_ACTIVITY",
        f"",
        f"  oscillation_score >= 0.3: {n_above_osc}/{len(table)}",
        f"  legacy FFT > 10:           {n_above_fft}/{len(table)}",
        f"  auxin collapsed (tf < 1):  {n_aux_collapse}/{len(table)}",
        f"  oscillation AND auxin held: {n_temporal_osc}/{len(table)}",
        f"",
        f"  best oscillation_score: #{int(best_osc_row['chrom_idx'])} "
        f"({best_osc_row['label']}) score={best_osc_row['oscillation_score']:.4f}",
    ]
    summary_path = EVAL_DIR / "e4_summary.txt"
    summary_path.write_text("\n".join(summary) + "\n")
    print()
    print("\n".join(summary))
    print()
    print(f"# wrote summary to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
