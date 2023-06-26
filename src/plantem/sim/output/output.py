import csv
from src.plantem.sim.simulation.sim import GrowingSim


class Output:
    """
    Summary of simulation output
    """

    def __init__(self, sim: GrowingSim, filename: str):
        self.sim = sim
        self.filename = filename

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
        cell_list = self.sim.cell_list
        for cell in cell_list:
            summary = {}
            summary["cell"] = cell
            summary["auxin"] = self.get_auxin(cell)
            summary["location"] = self.get_location(cell)
            summary = self.get_circ_contents(summary, cell)
            summary["num_divisions"] = self.get_division_number(cell)
            output.append(summary)

        # generate spreadsheet
        header = output[0].keys()
        with open(self.filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(output)

    # Helper functions
    def get_auxin(self, cell) -> float:
        """
        Get auxion concentration for each cell
        """
        return cell.circulator.get_auxin()

    def get_location(self, cell) -> list:
        """
        Get location (x, y corners) for each cell
        """
        return cell.quad_perimeter.get_corners_for_disp()

    def get_circ_contents(self, summary: dict, cell) -> dict:
        """
        Get circulation results for each cell
        """
        summary["ARR"] = cell.circulator.get_arr()
        summary["AUX/LAX"] = cell.circulator.get_aux_lax()
        summary["PIN_apical"] = cell.circulator.get_apical_pin()
        summary["PIN_basal"] = cell.circulator.get_basal_pin()
        summary["PIN_left"] = cell.circulator.get_left_pin()
        summary["PIN_right"] = cell.circulator.get_right_pin()
        return summary

    def get_division_number(self, cell) -> float:
        """
        Get number of cell divisions
        """
        pass
