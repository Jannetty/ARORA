import numpy as np

from src.sim.simulation.sim import GrowingSim
from src.agent.cell import Cell


def auxin_peak_at_root_tip(sim: GrowingSim) -> float:
    """
    Returns the ratio of the average auxin concentration in non-root tip cells 
    to the average auxin concentration in root tip cells.

    Parameters
    ----------
    sim : GrowingSim
        The simulation object containing the cells.

    Returns
    -------
    float
        The ratio of the average auxin concentration in non-root tip cells
    """
    non_root_tip_auxins = [cell.get_circ_mod().get_auxin() for cell in sim.cell_list if cell.get_dev_zone() != 'roottip']
    root_tip_auxins = [cell.get_circ_mod().get_auxin() for cell in sim.cell_list if cell.get_dev_zone() == 'roottip']
    avg_non_root_tip_auxins = sum(non_root_tip_auxins)/len(non_root_tip_auxins)
    avg_root_tip_auxins = sum(root_tip_auxins)/len(root_tip_auxins)
    return avg_non_root_tip_auxins/avg_root_tip_auxins

def auxin_greater_in_larger_cells(sim: GrowingSim) -> float:
    """
    Returns the correlation coefficient between cell size and auxin concentration in meristematic and transition cells.

    Parameters
    ----------
    sim : GrowingSim
        The simulation object containing the cells.

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
    corr_coeff = correlation_coefficient(areas, auxins)
    if corr_coeff < 0:
        print("Inverse correlation between cell size and auxin concentration in meristematic and transition cells. Cost set to infinity.")
        return np.inf
    return corr_coeff



def correlation_coefficient(list_x: list[float], list_y: list[float]) -> float:
    """
    Calculates the correlation coefficient between two lists.

    Parameters
    ----------
    list_x: list[float] 
        The first list.
    list_y: list[float] 
        The second list.

    Returns
    -------
    float
        The Pearson correlation coefficient.
    """
    if len(list_x) != len(list_y):
        raise ValueError("Lists must have the same length.")
    
    mean_x = np.mean(list_x)
    mean_y = np.mean(list_y)
    numerator = sum((list_x[i] - mean_x) * (list_y[i] - mean_y) for i in range(len(list_x)))
    denominator = np.sqrt(sum((list_x[i] - mean_x)**2 for i in range(len(list_x))) * sum((list_y[i] - mean_y)**2 for i in range(len(list_y))))
    
    if denominator == 0:
        raise ValueError("Denominator is zero, correlation coefficient is undefined.")
    
    return numerator / denominator