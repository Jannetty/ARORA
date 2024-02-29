from param_est.cost_functions import correlation_coefficient, auxin_greater_in_larger_cells, auxin_peak_at_root_tip

# use PyGAD to estimate the parameters
import pygad
from pygad import GA

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "ARORA"

# define the cost function
def cost_func(params):
    # create a simulation object
    sim = GrowingSim(params)
    # run the simulation
    sim.run()
    # calculate the cost
    cost = auxin_peak_at_root_tip(sim) + auxin_greater_in_larger_cells(sim)
    return cost

# define the parameters
params = {
    'param1': [0, 1],
    'param2': [0, 1],
    'param3': [0, 1],
    'param4': [0, 1],
    'param5': [0, 1],
    'param6': [0, 1],
    'param7': [0, 1],
    'param8': [0, 1],
    'param9': [0, 1],
    'param10': [0, 1],
}

# create an instance of the GA class
ga = GA(num_generations=100, 
        num_parents_mating=5, 
        fitness_func=cost_func, 
        sol_per_pop=10, 
        num_genes=len(params))

# run the GA
ga.run()

# get the best solution
best_solution = ga.best_solution()
print(best_solution)