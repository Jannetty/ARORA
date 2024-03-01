import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"
import numpy as np
import pandas as pd
# use PyGAD to estimate the parameters
import pygad
from pygad import GA
from param_est.cost_functions import correlation_coefficient, auxin_greater_in_larger_cells, auxin_peak_at_root_tip
from src.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "ARORA"

class ARORAGeneticAlg:
    def __init__(self, initial_parent_gen_file):
        self.parameters_df = pd.read_csv(initial_parent_gen_file)
        self.ga_instance = None

    def fitness_function(self, ga_instance, solution, solution_idx):
        params = self.parameters_df.iloc[solution_idx]
        cost = self._run_ARORA(params)
        fitness = -cost
        return fitness
    
    def _run_ARORA(self, params):
        timestep = 1
        root_midpoint_x = 71
        vis = False
        cell_val_file = "src/sim/input/default_init_vals.csv"
        v_file = "src/sim/input/default_vs.csv"
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
                            )
        simulation.setup()
        try:
            simulation.run_sim()
            cost = self._calculate_cost(simulation)
        except Exception as e:
            print("Cost set to infinity")
            cost = np.inf
        return cost
    
    def _calculate_cost(self, simulation):
        # calculate cost
        cost = auxin_greater_in_larger_cells(simulation) + auxin_peak_at_root_tip(simulation)
        return cost

    def make_paramspace(self):
        ks_range = np.linspace(0.001, 0.3, 10)
        kd_range = np.linspace(0.0001, 0.03, 10)
        k1_range = np.round(np.linspace(10, 160, 10)).astype(int)
        k2_range = np.round(np.linspace(50, 100, 10)).astype(int)
        k3_range = np.round(np.linspace(10, 75, 10)).astype(int)
        k4_range = np.round(np.linspace(50, 100, 10)).astype(int)
        k5_range = np.linspace(0.07, 20, 10) # kal
        k6_range = np.linspace(0.2, 20, 10) # kpin
        tau_range = np.round(np.linspace(60, 7200, 10)).astype(int)
        return [ks_range, kd_range, k1_range, k2_range, k3_range, k4_range, k5_range, k6_range, tau_range]

    def run_genetic_alg(self):
        genespace = self.make_paramspace()
        self.ga_instance = pygad.GA(num_generations=1,
                                    num_parents_mating=10,
                                    fitness_func=self.fitness_function,
                                    sol_per_pop=len(self.parameters_df),
                                    num_genes=len(self.parameters_df.columns),
                                    gene_space=genespace,
                                    mutation_percent_genes=50)

        self.ga_instance.run()

    def analyze_results(self):
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        print("Parameters of the best solution : {solution}".format(solution=solution))
        print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
        print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))
        # plot the fitness evolution
        pygad.plot_fitness(self.ga_instance)