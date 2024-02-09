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
    sim.main(timestep, root_midpoint_x, vis, cell_val_file="default", v_file="default")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")