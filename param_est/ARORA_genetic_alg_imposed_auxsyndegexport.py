import json
import os
import platform
import csv
import glob
from skimage.draw import polygon
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum


if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"
import numpy as np
import pandas as pd
import pygad
from pygad import GA
from param_est.fitness_functions import (
    auxin_greater_in_larger_cells_at_trans_elon_interface,
    avg_auxin_root_tip_greater_than_elsewhere,
    parity_of_mz_auxin_concentrations_with_VDB_data,
    parity_of_auxin_c_for_xpp_boundary_cell_at_each_time_point,
    arora_vdb_ssd,
    oscillation_score_from_csv,
)
from src.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "ARORA"

DEFAULT_PARAM_NAMES = ["k_s", "k_d", "k1", "k2", "k3", "k4", "k5", "k6", "tau"]

IMPOSED_PIN_ARR_ACTIVITY_PARAM_NAMES = [
    "ks_aux",
    "kd_aux",
    "ks_arr",
    "kd_arr",
    "k1",
    "k5",
    "k6",
    "tau",
]

IMPOSED_PIN_NO_ARR_PARAM_NAMES = ["ks_aux", "kd_aux", "k5", "k6"]

def make_dumpable(obj): # lol we have to change the name of this but right now this dumbness is keeping me going
    import numpy as np

    # numpy scalars -> Python scalars
    if isinstance(obj, (np.integer, np.int_, np.int64)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float_, np.float64)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)

    # numpy arrays -> lists
    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # Raise TypeError if anything isn't a scalar or list (should never be the case but who knows)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

class ARORAGeneticAlgImposedAuxinSynDegExport:
    def __init__(
        self,
        filename: str,
        out_dir: str = "param_est/ga_runs",
        run_name: str | None = None,
        plots_dirname: str = "plots",
        fitness_mode: str = "oscillation",
    ):
        self.ga_instance = None
        self.filename = filename  # existing json population dump
        self.population = []
        if fitness_mode == "oscillation_no_arr":
            self.param_names = IMPOSED_PIN_NO_ARR_PARAM_NAMES
        else:
            self.param_names = IMPOSED_PIN_ARR_ACTIVITY_PARAM_NAMES
        self.cleanup = True
        self.fitness_mode = fitness_mode  # "oscillation" | "vdb_ssd"

        out_dir = Path(out_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        if run_name is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = f"run_{ts}"
        self.run_name = run_name

        self.run_dir = out_dir / run_name
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.plots_dir = self.run_dir / plots_dirname
        self.plots_dir.mkdir(parents=True, exist_ok=True)

        # one-line-per-eval log (CSV)
        self.runs_csv_path = self.run_dir / "runs.csv"

        # text summary for best params + ranges
        self.best_txt_path = self.run_dir / "best_summary.txt"

        # store the gene space so we can report it later
        self.genespace = None

        # write CSV header once
        if not self.runs_csv_path.exists():
            with open(self.runs_csv_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["timestamp", "generation", "sol_idx", *self.param_names, "fitness", "finished", "tick", "exception"])

    def fitness_function(self, ga_instance, solution, solution_idx):
        print(f"-----------------------{solution_idx}---------------------------")
        print(f"Chromosome {solution_idx} : {solution}")
        chromosome = {}
        chromosome["sol_idx"] = solution_idx
        chromosome["generation"] = ga_instance.generations_completed # debugging
        params = pd.Series(solution, index=self.param_names)
        for param in self.param_names:
            chromosome[param] = params[param]
        if not self._check_constraints(params, chromosome):
            print("Invalid solution")
            cost = np.inf
        else:
            print(f"Running ARORA with params: {params}")
            fitness = self._run_ARORA(params, chromosome)
        chromosome["fitness"] = fitness
        self.population.append(chromosome)
        self._append_run_row(chromosome)
        print(f"Chromosome entry: {chromosome}")
        with open(self.filename, "w") as f:
            json.dump(self.population, f, indent=4, default=make_dumpable)
        return fitness

    def _append_run_row(self, chromosome: dict) -> None:
        """Append one row to runs.csv for every fitness eval."""
        row = [
            datetime.now().isoformat(timespec="seconds"),
            chromosome.get("generation"),
            chromosome.get("sol_idx"),
        ]
        for p in self.param_names:
            row.append(chromosome.get(p))
        row.extend([
            chromosome.get("fitness"),
            chromosome.get("finished"),
            chromosome.get("tick"),
            chromosome.get("exception"),
        ])

        with open(self.runs_csv_path, "a", newline="") as f:
            csv.writer(f).writerow(row)

    def _check_constraints(self, params, chromosome):
        # Check constraints here
        # ks = params['k_s']
        # kd = params['k_d']
        # Add more constraints as needed
        # if ks <= kd:
        #    print("k_s must be greater than k_d")
        #    return False
        return True

    def _cleanup_sim_files(self, chrom_idx: int) -> None:
        """Delete all intermediate files produced for a given chromosome index."""
        patterns = [
            f"param_est/ARORA_output_{chrom_idx}.csv",
            f"param_est/ARORA_output_{chrom_idx}.json",
            f"param_est/ARORA_output_{chrom_idx}_tick_*.json",
            f"param_est/ARORA_auxin_output_chrom_{chrom_idx}_tick_*.csv",
            f"param_est/ARORA_best_solution_tick_*.json" # added this to clean up the best_solution files too
        ]

        for pattern in patterns:
            for path in glob.glob(pattern):
                try:
                    os.remove(path)
                    print(f"Deleted {path}")
                except FileNotFoundError:
                    pass
                except OSError as e:
                    print(f"Warning: could not delete {path}: {e}")

    def _run_ARORA(self, params, chromosome):
        timestep = 1/9 # 6.6 minutes, this is less frequent than VDB outputs.
        vis = False
        cell_val_file = "src/sim/input/indep_syndeg_init_vals.json"
        v_file = "src/sim/input/default_vs.json"
        gparam_series = params
        geometry = "default"
        # Oscillation search uses 18 h (≈ 162 ticks) so each eval takes ~55 % of
        # the time a full 26-h run would take, while still allowing ≥2 cycles for
        # oscillations with periods up to ~8 h.  Full VDB comparison still needs
        # the full 26 h run to generate all required reference-aligned ticks.
        max_hours = 18 if self.fitness_mode == "oscillation" else 26

        simulation = GrowingSim(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            title=SCREEN_TITLE,
            timestep=timestep,
            vis=vis,
            cell_val_file=cell_val_file,
            v_file=v_file,
            gparam_series=gparam_series,
            geometry=geometry,
            output_file=f"param_est/ARORA_output_{chromosome['sol_idx']}",
            circ_mod=(
                CircModEnum.IMPOSED_PIN_NO_ARR
                if self.fitness_mode == "oscillation_no_arr"
                else CircModEnum.IMPOSED_PIN_ARR_ACTIVITY
            ),
            pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
            output_frequency=1,
            max_hours=max_hours,
        )

        try:
            simulation.run_sim()
            chromosome["finished"] = True
            chromosome["tick"] = simulation.get_tick()
            if self.fitness_mode == "vdb_ssd":
                ticks = range(simulation.get_tick())
                for tick in ticks:
                    self.create_arora_csv(f"param_est/ARORA_output_{chromosome['sol_idx']}_tick_{tick}.json", chromosome['sol_idx'], tick)
            fitness = self._calculate_fitness(simulation, chromosome)
        except Exception as e:
            print(e)
            chromosome["exception"] = str(e)
            chromosome["finished"] = False
            tick = simulation.get_tick()
            chromosome["tick"] = tick
            print("Fitness set to -infinity")
            fitness = -np.inf
        finally:
            if self.cleanup:
                self._cleanup_sim_files(chromosome["sol_idx"])
        return fitness

    def create_arora_csv(self, path: str, chromosome_idx: int,tick: int) -> None:
        """
        Convert a per-tick ARORA JSON file into a 2D auxin CSV image.

        New JSON structure (per file):
            [
            {
                "tick": <int>,
                "auxin": <float>,
                "location": [[x0, y0], [x1, y1], [x2, y2], [x3, y3]],
                ...
            },
            ...
            ]

        This function:
        - Loads all cell records for a single tick.
        - Computes the minimum y across all polygon corners (ymin).
        - If ymin < 0, shifts all y-coordinates up by |ymin|.
        - Rasterizes each cell polygon into a (1208, 141) array (aligning with dimensions of VDB sim space),
            filling it with the cell's auxin value.
        - Saves the resulting 2D auxin field as a CSV file named with the tick.
        """
        with open(path) as file:
            cells = json.load(file)  # list of cell dicts for a single tick

        # Initialize auxin image
        arr = np.zeros((1208, 141), dtype=float)

        # --- Compute ymin across all cells ---
        ymin = 0
        for cell in cells:
            loc = cell["location"]
            for corner in loc:
                y = corner[1]
                ymin = min(ymin, y)

        # --- Rasterize each cell into the auxin array ---
        for cell in cells:
            auxin = cell["auxin"]
            location = np.array(cell["location"], dtype=float)  # shape (4, 2), columns [x, y]
            for coord in location: 
                coord[0] -= 1 # to match where VDB data starts and ends

            if ymin < 0:
                # Shift y-coordinates up so that they are non-negative
                location[:, 1] += abs(ymin)

            # polygon() expects (r, c) = (y, x)
            rr, cc = polygon(location[:, 1], location[:, 0], arr.shape)
            arr[rr, cc] = auxin

        # --- Save to CSV ---
        out_path = f"param_est/ARORA_auxin_output_chrom_{chromosome_idx}_tick_{tick}.csv"
        np.savetxt(out_path, arr, delimiter=",", fmt="%f")


    def _calculate_fitness(self, simulation, chromosome):
        if self.fitness_mode == "vdb_ssd":
            return arora_vdb_ssd(chromosome["sol_idx"])
        elif self.fitness_mode == "oscillation":
            return oscillation_score_from_csv(simulation.output.filename_csv)
        else:
            raise ValueError(f"Unknown fitness_mode: {self.fitness_mode!r}")

    def make_paramspace_imposed_pin_arr_activity(self):
        # ks_aux: auxin synthesis rate [a.u./h].
        # Chosen so that A_ss = ks_aux * auxin_w / kd_aux spans ~1–200 a.u. over kd_aux range.
        ks_aux_range = np.geomspace(0.1, 10.0, 100).astype(float)

        # kd_aux: auxin degradation rate [1/h].
        # Half-life = ln(2)/kd_aux ≈ 1.4–13.9 h → “few hours to half-day” auxin turnover.
        kd_aux_range = np.geomspace(0.05, 0.5, 100).astype(float)

        # ARR turnover rates control dynamic transport activity through reg factor.
        ks_arr_range = np.geomspace(0.01, 1.0, 100).astype(float)
        kd_arr_range = np.geomspace(0.01, 1.0, 100).astype(float)

        # k1: ARR self-repression saturation constant.
        k1_range = np.geomspace(1.0, 200.0, 80).astype(float)

        # k5: k_al, AUX/LAX-mediated exchange factor [1/h].
        k5_range = np.geomspace(0.02, 1.0, 80).astype(float)

        # k6: k_pin, PIN-mediated export factor [1/h].
        k_pin_range = np.geomspace(0.02, 1.0, 80).astype(float)

        # tau: delay for ARR self-repression.
        # Minimum 5 ticks (33 min) to ensure a meaningful delay; maximum 36 ticks (4 h)
        # extended from 24 to allow longer delays that can support slower oscillations.
        tau_range = np.arange(5, 37, dtype=int)

        return [
            ks_aux_range,
            kd_aux_range,
            ks_arr_range,
            kd_arr_range,
            k1_range,
            k5_range,
            k_pin_range,
            tau_range,
        ]

    def make_paramspace_imposed_pin_no_arr(self):
        # Ranges match the ARR-coupled module for the shared parameters
        # so GA searches across both models are directly comparable.
        ks_aux_range = np.geomspace(0.1, 10.0, 100).astype(float)
        kd_aux_range = np.geomspace(0.05, 0.5, 100).astype(float)
        k5_range     = np.geomspace(0.02, 1.0, 80).astype(float)
        k_pin_range  = np.geomspace(0.02, 1.0, 80).astype(float)
        return [ks_aux_range, kd_aux_range, k5_range, k_pin_range]

    def run_genetic_alg(self):
        if self.fitness_mode == "oscillation_no_arr":
            genespace = self.make_paramspace_imposed_pin_no_arr()
        else:
            genespace = self.make_paramspace_imposed_pin_arr_activity()
        self.genespace = genespace

        # Hyperparameters tuned for oscillation search:
        #   - Higher mutation (20 %) explores the parameter space more broadly
        #     than the default 5 %, which was effectively no exploration.
        #   - Tournament selection balances exploitation and exploration.
        #   - keep_elitism=2 preserves the two best solutions each generation
        #     so good oscillatory solutions are not lost.
        #   - Smaller population (25) and fewer generations (10) keeps the
        #     total number of ~21 s evaluations around 275, finishing in ~2 h.
        #     The 18-hour simulation window (set in _run_ARORA) halves the cost
        #     per evaluation while still allowing ≥2 cycles for 1–8 h oscillations.
        #   - on_generation callback prints progress.
        if self.fitness_mode in ("oscillation", "oscillation_no_arr"):
            num_generations = 20
            num_parents_mating = 15
            sol_per_pop = 30
            mutation_percent_genes = 20
            parent_selection_type = "tournament"
            keep_elitism = 3
        else:  # vdb_ssd: original conservative settings
            num_generations = 20
            num_parents_mating = 25
            sol_per_pop = 50
            mutation_percent_genes = 5
            parent_selection_type = "sss"
            keep_elitism = 1

        fitness_function_label = self.fitness_mode
        save_best_solutions = False

        ga_parameters = {
            "num_generations": num_generations,
            "num_parents_mating": num_parents_mating,
            "fitness_func": self.fitness_function,
            "sol_per_pop": sol_per_pop,
            "num_genes": len(genespace),
            "gene_space": genespace,
            "mutation_percent_genes": mutation_percent_genes,
            "save_best_solutions": save_best_solutions,
            "parent_selection_type": parent_selection_type,
            "keep_elitism": keep_elitism,
            "on_generation": self.on_gen,
        }
        ga_parameters_for_saving = {
            "num_generations": num_generations,
            "num_parents_mating": num_parents_mating,
            "fitness_func": fitness_function_label,
            "sol_per_pop": sol_per_pop,
            "num_genes": len(genespace),
            "gene_space": genespace,
            "mutation_percent_genes": mutation_percent_genes,
            "save_best_solutions": save_best_solutions,
            "parent_selection_type": parent_selection_type,
            "keep_elitism": keep_elitism,
            "initialization_file": "indep_syndeg_init_vals.json",
            "hours_per_simulation": 27,
            "fitness_mode": self.fitness_mode,
        }
        self.population.append(ga_parameters_for_saving)
        self.ga_instance = pygad.GA(**ga_parameters)
        print(f"Running GA (fitness_mode={self.fitness_mode})!")
        self.ga_instance.run()

    def on_gen(self, ga_instance):
        print("Generation : ", ga_instance.generations_completed)
        print("Fitness of the best solution :", ga_instance.best_solution()[1])

    def _auxin_at_rc_from_tick_json(self, path: str, r: int, c: int) -> float:
        """
        Returns the auxin value at array location (r, c) for a single tick JSON.

        - Uses the same rasterization conventions as create_arora_csv():
          arr shape = (1208, 141), polygon uses (row=y, col=x), and x is shifted by -1.
        - If the point falls outside all polygons, returns 0.0 (background).
        """
        with open(path) as file:
            cells = json.load(file)

        arr = np.zeros((1208, 141), dtype=float)

        ymin = 0
        for cell in cells:
            for corner in cell["location"]:
                ymin = min(ymin, corner[1])

        for cell in cells:
            auxin = float(cell["auxin"])
            location = np.array(cell["location"], dtype=float)  # (4,2) [x,y]

            # match VDB alignment (same as create_arora_csv)
            location[:, 0] -= 1

            if ymin < 0:
                location[:, 1] += abs(ymin)

            rr, cc = polygon(location[:, 1], location[:, 0], arr.shape)
            arr[rr, cc] = auxin

        # guard against out-of-bounds
        if r < 0 or r >= arr.shape[0] or c < 0 or c >= arr.shape[1]:
            raise ValueError(f"(r,c)=({r},{c}) out of bounds for auxin array shape {arr.shape}")

        return float(arr[r, c])

    def _format_gene_space(self) -> str:
        """Strict, human-readable summary of gene_space."""
        if self.genespace is None:
            return "gene_space: <not set>\n"

        lines = []
        for name, space in zip(self.param_names, self.genespace):
            # constants (0, 1, etc.)
            if isinstance(space, (int, float, np.integer, np.floating)):
                lines.append(f"{name}: constant = {float(space)}")
                continue

            # list/ndarray of allowed values
            if isinstance(space, (list, tuple, np.ndarray)):
                arr = np.array(space, dtype=float)
                lines.append(
                    f"{name}: n={len(arr)} min={arr.min():.6g} max={arr.max():.6g} first={arr[0]:.6g} last={arr[-1]:.6g}"
                )
                continue

            # fallback
            lines.append(f"{name}: {repr(space)}")

        return "gene_space:\n  " + "\n  ".join(lines) + "\n"

    def _write_best_summary(self, solution: np.ndarray, solution_fitness: float, solution_idx: int) -> None:
        p = self.best_txt_path
        with open(p, "w") as f:
            f.write(f"run_dir: {self.run_dir}\n")
            f.write(f"best_solution_idx: {solution_idx}\n")
            f.write(f"best_fitness: {solution_fitness}\n\n")

            f.write("best_parameters:\n")
            for name, val in zip(self.param_names, solution):
                f.write(f"  {name}: {float(val)}\n")
            f.write("\n")
            f.write(self._format_gene_space())

        print(f"Saved: {p}")

    def analyze_results(self):
        print("Generating plot of best fitness per generation.")
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()

        self._write_best_summary(solution, solution_fitness, solution_idx)

        print("Parameters of the best solution : {solution}".format(solution=solution))
        print(
            "Fitness value of the best solution = {solution_fitness}".format(
                solution_fitness=solution_fitness
            )
        )
        print(
            "Index of the best solution : {solution_idx}".format(
                solution_idx=solution_idx
            )
        )

        # ---------------------------
        # Plot 1: Best fitness per generation
        # ---------------------------
        # pygad keeps this as a list of best fitness values (one per generation)
        best_fitness = self.ga_instance.best_solutions_fitness
        plot1_path = self.plots_dir / f"best_fitness_per_generation_{self.run_name}.png"

        if best_fitness is None or len(best_fitness) == 0:
            print("Warning: best_solutions_fitness empty; skipping plot.")
        else:
            gens = np.arange(1, len(best_fitness) + 1)
            plt.figure()
            plt.plot(gens, best_fitness)
            plt.xlabel("Generation")
            plt.ylabel("Best fitness")
            plt.title("Best fitness per generation")
            plt.tight_layout()
            plt.savefig(plot1_path, dpi=200)
            plt.close()
            print(f"Saved: {plot1_path}")

        # ---------------------------
        # Plot 2: Mean OZ XPP auxin + ARR over time (what the fitness function measures)
        # ---------------------------
        print("Re-running best solution (26 h) to generate detailed time-course plots.")

        timestep = 1 / 9  # hours per tick
        vis = False
        cell_val_file = "src/sim/input/indep_syndeg_init_vals.json"
        v_file = "src/sim/input/default_vs.json"
        geometry = "default"

        best_params = pd.Series(solution, index=self.param_names)
        out_base = "param_est/ARORA_best_solution"

        simulation = GrowingSim(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            title=SCREEN_TITLE,
            timestep=timestep,
            vis=vis,
            cell_val_file=cell_val_file,
            v_file=v_file,
            gparam_series=best_params,
            geometry=geometry,
            output_file=out_base,
            circ_mod=(
                CircModEnum.IMPOSED_PIN_NO_ARR
                if self.fitness_mode == "oscillation_no_arr"
                else CircModEnum.IMPOSED_PIN_ARR_ACTIVITY
            ),
            pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
            output_frequency=1,
        )
        simulation.run_sim()
        n_ticks = simulation.get_tick()

        # --- Read output CSV and compute OZ XPP statistics per tick ---
        out_csv = f"{out_base}.csv"
        try:
            df_out = pd.read_csv(out_csv)
            xpp_oz = df_out[
                df_out["dev_zone"].isin(["transition", "elongation"]) &
                (df_out["cell_type"] == "peri")
            ]
            agg_aux = (
                xpp_oz.groupby("tick")["auxin"]
                .agg(["mean", "std"])
                .sort_index()
            )
            agg_arr = (
                xpp_oz.groupby("tick")["arr"]
                .agg(["mean"])
                .sort_index()
            )
            times_csv = agg_aux.index.values * timestep
            has_csv_data = True
        except Exception as exc:
            print(f"Warning: could not read CSV for time-course plot: {exc}")
            has_csv_data = False

        # --- Plot: mean OZ XPP auxin, ±1 SD, and mean ARR ---
        plot2_path = self.plots_dir / f"oz_xpp_timecourse_{self.run_name}.png"
        if has_csv_data:
            fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

            # Auxin panel
            ax_aux = axes[0]
            ax_aux.plot(times_csv, agg_aux["mean"].values, label="Mean auxin")
            ax_aux.fill_between(
                times_csv,
                agg_aux["mean"].values - agg_aux["std"].fillna(0).values,
                agg_aux["mean"].values + agg_aux["std"].fillna(0).values,
                alpha=0.25,
                label="±1 SD",
            )
            ax_aux.set_ylabel("Auxin (a.u.)")
            param_summary = ", ".join(
                f"{k}={v:.4g}" for k, v in zip(self.param_names, solution)
            )
            ax_aux.set_title(
                f"OZ XPP cells — mean auxin and ARR over time (best solution)\n"
                f"{param_summary}"
            )
            ax_aux.legend(fontsize=8)

            # ARR panel
            ax_arr = axes[1]
            ax_arr.plot(times_csv, agg_arr["mean"].values, color="tab:orange", label="Mean ARR")
            ax_arr.set_ylabel("ARR (a.u.)")
            ax_arr.set_xlabel("Time (hours)")
            ax_arr.legend(fontsize=8)

            plt.tight_layout()
            plt.savefig(plot2_path, dpi=200)
            plt.close()
            print(f"Saved: {plot2_path}")

        # --- Also plot spatial CoV over time ---
        plot3_path = self.plots_dir / f"oz_xpp_cov_{self.run_name}.png"
        if has_csv_data:
            cov_ts = agg_aux["std"].fillna(0).values / (agg_aux["mean"].values + 1e-10)
            plt.figure(figsize=(10, 4))
            plt.plot(times_csv, cov_ts)
            plt.xlabel("Time (hours)")
            plt.ylabel("Spatial CoV (std/mean)")
            plt.title("Spatial coefficient of variation of auxin across OZ XPP cells")
            plt.tight_layout()
            plt.savefig(plot3_path, dpi=200)
            plt.close()
            print(f"Saved: {plot3_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run ARORA genetic algorithm.")
    parser.add_argument(
        "--mode",
        choices=["oscillation", "oscillation_no_arr", "vdb_ssd"],
        default="oscillation",
        help="Fitness mode: 'oscillation' targets temporal oscillation (ARR-coupled "
             "model); 'oscillation_no_arr' same but ARR clamped to 0 (VDB-aligned, "
             "4 params: ks_aux, kd_aux, k5, k6); 'vdb_ssd' minimises SSD against "
             "VDB reference images.",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional label for the run directory (default: run_<timestamp>).",
    )
    parser.add_argument(
        "--out-dir",
        default="param_est/ga_runs",
        help="Output directory for GA run artefacts.",
    )
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pop_file = f"param_est/ARORA_population_{args.mode}_{ts}.json"

    ga = ARORAGeneticAlgImposedAuxinSynDegExport(
        filename=pop_file,
        out_dir=args.out_dir,
        run_name=args.run_name,
        fitness_mode=args.mode,
    )
    ga.run_genetic_alg()
    ga.analyze_results()
