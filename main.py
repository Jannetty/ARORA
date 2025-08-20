import os
import platform
import argparse

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"

import time
import numpy as np
import pandas as pd
from src.sim.simulation import sim
import pyglet

"""
File to run simulation
"""
DEFAULT_PARAM_NAMES = ["k_s","k_d","k1","k2","k3","k4","k5","k6","tau"]
INDEP_PARAM_NAMES = ["ks_aux","kd_aux","ks_pinu","kd_pinu","kd_pinloc","ks_auxlax","kd_auxlax","k1","k2","k3","k4","k5","k6","tau"]

def make_default_param_series():
    ks_range = 0.0553636
    kd_range = 0.0278859
    k1_range = 60
    k2_range = 64
    k3_range = 35
    k4_range = 61
    k5_range = 0.464545
    k6_range = 0.959596
    tau_range = 18
    param_vals =  [ks_range, kd_range, k1_range, k2_range, k3_range, k4_range, k5_range, k6_range, tau_range]
    return pd.Series(param_vals, index=DEFAULT_PARAM_NAMES)

def make_indep_param_series():
    ks_aux = 0.266778
    kd_aux = 0.0224495
    ks_pinu = 0.523434
    kd_pinu = .0176172
    kd_pinloc = 0.00191212
    ks_auxlax = 0.0040202
    kd_auxlax = 0.0257717
    k1_range = 60
    k2_range = 60
    k3_range = 33
    k4_range = 58
    k5_range = 1
    k6_range = 0.975758
    tau_range =3
    param_vals = [ks_aux, kd_aux, ks_pinu, kd_pinu, kd_pinloc, ks_auxlax, kd_auxlax, k1_range, k2_range, k3_range, k4_range, k5_range, k6_range, tau_range]
    return pd.Series(param_vals, index=INDEP_PARAM_NAMES)

def get_simulation_config(circ_mod: str):
    if circ_mod == "universal_syndeg":
        return {
            "cell_val_file": "src/sim/input/default_init_vals_higher_auxinw_in_shootward_vasc.json",
            "v_file": "src/sim/input/default_vs.json",
            "gparam_series": make_default_param_series(),
        }
    elif circ_mod == "indep_syndeg":
        return {
            "cell_val_file": "src/sim/input/indep_syndeg_init_vals.json",
            "v_file": "src/sim/input/default_vs.json",
            "gparam_series": make_indep_param_series(),
        }
    elif circ_mod == "aux_syndegonly":
        return {
            "cell_val_file": "src/sim/input/aux_syndegonly_init_vals.json",
            "v_file": "src/sim/input/default_vs.json",
            "gparam_series": make_default_param_series(),
        }
    else:
        raise ValueError(f"Unsupported circ_mod: {circ_mod}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run ARORA Simulation")
    parser.add_argument("--circ_mod", type=str, default="universal_syndeg",
                        choices=["universal_syndeg", "indep_syndeg", "aux_syndegonly"],
                        help="Which circulation module to use")

    args = parser.parse_args()
    circ_mod = args.circ_mod
    timestep = 1
    vis = True
    start_time = time.time()
    config = get_simulation_config(circ_mod)
    sim.main(
        timestep,
        vis,
        cell_val_file=config["cell_val_file"],
        v_file=config["v_file"],
        gparam_series=config["gparam_series"]
    )
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")