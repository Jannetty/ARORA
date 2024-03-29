import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"

import time
import numpy as np
import pandas as pd
from src.sim.simulation import sim

"""
File to run simulation
"""
PARAM_NAMES = ["k_s","k_d","k1","k2","k3","k4","k5","k6","tau"]

def make_param_series():
    ks_range = .3 #np.linspace(0.001, 0.3, 100).astype(float)
    kd_range = .003 #np.linspace(0.0001, 0.03, 100).astype(float)
    k1_range = 10 #np.round(np.linspace(10, 160, 100)).astype(int)
    k2_range = 50 #np.round(np.linspace(50, 100, 100)).astype(int)
    k3_range = 10 #np.round(np.linspace(10, 75, 100)).astype(int)
    k4_range = 50 #np.round(np.linspace(50, 100, 100)).astype(int)
    k5_range = .08 #np.linspace(0.07, 1, 100).astype(float)#np.linspace(0.07, 20, 100).astype(float) # kal
    k6_range = .3 #np.linspace(0.2, 1, 100).astype(float)#np.linspace(0.2, 20, 100).astype(float) # kpin
    tau_range = 60 #np.round(np.linspace(60, 7200, 100)).astype(int)
    param_vals =  [ks_range, kd_range, k1_range, k2_range, k3_range, k4_range, k5_range, k6_range, tau_range]
    return pd.Series(param_vals, index=PARAM_NAMES)

if __name__ == '__main__':
    timestep = 1
    root_midpoint_x = 71
    vis = True
    start_time = time.time()
    sim.main(timestep, root_midpoint_x, vis, cell_val_file="default", v_file="default", gparam_series=make_param_series())
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")