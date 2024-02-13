from src.plantem.sim.simulation.sim import GrowingSim
from src.plantem.agent.cell import Cell


def auxin_peak_at_root_tip(sim: GrowingSim) -> float:
    non_root_tip_auxins = [cell.get_circ_mod().get_auxin() for cell in sim.cell_list if cell.get_dev_zone() != 'roottip']
    root_tip_auxins = non_root_tip_auxins = [cell.get_circ_mod().get_auxin() for cell in sim.cell_list if cell.get_dev_zone() == 'roottip']
    avg_non_root_tip_auxins = sum(non_root_tip_auxins)/len(non_root_tip_auxins)
    avg_root_tip_auxins = sim(root_tip_auxins)/len(root_tip_auxins)
    return avg_non_root_tip_auxins/avg_root_tip_auxins

def auxin_greater_in_larger_cells(sim: GrowingSim) -> float:
    meristematic_and_transition_cells = [cell for cell in sim.cell_list if (cell.get_dev_zone() == 'meristematic' or cell.get_dev_zone() == 'transition')]
    xpp_meri_and_trans_cells = [cell for cell in meristematic_and_transition_cells if (cell.get_quad_perimeter().get_midpointx() == 56.5 or cell.get_quad_perimeter().get_midpointx() == 85.5)]
    print(xpp_meri_and_trans_cells)