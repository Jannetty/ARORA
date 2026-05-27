"""Plan 3 §5 E2 — E3_noARR: intervention run on the LRC-geometry-extension branch.

Runs a 26-hour (234-tick) simulation with:
  - `IMPOSED_PIN_NO_ARR` + `IMPOSED` PIN rules  (ARR clamped to 0; VDB-aligned)
  - The extended LRC geometry (Plan 2 γ option, 858 cells)
  - osc_search_03 best chromosome trimmed to 4 params (ks_aux, kd_aux, k5, k6)

This mirrors scripts/run_e3_intervention.py but uses the ARR-free model to
structurally align with the VDB 2021 pure reflux-and-growth mechanism.

Outputs:
  - param_est/e3_noARR_output.csv   (full per-cell, per-tick state)
  - evaluation/noARR_intervention_run.csv      (OZ XPP per-tick mean auxin)
  - evaluation/noARR_intervention_c693_auxin.png (time-series plot)
  - evaluation/noARR_intervention_summary.txt   (oscillation score, peak count)

Run:
    uv run python3 scripts/run_e3_noARR.py
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
from param_est.fitness_functions import oscillation_score_from_csv

# IMPOSED_PIN_NO_ARR uses 4 params only (ARR-related params are no-ops)
PARAM_NAMES = ["ks_aux", "kd_aux", "k5", "k6"]
BEST_PARAMS = pd.Series(
    [
        0.10974987654930562,   # ks_aux  (osc_search_03 best, same value)
        0.16372745814388645,   # kd_aux  (osc_search_03 best, same value)
        0.023203197888695095,  # k5      (osc_search_03 best, same value)
        0.02,                  # k6      (osc_search_03 best, same value)
    ],
    index=PARAM_NAMES,
)

MAX_HOURS = 144.0
DT_HOURS = 1.0 / 9.0
N_TICKS = int(MAX_HOURS / DT_HOURS)   # 234

OUT_RAW_BASE = REPO / "param_est" / "e3_noARR_output"
EVAL_DIR = REPO / "evaluation"
SUMMARY_CSV = EVAL_DIR / "noARR_intervention_run.csv"
PLOT_PATH = EVAL_DIR / "noARR_intervention_c693_auxin.png"
SUMMARY_TXT = EVAL_DIR / "noARR_intervention_summary.txt"


def build_sim() -> GrowingSim:
    return GrowingSim(
        800, 600, "E3_noARR",
        timestep=DT_HOURS,
        vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_NO_ARR,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=BEST_PARAMS,
        geometry="default",
        output_file=str(OUT_RAW_BASE.relative_to(REPO)),
        max_hours=MAX_HOURS,
        output_frequency=1,
    )


def cleanup_tick_jsons() -> None:
    for f in OUT_RAW_BASE.parent.glob(OUT_RAW_BASE.name + "*.json"):
        f.unlink(missing_ok=True)


def main() -> int:
    import io, contextlib
    EVAL_DIR.mkdir(exist_ok=True)
    raw_csv = OUT_RAW_BASE.with_suffix(".csv")
    if raw_csv.exists():
        raw_csv.unlink()
    cleanup_tick_jsons()

    print(f"# E3_noARR — IMPOSED_PIN_NO_ARR, {N_TICKS} ticks at dt={DT_HOURS:.4f} h")
    print(f"# total simulated time: {MAX_HOURS} h")
    print(f"# params: {dict(BEST_PARAMS)}")
    print()

    sim = build_sim()
    print(f"# cells: {len(sim.cell_list)} (expected 858 for option γ)")

    # Verify ARR is 0 before starting
    sample = sim.cell_list[0]
    assert sample.get_circ_mod().arr == 0.0, "arr not 0 at t=0"
    assert sample.get_circ_mod().get_pin_reg_factor() == 1.0, "reg factor not 1.0 at t=0"
    print("# pre-run check: arr==0 and reg==1.0 confirmed")

    buf = io.StringIO()
    print("# running...", end="", flush=True)
    for t in range(N_TICKS + 1):
        if t % 25 == 0:
            print(f" {t}", end="", flush=True)
        with contextlib.redirect_stdout(buf):
            sim.on_update(DT_HOURS)
    print(" done")
    print(f"# final tick: {sim.get_tick()}")

    # Verify ARR stayed 0 throughout (spot-check at end)
    any_nonzero_arr = any(c.get_circ_mod().arr != 0.0 for c in sim.cell_list)
    print(f"# post-run check: any cell has arr != 0? {any_nonzero_arr} (expected False)")

    if not raw_csv.exists():
        print(f"ERROR: expected output CSV not found at {raw_csv}")
        return 1

    print(f"# reading {raw_csv}")
    df = pd.read_csv(raw_csv, usecols=["tick", "cell", "dev_zone", "cell_type", "auxin"])
    print(f"# rows in CSV: {len(df)}")

    oz_xpp = df[
        df["dev_zone"].isin(["transition", "elongation"]) &
        (df["cell_type"] == "peri")
    ]
    print(f"# OZ XPP rows: {len(oz_xpp)} "
          f"({oz_xpp['cell'].nunique()} unique cells across "
          f"{oz_xpp['tick'].nunique()} ticks)")

    agg = (
        oz_xpp.groupby("tick")["auxin"]
        .agg(["mean", "std", "min", "max"])
        .sort_index()
        .reset_index()
    )
    agg.to_csv(SUMMARY_CSV, index=False)
    print(f"# wrote per-tick aggregate to {SUMMARY_CSV}")

    score = oscillation_score_from_csv(str(raw_csv))
    print(f"# oscillation_score_from_csv: {score:.4f}")

    final_tick = int(df["tick"].max())
    final_aux = oz_xpp[oz_xpp["tick"] == final_tick]["auxin"].values
    fft_amps = np.abs(np.fft.fft(final_aux))
    freqs = np.fft.fftfreq(len(final_aux))
    fft_amps[np.abs(freqs) > 0.1] = 0
    legacy_fft_peak = float(np.max(fft_amps))
    print(f"# legacy FFT peak at final tick: {legacy_fft_peak:.4f}")

    c693 = df[df["cell"] == 693].sort_values("tick")
    plt.figure(figsize=(10, 5))
    plt.plot(c693["tick"] * DT_HOURS, c693["auxin"], label="c693 auxin (OZ XPP)")
    plt.plot(agg["tick"] * DT_HOURS, agg["mean"], label="mean OZ XPP auxin",
             linewidth=1.5, color="C1")
    plt.fill_between(
        agg["tick"] * DT_HOURS,
        agg["mean"] - agg["std"], agg["mean"] + agg["std"],
        alpha=0.15, color="C1", label="± 1 std across OZ XPP cells",
    )
    plt.xlabel("time (h)")
    plt.ylabel("auxin")
    plt.title(f"E3_noARR — IMPOSED_PIN_NO_ARR (ARR=0, VDB-aligned)\n"
              f"oscillation_score = {score:.3f},  legacy FFT = {legacy_fft_peak:.2f}")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=120)
    print(f"# wrote plot to {PLOT_PATH}")

    summary_lines = [
        f"E3_noARR intervention summary (Plan 3 §5 E2)",
        f"  branch: lrc-geometry-extension",
        f"  circ_mod: IMPOSED_PIN_NO_ARR  (ARR clamped to 0, VDB-aligned)",
        f"  params: osc_search_03 best trimmed to 4 (ks_aux, kd_aux, k5, k6)",
        f"  ticks: {N_TICKS}  dt: {DT_HOURS:.4f} h  total: {MAX_HOURS} h",
        f"  cells: {len(sim.cell_list)}",
        f"  OZ XPP cells observed: {oz_xpp['cell'].nunique()}",
        f"",
        f"  oscillation_score_from_csv: {score:.4f}",
        f"  legacy FFT peak (final tick): {legacy_fft_peak:.4f}",
        f"",
        f"  Plan 3 §5 E2 pass criteria:",
        f"    oscillation_score >= 0.3  ->  {score:.4f}  {'PASS' if score >= 0.3 else 'FAIL'}",
        f"    >= 2 visible peaks in 2nd half  ->  see plot",
        f"",
        f"  Compare to Plan 2 E3 (ARR-coupled): oscillation_score = 0.1840",
    ]
    SUMMARY_TXT.write_text("\n".join(summary_lines) + "\n")
    print(f"# wrote summary to {SUMMARY_TXT}")

    cleanup_tick_jsons()
    print("# cleaned up per-tick JSON files")

    print()
    print("E3_noARR RUN COMPLETE.")
    print(f"  oscillation_score: {score:.4f}  (pass threshold: >= 0.3)")
    print(f"  legacy FFT peak:   {legacy_fft_peak:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
