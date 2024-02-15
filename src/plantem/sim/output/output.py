import csv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.plantem.sim import Sim
    from src.plantem.agent.cell import Cell


class Output:
    """
    Summary of simulation output
    """

    def __init__(self, sim: "Sim", filename: str):
        self.sim = sim
        self.filename = filename
        with open(self.filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "tick",
                    "cell",
                    "auxin",
                    "location",
                    "ARR",
                    "AUX/LAX",
                    "PIN_unlocalized",
                    "PIN_apical",
                    "PIN_basal",
                    "PIN_left",
                    "PIN_right",
                    "arr_hist",
                ]
            )

    def output_cells(self) -> None:
        """
        Generate output spreadsheet for simulation
        """
        # generates spreadsheet under name filename with contents of all cells
        # gets cell_list from sim
        # - for cell in self.sim.cell_list:
        # gets contents of each cell including
        # - Auxin concentration
        # - Location (x,y of corners retrieved from vertex class)
        # - all circ contents (PINs in relation to left right instead of lateral/medial)
        # - number of cell divisions
        output = []
        cell_list = list(self.sim.get_cell_list())
        for cell in cell_list:
            summary = {}
            summary["tick"] = self.sim.get_tick()
            summary["cell"] = cell.get_c_id()
            summary["auxin"] = self.get_auxin(cell)
            summary["location"] = self.get_location(cell)
            summary = self.get_circ_contents(summary, cell)
            # summary["num_divisions"] = self.get_division_number(cell)
            output.append(summary)

        # generate spreadsheet
        header = output[0].keys()
        with open(self.filename, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            # writer.writeheader()
            writer.writerows(output)

    # Helper functions
    def get_auxin(self, cell: "Cell") -> float:
        """
        Get auxin concentration for each cell
        """
        return cell.get_circ_mod().get_auxin()

    def get_location(self, cell: "Cell") -> list[float]:
        """
        Get location (x, y corners) for each cell
        """
        return cell.quad_perimeter.get_corners_for_disp()

    def get_circ_contents(self, summary: dict, cell: "Cell") -> dict:
        """
        Get circulation results for each cell
        """
        summary["ARR"] = cell.get_circ_mod().get_arr()
        summary["AUX/LAX"] = cell.get_circ_mod().get_al()
        summary["PIN_unlocalized"] = cell.get_circ_mod().get_pin()
        summary["PIN_apical"] = cell.get_circ_mod().get_apical_pin()
        summary["PIN_basal"] = cell.get_circ_mod().get_basal_pin()
        summary["PIN_left"] = cell.get_circ_mod().get_left_pin()
        summary["PIN_right"] = cell.get_circ_mod().get_right_pin()
        summary["arr_hist"] = cell.get_circ_mod().get_arr_hist()
        summary["auxin_w"] = cell.get_circ_mod().get_auxin_w()
        return summary

    def get_division_number(self, cell: "Cell") -> float:
        """
        Get number of cell divisions
        """
        pass
