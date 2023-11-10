from src.plantem.sim.simulation import sim

"""
File to run simulation
"""

if __name__ == '__main__':
    timestep = 1
    root_midpoint_x = 71
    sim.main(timestep, root_midpoint_x, True, cell_val_file="src/plantem/sim/input/default_init_vals_root_tip.csv", v_file="src/plantem/sim/input/default_vs.csv")