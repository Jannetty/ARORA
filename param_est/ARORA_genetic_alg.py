import json
import os
import platform


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
)
from src.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "ARORA"

DEFAULT_PARAM_NAMES = ["k_s", "k_d", "k1", "k2", "k3", "k4", "k5", "k6", "tau"]
INDEP_SYN_DEG_PARAM_NAMES = [
    "ks_aux",
    "kd_aux",
    "ks_pinu",
    "kd_pinu",
    "kd_pinloc",
    "ks_auxlax",
    "kd_auxlax",
    "k1",
    "k2",
    "k3",
    "k4",
    "k5",
    "k6",
    "tau",
]
AUX_SYN_DEG_PARAM_NAMES = [
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


class ARORAGeneticAlg:
    def __init__(self, filename: str, circ_mod: str):
        self.ga_instance = None
        self.filename = filename
        self.population = []
        if circ_mod == "auxsyndeg_only":
            self.param_names = AUX_SYN_DEG_PARAM_NAMES
        elif circ_mod == "indep_syn_deg":
            self.param_names = INDEP_SYN_DEG_PARAM_NAMES
        else:
            raise ValueError("Invalid circ_mod")

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
            json.dump(self.population, f, indent=4)
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

    def _run_ARORA(self, params, chromosome):
        timestep = 1
        vis = False
        if self.param_names == AUX_SYN_DEG_PARAM_NAMES:
            cell_val_file = "src/sim/input/aux_syndegonly_init_vals.json"
        elif self.param_names == INDEP_SYN_DEG_PARAM_NAMES:
            cell_val_file = "src/sim/input/indep_syn_deg_init_vals.json"
        v_file = "src/sim/input/default_vs.json"
        gparam_series = params
        geometry = "default"
        simulation = GrowingSim(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            timestep,
            root_midpoint_x,
            vis,
            cell_val_file,
            v_file,
            gparam_series,
            geometry,
            f"param_est/ARORA_output_{chromosome['sol_idx']}",
        )
        simulation.setup()
        try:
            simulation.run_sim()
            chromosome["finished"] = True
            fitness = self._calculate_fitness(simulation, chromosome)
            try:
                os.remove(f"param_est/ARORA_output_{chromosome['sol_idx']}.csv")
                os.remove(f"param_est/ARORA_output_{chromosome['sol_idx']}.json")
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
            chromosome["exception"] = str(e)
            chromosome["finished"] = False
            tick = simulation.get_tick()
            chromosome["tick"] = tick
            print("Fitness set to -infinity")
            fitness = -np.inf
            try:
                os.remove(f"param_est/ARORA_output_{chromosome['sol_idx']}.csv")
                os.remove(f"param_est/ARORA_output_{chromosome['sol_idx']}.json")
            except Exception as e:
                print(e)
        return fitness

    # def _calculate_fitness_original(self, simulation, chromosome):
    #     # calculate fitness
    #     fitness = (
    #         100
    #         * auxin_greater_in_larger_cells_at_trans_elon_interface(
    #             simulation, chromosome
    #         )
    #     ) + avg_auxin_root_tip_greater_than_elsewhere(simulation, chromosome)
    #     chromosome["auxin_corr_with_cell_size"] = (
    #         100
    #         * auxin_greater_in_larger_cells_at_trans_elon_interface(
    #             simulation, chromosome
    #         )
    #     )
    #     chromosome["auxin_peak_at_root_tip"] = (
    #         avg_auxin_root_tip_greater_than_elsewhere(simulation, chromosome)
    #     )
    #     print(f"auxin_corr_with_cell_size: {chromosome['auxin_corr_with_cell_size']}")
    #     print(f"Auxin peak at root tip: {chromosome['auxin_peak_at_root_tip']}")
    #     print(f"Fitness: {fitness}")
    #     return fitness

    def _calculate_fitness(self, simulation, chromosome):
        # calculate fitness
        fitness = parity_of_mz_auxin_concentrations_with_VDB_data(
            simulation, chromosome
        ) + parity_of_auxin_c_for_xpp_boundary_cell_at_each_time_point(
            simulation, chromosome
        )
        return fitness

    def make_paramspace_ks_kd(self):
        ks_range = np.linspace(0.0001, 3, 1000).astype(float)
        kd_range = np.linspace(0.00001, 0.3, 1000).astype(float)
        k1_range = np.linspace(1, 1600, 1510).astype(int)
        k2_range = np.linspace(5, 1000, 510).astype(int)
        k3_range = np.linspace(1, 750, 660).astype(int)
        k4_range = np.linspace(5, 1000, 510).astype(int)
        k5_range = np.linspace(0.007, 10, 1000).astype(float)
        k6_range = np.linspace(0.02, 10, 1000).astype(float)
        tau_range = np.linspace(1, 240, 240).astype(int)
        return [
            ks_range,
            kd_range,
            k1_range,
            k2_range,
            k3_range,
            k4_range,
            k5_range,
            k6_range,
            tau_range,
        ]

    def make_paramspace_indep_syn_deg(self):
        ks_aux_range = np.linspace(0.001, 0.3, 100).astype(float)
        kd_aux_range = np.linspace(0.0001, 0.03, 100).astype(float)
        ks_pinu_range = np.linspace(0.001, 0.3, 100).astype(float)
        kd_pinu_range = np.linspace(0.0001, 0.03, 100).astype(float)
        kd_pinloc_range = np.linspace(0.0001, 0.03, 100).astype(float)
        ks_auxlax_range = np.linspace(0.001, 0.3, 100).astype(float)
        kd_auxlax_range = np.linspace(0.0001, 0.03, 100).astype(float)
        k1_range = np.linspace(10, 160, 151).astype(int)
        k2_range = np.linspace(50, 100, 51).astype(int)
        k3_range = np.linspace(10, 75, 66).astype(int)
        k4_range = np.linspace(50, 100, 51).astype(int)
        k5_range = np.linspace(0.07, 1, 100).astype(float)
        k6_range = np.linspace(0.2, 1, 100).astype(float)
        tau_range = np.linspace(1, 24, 24).astype(int)
        return [
            ks_aux_range,
            kd_aux_range,
            ks_pinu_range,
            kd_pinu_range,
            kd_pinloc_range,
            ks_auxlax_range,
            kd_auxlax_range,
            k1_range,
            k2_range,
            k3_range,
            k4_range,
            k5_range,
            k6_range,
            tau_range,
        ]
    
    def make_paramspace_aux_syn_deg(self):
        ks_aux_range = np.linspace(0.001, 0.3, 100).astype(float)
        kd_aux_range = np.linspace(0.0001, 0.03, 100).astype(float)
        k1_range = np.linspace(10, 160, 151).astype(int)
        k2_range = np.linspace(50, 100, 51).astype(int)
        k3_range = np.linspace(10, 75, 66).astype(int)
        k4_range = np.linspace(50, 100, 51).astype(int)
        k5_range = np.linspace(0.07, 1, 100).astype(float)
        k6_range = np.linspace(0.2, 1, 100).astype(float)
        tau_range = np.linspace(1, 24, 24).astype(int)
        return [
            ks_aux_range,
            kd_aux_range,
            k1_range,
            k2_range,
            k3_range,
            k4_range,
            k5_range,
            k6_range,
            tau_range,
        ]

    def run_genetic_alg(self):
        if self.param_names == AUX_SYN_DEG_PARAM_NAMES:
            genespace = self.make_paramspace_aux_syn_deg()
        elif self.param_names == INDEP_SYN_DEG_PARAM_NAMES:
            genespace = self.make_paramspace_indep_syn_deg()
        ga_parameters = {
            "num_generations":20,
            "num_parents_mating": 25,
            "fitness_func": self.fitness_function,
            "sol_per_pop": 50,
            "num_genes": len(genespace),
            "gene_space": genespace,
            "mutation_percent_genes": 5,
            "save_best_solutions": False,
            "parent_selection_type": "sss",
        }
        ga_parameters_for_saving = {
            "num_generations": 20,
            "num_parents_mating": 5,
            "fitness_func": "parity_of_mz_auxin_concentrations_with_VDB_data + parity_of_auxin_c_for_xpp_boundary_cell_at_each_time_point",
            "negative_corr_sets_fitness_to_neg_inf": False,
            "sol_per_pop": 20,
            "num_genes": len(genespace),
            "gene_space": "ks .001 to .3, kd .0001 to .03, k1 10 to 160, k2 50 to 100, k3 10 to 75, k4 50 to 100, k5 .07 to 1, k6 .2 to 1, tau 1 to 24",
            "mutation_percent_genes": 5,
            "save_best_solutions": False,
            "parent_selection_type": "sss",
            "initialization_file": "aux_syndegonly_init_vals.json",
            "hours_per_simulation": 27,
        }
        self.population.append(ga_parameters_for_saving)
        # with open(self.filename, 'w') as f:
        #    json.dump({'GA_parameters': ga_parameters_for_saving}, f, indent=4)
        # Initialize the GA with the parameters
        self.ga_instance = pygad.GA(**ga_parameters)

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
