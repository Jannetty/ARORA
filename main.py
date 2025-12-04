import os
import platform
import argparse

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"

import time
import numpy as np
import pandas as pd
from src.sim.simulation import sim
from src.arora_enums import CircModEnum
from src.arora_enums import PinLocalizationRulesetEnum
import pyglet

"""
File to run simulation
"""
DEFAULT_PARAM_NAMES = ["k_s", "k_d", "k1", "k2", "k3", "k4", "k5", "k6", "tau"]
INDEP_PARAM_NAMES = [
    "ks_aux",
    "kd_aux",
    "ks_pinu",
    "kd_pinu",
    "kd_pinloc",
    "ks_auxlax",
    "kd_auxlax",
    "k1",
    "k2",
    "k3",
    "k4",
    "k5",
    "k6",
    "tau",
]


def make_default_param_series():
    ks_range = 0.01
    kd_range = 0.0001
    k1_range = 60
    k2_range = 64
    k3_range = 35
    k4_range = 61
    k5_range = 0.464545
    k6_range = 0.959596
    tau_range = 18
    param_vals = [
        ks_range,
        kd_range,
        k1_range,
        k2_range,
        k3_range,
        k4_range,
        k5_range,
        k6_range,
        tau_range,
    ]
    return pd.Series(param_vals, index=DEFAULT_PARAM_NAMES)

def make_aux_syn_deg_exp_param_series():
    ks_aux = 1
    kd_aux = .2
    ks_pinu = 0
    kd_pinu = 0
    kd_pinloc = 0
    ks_auxlax = 0
    kd_auxlax = 0
    k1_range = 0
    k2_range = 0
    k3_range = 0
    k4_range = 0
    kal_range = .02
    kpin_range = .02
    tau_range = 1
    param_vals = [
        ks_aux,
        kd_aux,
        ks_pinu,
        kd_pinu,
        kd_pinloc,
        ks_auxlax,
        kd_auxlax,
        k1_range,
        k2_range,
        k3_range,
        k4_range,
        kal_range,
        kpin_range,
        tau_range,
    ]
    return pd.Series(param_vals, index=INDEP_PARAM_NAMES)


def make_indep_param_series():
    ks_aux = 0.266778
    kd_aux = 0.0224495
    ks_pinu = 0.523434
    kd_pinu = 0.0176172
    kd_pinloc = 0.00191212
    ks_auxlax = 0.0040202
    kd_auxlax = 0.0257717
    k1_range = 60
    k2_range = 60
    k3_range = 33
    k4_range = 58
    k5_range = 1
    k6_range = 0.975758
    tau_range = 3
    param_vals = [
        ks_aux,
        kd_aux,
        ks_pinu,
        kd_pinu,
        kd_pinloc,
        ks_auxlax,
        kd_auxlax,
        k1_range,
        k2_range,
        k3_range,
        k4_range,
        k5_range,
        k6_range,
        tau_range,
    ]
    return pd.Series(param_vals, index=INDEP_PARAM_NAMES)


def get_simulation_config(circ_mod: CircModEnum):
    if circ_mod == CircModEnum.UNIVERSAL_SYN_DEG:
        return {
            "cell_val_file": "src/sim/input/default_init_vals_higher_auxinw_in_shootward_vasc.json",
            "v_file": "src/sim/input/default_vs.json",
            "gparam_series": make_default_param_series(),
        }
    elif CircModEnum.INDEP_SYN_DEG:
        return {
            "cell_val_file": "src/sim/input/indep_syndeg_init_vals.json",
            "v_file": "src/sim/input/default_vs.json",
            "gparam_series": make_indep_param_series(),
        }
    elif circ_mod == CircModEnum.AUX_SYN_DEG_ONLY:
        return {
            "cell_val_file": "src/sim/input/aux_syndegonly_init_vals.json",
            "v_file": "src/sim/input/default_vs.json",
            "gparam_series": make_default_param_series(),
        }
    elif circ_mod == CircModEnum.AUX_SYN_DEG_EXP:
        return {
            "cell_val_file": "src/sim/input/aux_syndegonly_init_vals.json",
            "v_file": "src/sim/input/default_vs.json",
            "gparam_series": make_aux_syn_deg_exp_param_series(),
        }
    else:
        raise ValueError(f"Unsupported circ_mod: {circ_mod}")


def get_circ_mod_enum(circ_mod_str: str):
    if circ_mod_str == "universal_syndeg" or circ_mod_str == "1":
        return CircModEnum.UNIVERSAL_SYN_DEG
    elif circ_mod_str == "indep_syndeg" or circ_mod_str == "2":
        return CircModEnum.INDEP_SYN_DEG
    elif circ_mod_str == "aux_syndegonly" or circ_mod_str == "3":
        return CircModEnum.AUX_SYN_DEG_ONLY
    elif circ_mod_str == "aux_syndegtrans" or circ_mod_str == "4":
        return CircModEnum.AUX_SYN_DEG_EXP
    else:
        raise ValueError(f"Unsupported circ_mod: {circ_mod}")


def get_pin_loc_rules_enum(pin_loc_rules_str: str):
    if pin_loc_rules_str == "simple_inheritance" or pin_loc_rules_str == "1":
        return PinLocalizationRulesetEnum.SIMPLE_INHERITANCE
    elif pin_loc_rules_str == "imposed" or pin_loc_rules_str == "2":
        return PinLocalizationRulesetEnum.IMPOSED


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ARORA Simulation")
    parser.add_argument(
        "--circ_mod",
        type=str,
        default="universal_syndeg",
        choices=["universal_syndeg", "1", "indep_syndeg", "2", "aux_syndegonly", "3", "aux_syndegtrans", "4"],
        help="Which circulation module to use",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="output",
        help="Base name for the output files (without extension)",
    )
    parser.add_argument(
        "--pin_loc_rules",
        type=str,
        default="simple_inheritance",
        choices=["simple_inheritance", "1", "imposed", "2"],
        help="Which PIN localization ruleset to use",
    )

    args = parser.parse_args()
    circ_mod = get_circ_mod_enum(args.circ_mod)
    timestep = .2
    vis = True
    start_time = time.time()
    config = get_simulation_config(circ_mod)
    sim.main(
        timestep,
        vis,
        pin_loc_rules=get_pin_loc_rules_enum(args.pin_loc_rules),
        circ_mod = circ_mod,
        cell_val_file=config["cell_val_file"],
        v_file=config["v_file"],
        gparam_series=config["gparam_series"],
        output_file=args.output_file,
    )
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")
