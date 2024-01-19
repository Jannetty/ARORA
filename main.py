import time
from src.plantem.sim.simulation import sim

"""
File to run simulation
"""

if __name__ == '__main__':
    timestep = 1
    root_midpoint_x = 71
    vis = True
    start_time = time.time()
    tick = sim.main(timestep, root_midpoint_x, vis, cell_val_file="src/plantem/sim/input/default_init_vals.csv", v_file="src/plantem/sim/input/default_vs.csv")
    end_time = time.time()
    # elapsed_time = end_time - start_time
    # print(f"Elapsed Time: {elapsed_time} seconds")
    # time_per_tick = elapsed_time/tick
    # total_time_estimate = time_per_tick * (1000*2592)
    # print(f"Total time estimate: {total_time_estimate} seconds")
    # print(f"Total time estimate: {total_time_estimate/60} minutes")
    # print(f"Total time estimate: {(total_time_estimate/60)/60} hours")
    # print(f"Total time estimate: {((total_time_estimate/60)/60)/24} days")