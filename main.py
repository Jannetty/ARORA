import time
from src.plantem.sim.simulation import sim

"""
File to run simulation
"""

if __name__ == '__main__':
    timestep = 1
    root_midpoint_x = 71
    vis = False
    start_time = time.time()
    sim.main(timestep, root_midpoint_x, vis, cell_val_file="src/plantem/sim/input/default_init_vals.csv", v_file="src/plantem/sim/input/default_vs.csv")
    end_time = time.time()
    print(f"Elapsed Time: {end_time - start_time} seconds")
    print(f"Total time estimate: {(end_time - start_time)*1000} seconds")