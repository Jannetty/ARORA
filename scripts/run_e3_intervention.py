"""Plan 2 §8 E3 — intervention run on the LRC-geometry-extension branch.

Runs a 26-hour (234-tick) simulation with:
  - `IMPOSED_PIN_ARR_ACTIVITY` + `IMPOSED` PIN rules
  - The extended LRC geometry (this branch's state)
  - osc_search_03 best chromosome (8 parameters)

Outputs:
  - param_est/e3_intervention_output.csv (full per-cell, per-tick state)
  - evaluation/intervention_run.csv      (OZ XPP per-tick mean auxin)
  - evaluation/intervention_c693_auxin.png (time-series plot)
  - evaluation/intervention_summary.txt   (FFT/cycle score, peak count)

Note: E2 (baseline) was intentionally skipped per Sophia's direction
2026-05-21 — the diagnostic is reported relative to the published
CLAUDE.md claim that ARORA-without-LRC-extension is non-oscillatory.
E4 (sensitivity sweep) will revisit this with multiple parameter
chromosomes.

Run:
    uv run python3 scripts/run_e3_intervention.py
"""

from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Allow `import src.…` when run as a standalone script.
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.sim.simulation.sim import GrowingSim
from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum
from param_est.fitness_functions import oscillation_score_from_csv

# IMPOSED_PIN_ARR_ACTIVITY parameter order
PARAM_NAMES = ["ks_aux", "kd_aux", "ks_arr", "kd_arr", "k1", "k5", "k6", "tau"]
BEST_PARAMS = pd.Series(
    [
        0.10974987654930562,   # ks_aux
        0.16372745814388645,   # kd_aux
        0.23644894126454083,   # ks_arr
        0.43287612810830595,   # kd_arr
        5.347786360722666,     # k1
        0.023203197888695095,  # k5
        0.02,                  # k6
        8,                     # tau (int)
    ],
    index=PARAM_NAMES,
)

MAX_HOURS = 144.0
DT_HOURS = 1.0 / 9.0
N_TICKS = int(MAX_HOURS / DT_HOURS)   # 234

OUT_RAW_BASE = REPO / "param_est" / "e3_intervention_output"   # CSV + JSONs
EVAL_DIR = REPO / "evaluation"
SUMMARY_CSV = EVAL_DIR / "intervention_run.csv"
PLOT_PATH = EVAL_DIR / "intervention_c693_auxin.png"
SUMMARY_TXT = EVAL_DIR / "intervention_summary.txt"


def build_sim() -> GrowingSim:
    return GrowingSim(
        800, 600, "E3",
        timestep=DT_HOURS,
        vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_ARR_ACTIVITY,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=BEST_PARAMS,
        geometry="default",
        output_file=str(OUT_RAW_BASE.relative_to(REPO)),
        max_hours=MAX_HOURS,
        output_frequency=1,
    )


def tick_silently(sim: GrowingSim) -> None:
    """Same as sim.on_update, but suppresses the per-tick stdout spam."""
    # Capture and discard stdout for the duration of the tick.
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        sim.on_update(DT_HOURS)


def cleanup_tick_jsons() -> None:
    """Delete the 234 per-tick JSON files written during the run.
    The full CSV (which oscillation_score_from_csv reads) is kept."""
    for f in OUT_RAW_BASE.parent.glob(OUT_RAW_BASE.name + "*.json"):
        f.unlink(missing_ok=True)


def main() -> int:
    EVAL_DIR.mkdir(exist_ok=True)
    # Clean any previous run output so the CSV is fresh
    raw_csv = OUT_RAW_BASE.with_suffix(".csv")
    if raw_csv.exists():
        raw_csv.unlink()
    cleanup_tick_jsons()

    print(f"# E3 intervention — IMPOSED_PIN_ARR_ACTIVITY, {N_TICKS} ticks at dt={DT_HOURS:.4f} h")
    print(f"# total simulated time: {MAX_HOURS} h")
    print()

    sim = build_sim()
    print(f"# cells: {len(sim.cell_list)} (expected 858 for option γ)")

    # Run silently (suppress per-tick stdout); print a progress bar
    print("# running...", end="", flush=True)
    for t in range(N_TICKS + 1):
        if t % 25 == 0:
            print(f" {t}", end="", flush=True)
        tick_silently(sim)
    print(" done")
    print(f"# final tick: {sim.get_tick()}")

    # --- Analyse the CSV --------------------------------------------------
    if not raw_csv.exists():
        print(f"ERROR: expected output CSV not found at {raw_csv}")
        return 1

    print(f"# reading {raw_csv}")
    df = pd.read_csv(raw_csv, usecols=["tick", "cell", "dev_zone", "cell_type", "auxin"])
    print(f"# rows in CSV: {len(df)}")

    # OZ XPP cells
    oz_xpp = df[
        df["dev_zone"].isin(["transition", "elongation"]) &
        (df["cell_type"] == "peri")
    ]
    print(f"# OZ XPP rows: {len(oz_xpp)} "
          f"({oz_xpp['cell'].nunique()} unique cells across "
          f"{oz_xpp['tick'].nunique()} ticks)")

    # Per-tick aggregate
    agg = (
        oz_xpp.groupby("tick")["auxin"]
        .agg(["mean", "std", "min", "max"])
        .sort_index()
        .reset_index()
    )
    agg.to_csv(SUMMARY_CSV, index=False)
    print(f"# wrote per-tick aggregate to {SUMMARY_CSV}")

    # --- Oscillation score ------------------------------------------------
    score = oscillation_score_from_csv(str(raw_csv))
    print(f"# oscillation_score_from_csv: {score:.4f}")

    # Also compute the legacy plan-§7 FFT amplitude for comparison
    # (legacy = max |FFT| of auxin across OZ XPP cells, low-pass to f<=0.1).
    final_tick = int(df["tick"].max())
    final_aux = oz_xpp[oz_xpp["tick"] == final_tick]["auxin"].values
    fft_amps = np.abs(np.fft.fft(final_aux))
    freqs = np.fft.fftfreq(len(final_aux))
    fft_amps[np.abs(freqs) > 0.1] = 0
    legacy_fft_peak = float(np.max(fft_amps))
    print(f"# legacy FFT peak at final tick: {legacy_fft_peak:.4f}")

    # --- Plot the c693 auxin time series ----------------------------------
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
    plt.title(f"E3 intervention — IMPOSED_PIN_ARR_ACTIVITY, osc_search_03 params\n"
              f"oscillation_score = {score:.3f},  legacy FFT = {legacy_fft_peak:.2f}")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=120)
    print(f"# wrote plot to {PLOT_PATH}")

    # --- Summary text -----------------------------------------------------
    summary_lines = [
        f"E3 intervention summary (Plan 2 §8 E3)",
        f"  branch: lrc-geometry-extension",
        f"  circ_mod: IMPOSED_PIN_ARR_ACTIVITY",
        f"  params: osc_search_03 best chromosome",
        f"  ticks: {N_TICKS}  dt: {DT_HOURS:.4f} h  total: {MAX_HOURS} h",
        f"  cells: {len(sim.cell_list)}",
        f"  OZ XPP cells observed: {oz_xpp['cell'].nunique()}",
        f"",
        f"  oscillation_score_from_csv: {score:.4f}",
        f"  legacy FFT peak (final tick): {legacy_fft_peak:.4f}",
        f"",
        f"  Plan §8 E3 pass criteria:",
        f"    [ ] FFT_intervention > 10  -> legacy FFT = {legacy_fft_peak:.4f}",
        f"    [ ] FFT_intervention > 3 x FFT_baseline  (baseline skipped per Sophia)",
        f"    [ ] >= 2 peaks of comparable amplitude in 2nd half  -> see plot",
    ]
    SUMMARY_TXT.write_text("\n".join(summary_lines) + "\n")
    print(f"# wrote summary to {SUMMARY_TXT}")

    # Clean up per-tick JSON dumps (the full CSV is kept for re-analysis)
    cleanup_tick_jsons()
    print("# cleaned up per-tick JSON files")

    print()
    print("E3 RUN COMPLETE.")
    print(f"  oscillation_score: {score:.4f}")
    print(f"  legacy FFT peak:   {legacy_fft_peak:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
