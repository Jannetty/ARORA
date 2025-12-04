import json
import os
import platform
import csv
import glob
from skimage.draw import polygon

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
    arora_vdb_ssd
)
from src.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "ARORA"

DEFAULT_PARAM_NAMES = ["k_s", "k_d", "k1", "k2", "k3", "k4", "k5", "k6", "tau"]

AUX_SYN_DEG_EXPORT_PARAM_NAMES = [
    "ks_aux",
    "kd_aux",
    "k1",
    "k2",
    "k3",
    "k4",
    "k5",
    "k6",
    "tau",
]

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
    def __init__(self, filename: str):
        self.ga_instance = None
        self.filename = filename
        self.population = []
        self.param_names = AUX_SYN_DEG_EXPORT_PARAM_NAMES

    def fitness_function(self, ga_instance, solution, solution_idx):
        print(f"-----------------------{solution_idx}---------------------------")
        print(f"Chromosome {solution_idx} : {solution}")
        chromosome = {}
        chromosome["sol_idx"] = solution_idx
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
        print(f"Chromosome entry: {chromosome}")
        with open(self.filename, "w") as f:
            json.dump(self.population, f, indent=4, default=make_dumpable)
        return fitness

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
        timestep = 1
        vis = False
        cell_val_file = "src/sim/input/aux_syndegonly_init_vals.json"
        v_file = "src/sim/input/default_vs.json"
        gparam_series = params
        geometry = "default"

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
            circ_mod=CircModEnum.AUX_SYN_DEG_EXP,
            pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        )

        try:
            simulation.run_sim()
            chromosome["finished"] = True
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
        - Rasterizes each cell polygon into a (1207, 142) array (aligning with dimensions of VDB sim space),
            filling it with the cell's auxin value.
        - Saves the resulting 2D auxin field as a CSV file named with the tick.
        """
        with open(path) as file:
            cells = json.load(file)  # list of cell dicts for a single tick

        # Initialize auxin image
        arr = np.zeros((1207, 142), dtype=float)

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
        fitness = 100 # :) dummy fitness function lol
        return fitness

    def make_paramspace_aux_syn_deg_trans(self):
        # ks_aux: auxin synthesis rate [a.u./h].
        # Chosen so that A_ss = ks_aux * auxin_w / kd_aux spans ~1–200 a.u. over kd_aux range.
        ks_aux_range = np.geomspace(0.1, 10.0, 100).astype(float)

        # kd_aux: auxin degradation rate [1/h].
        # Half-life = ln(2)/kd_aux ≈ 1.4–13.9 h → “few hours to half-day” auxin turnover.
        kd_aux_range = np.geomspace(0.05, 0.5, 100).astype(float)

        # --- Parameters not used by this circ mod ---

        # k1–k4: ARR / AUX-LAX / PIN regulatory couplings.
        k1_range = 0
        k2_range = 0
        k3_range = 0
        k4_range = 0

        # k5: k_al, AUX/LAX-mediated exchange factor [1/h].
        k5_range = 1

        # k6: k_pin, PIN-mediated export factor [1/h].
        k_pin_range = np.geomspace(0.05, 1.0, 60)

        # tau: time course of ARR's self- repression
        tau_range = 1

        return [
            ks_aux_range,
            kd_aux_range,
            k1_range,
            k2_range,
            k3_range,
            k4_range,
            k5_range,
            k_pin_range,
            tau_range,
        ]

    def run_genetic_alg(self):
        genespace = self.make_paramspace_aux_syn_deg_trans()
        # make GA hyperparameters
        num_generations = 20
        num_parents_mating = 25
        sol_per_pop = 50
        fitness_function = "descriptive string" # also dummy :)
        mutation_percent_genes = 5 # this is really low
        save_best_solutions = False
        parent_selection_type = "sss"
        ga_parameters = {
            "num_generations":num_generations,
            "num_parents_mating": num_parents_mating,
            "fitness_func": self.fitness_function,
            "sol_per_pop": sol_per_pop,
            "num_genes": len(genespace),
            "gene_space": genespace,
            "mutation_percent_genes": mutation_percent_genes,
            "save_best_solutions": save_best_solutions,
            "parent_selection_type": parent_selection_type,
        }
        ga_parameters_for_saving = {
            "num_generations": num_generations,
            "num_parents_mating": num_parents_mating,
            "fitness_func": fitness_function,
            "sol_per_pop":sol_per_pop,
            "num_genes": len(genespace),
            "gene_space": genespace,
            "mutation_percent_genes": mutation_percent_genes,
            "save_best_solutions": save_best_solutions,
            "parent_selection_type": parent_selection_type,
            "initialization_file": "aux_syndegonly_init_vals.json",
            "hours_per_simulation": 27,
        }
        self.population.append(ga_parameters_for_saving)
        self.ga_instance = pygad.GA(**ga_parameters)
        print("Running GA!")
        self.ga_instance.run()

    def on_gen(self, ga_instance):
        print("Generation : ", ga_instance.generations_completed)
        print("Fitness of the best solution :", ga_instance.best_solution()[1])

    def analyze_results(self):
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
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
