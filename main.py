from src.plantem.sim.simulation import sim

"""
File to run simulation
"""

if __name__ == '__main__':
    timestep = 1
    root_midpoint_x = 400
    sim.main(timestep, root_midpoint_x, True)