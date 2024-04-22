import json
import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"
import numpy as np
import pandas as pd
# use PyGAD to estimate the parameters
import pygad
from pygad import GA
from param_est.cost_functions import auxin_greater_in_larger_cells, auxin_peak_at_root_tip
from src.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "ARORA"

PARAM_NAMES = ["k_s","k_d","k1","k2","k3","k4","k5","k6","tau"]

class ARORAGeneticAlg:
    def __init__(self, filename: str):
        self.ga_instance = None
        self.filename = filename
        self.population = []
    
    def fitness_function(self, ga_instance, solution, solution_idx):
        print(f"-----------------------{solution_idx}---------------------------")
        print(f"Chromosome {solution_idx} : {solution}")
        chromosome = {}
        chromosome['sol_idx'] = solution_idx
        params = pd.Series(solution, index=PARAM_NAMES)
        for param in PARAM_NAMES:
            chromosome[param] = params[param]
        if not self._check_constraints(params, chromosome):
            print("Invalid solution")
            cost = np.inf
        else:
            fitness = self._run_ARORA(params, chromosome)
        chromosome['fitness'] = fitness
        self.population.append(chromosome)
        print(f"Chromosome entry: {chromosome}")
        with open(self.filename, 'w') as f:
            json.dump(self.population, f, indent=4)
        return fitness
    
    def _check_constraints(self, params, chromosome):
        # Check constraints here
        #ks = params['k_s']
        #kd = params['k_d']
        # Add more constraints as needed
        #if ks <= kd:
        #    print("k_s must be greater than k_d")
        #    return False
        return True
    
    def _run_ARORA(self, params, chromosome):
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
            chromosome['finished'] = True
            fitness = self._calculate_fitness(simulation, chromosome)
        except Exception as e:
            print(e)
            chromosome['exception'] = str(e)
            chromosome['finished'] = False
            tick = simulation.get_tick()
            chromosome['tick'] = tick
            print("Fitness set to -infinity")
            fitness = - np.inf
        return fitness
    
    def _calculate_fitness(self, simulation, chromosome):
        # calculate fitness
        fitness = (100 * auxin_greater_in_larger_cells(simulation, chromosome)) + auxin_peak_at_root_tip(simulation, chromosome)
        chromosome['auxin_corr_with_cell_size'] = (100 * auxin_greater_in_larger_cells(simulation, chromosome))
        chromosome['auxin_peak_at_root_tip'] = auxin_peak_at_root_tip(simulation, chromosome)
        print(f"auxin_corr_with_cell_size: {chromosome['auxin_corr_with_cell_size']}")
        print(f"Auxin peak at root tip: {chromosome['auxin_peak_at_root_tip']}")
        print(f"Fitness: {fitness}")
        return fitness 

    def make_paramspace(self):
        ks_range = np.linspace(0.001, 0.3, 100).astype(float)
        kd_range = np.linspace(0.0001, 0.03, 100).astype(float)
        k1_range = np.round(np.linspace(10, 160, 100)).astype(int)
        k2_range = np.round(np.linspace(50, 100, 100)).astype(int)
        k3_range = np.round(np.linspace(10, 75, 100)).astype(int)
        k4_range = np.round(np.linspace(50, 100, 100)).astype(int)
        k5_range = np.linspace(0.07, 1, 100).astype(float)#np.linspace(0.07, 20, 100).astype(float) # kal
        k6_range = np.linspace(0.2, 1, 100).astype(float)#np.linspace(0.2, 20, 100).astype(float) # kpin
        tau_range = np.round(np.linspace(1, 24, 24)).astype(int)
        return [ks_range, kd_range, k1_range, k2_range, k3_range, k4_range, k5_range, k6_range, tau_range]

    def run_genetic_alg(self):
        genespace = self.make_paramspace()

        self.ga_instance = pygad.GA(num_generations=15,
                                    num_parents_mating=25,
                                    fitness_func=self.fitness_function,
                                    sol_per_pop=50,
                                    num_genes=len(genespace),
                                    gene_space=genespace,
                                    mutation_percent_genes=50,
                                    save_best_solutions=False,
                                    parent_selection_type="sss",
                                    )

        self.ga_instance.run()

    def on_gen(self, ga_instance):
        print("Generation : ", ga_instance.generations_completed)
        print("Fitness of the best solution :", ga_instance.best_solution()[1])

    def analyze_results(self):
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        print("Parameters of the best solution : {solution}".format(solution=solution))
        print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
        print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))
        # plot the fitness evolution
        self.ga_instance.plot_fitness(label='Fitness')