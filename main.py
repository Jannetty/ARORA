from src.plantem.sim.simulation import sim

"""
File to run simulation
"""

if __name__ == '__main__':
    timestep = 1
    root_midpoint_x = 400
    sim.main(timestep, root_midpoint_x, True, cell_val_file="src/plantem/sim/input/default_init_vals.csv", v_file="src/plantem/sim/input/default_vs.csv")