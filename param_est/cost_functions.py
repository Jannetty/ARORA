import numpy as np
from scipy.stats import spearmanr

from src.sim.simulation.sim import GrowingSim
from src.agent.cell import Cell


def auxin_peak_at_root_tip(sim: GrowingSim, chromosome: dict) -> float:
    """
    Returns the ratio of the average auxin concentration in non-root tip cells 
    to the average auxin concentration in root tip cells.

    Parameters
    ----------
    sim : GrowingSim
        The simulation object containing the cells.
    chromosome: Dict
        The dictionary being populated with information about this simulation's run

    Returns
    -------
    float
        The ratio of the average auxin concentration in root tip cells to non-root tip cells
    """
    non_root_tip_auxins = [cell.get_circ_mod().get_auxin() for cell in sim.cell_list if cell.get_dev_zone() != 'roottip']
    root_tip_auxins = [cell.get_circ_mod().get_auxin() for cell in sim.cell_list if cell.get_dev_zone() == 'roottip']
    avg_non_root_tip_auxins = sum(non_root_tip_auxins)/len(non_root_tip_auxins)
    avg_root_tip_auxins = sum(root_tip_auxins)/len(root_tip_auxins)
    return avg_root_tip_auxins/avg_non_root_tip_auxins # maximizing this

def auxin_greater_in_larger_cells(sim: GrowingSim, chromosome: dict) -> float:
    """
    Returns the correlation coefficient between cell size and auxin concentration in meristematic and transition cells.

    Parameters
    ----------
    sim : GrowingSim
        The simulation object containing the cells.
    chromosome: Dict
        The dictionary being populated with information about this simulation's run

    Returns
    -------
    float
        The correlation coefficient between cell size and auxin concentration in meristematic and transition cells.
    """
    meristematic_and_transition_cells = [cell for cell in sim.cell_list if (cell.get_dev_zone() == 'meristematic' or cell.get_dev_zone() == 'transition')]
    xpp_meri_and_trans_cells = [cell for cell in meristematic_and_transition_cells if (cell.get_cell_type() == 'peri')]
    # get correlation coefficient between cell size and auxin concentration in xpp_meri_and_trans_cells
    areas = [cell.get_quad_perimeter().get_area() for cell in xpp_meri_and_trans_cells]
    auxins = [cell.get_circ_mod().get_auxin() for cell in xpp_meri_and_trans_cells]
    spearman_results = spearmanr(areas, auxins)
    corr_coeff = spearman_results.statistic
    if corr_coeff < 0:
        print(f"Inverse correlation between cell size and auxin concentration in meristematic and transition cells. Fitness set to {abs(corr_coeff)}.")
        print(f"corr_coef = {corr_coeff}")
        print(f"Areas = {areas}")
        print(f"Auxins = {auxins}")
        chromosome["notes"] = f"Inverse correlation between cell size and auxin concentration in meristematic and transition cells. Fitness set to {abs(corr_coeff)}."
        return abs(corr_coeff) #we want there to be a strong correlation, we don't really care in what direction
    return abs(corr_coeff)