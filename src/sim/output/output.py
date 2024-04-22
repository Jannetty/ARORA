import csv
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim
    from src.agent.cell import Cell


class Output:
    """
    Handles the generation and management of simulation output data.

    This class is responsible for creating and writing simulation results to a CSV file,
    including detailed information about each cell.

    Attributes
    ----------
    sim : GrowingSim
        The simulation instance from which to gather output data.
    filename : str
        The name of the file to which output data will be written.

    Parameters
    ----------
    sim : GrowingSim
        The simulation instance associated with this output.
    filename : str
        The filename for the output CSV file.

    """

    def __init__(self, sim: "GrowingSim", filename: str):
        """
        Initializes the Output object with a simulation instance and output filename.

        Parameters
        ----------
        sim : GrowingSim
            The simulation instance associated with this output.
        filename : str
            The filename for the output CSV file.
        """
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
                    "apical_memlen",
                    "basal_memlen",
                    "left_memlen",
                    "right_memlen",
                    "dev_zone",
                    "cell_type",
                    "ARR",
                    "AUX/LAX",
                    "PIN_unlocalized",
                    "PIN_apical",
                    "PIN_basal",
                    "PIN_left",
                    "PIN_right",
                    "arr_hist",
                    "auxin_w",
                ]
            )

    def output_cells(self) -> None:
        """
        Writes the current state of all cells to the output file.

        This method gathers data from each cell within the simulation, including
        concentrations, locations, and PIN distributions, and writes this information
        to the specified output file.
        """
        output = []
        cell_list = list(self.sim.get_cell_list())
        for cell in cell_list:
            summary: dict[str, Any] = {}
            summary["tick"] = self.sim.get_tick()
            summary["cell"] = cell.get_c_id()
            summary["auxin"] = cell.get_circ_mod().get_auxin()
            summary["location"] = cell.quad_perimeter.get_corners_for_disp()
            summary["apical_memlen"] = cell.quad_perimeter.get_apical_memlen()
            summary["basal_memlen"] = cell.quad_perimeter.get_basal_memlen()
            summary["left_memlen"] = cell.quad_perimeter.get_left_memlen()
            summary["right_memlen"] = cell.quad_perimeter.get_right_memlen()
            summary["dev_zone"] = cell.get_dev_zone()
            summary["cell_type"] = cell.get_cell_type()
            summary = self.get_circ_contents(summary, cell)
            # summary["num_divisions"] = self.get_division_number(cell)
            output.append(summary)

        # generate spreadsheet
        header = output[0].keys()
        with open(self.filename, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            # writer.writeheader()
            writer.writerows(output)

    def get_circ_contents(self, summary: dict[str, Any], cell: "Cell") -> dict[str, Any]:
        """
        Populates the summary dictionary with circulation content information for a given cell.

        Parameters
        ----------
        summary : dict[str, Any]
            The summary dictionary to be populated with cell circulation data.
        cell : Cell
            The cell from which to retrieve circulation content information.

        Returns
        -------
        dict[str, Any]
            The updated summary dictionary containing circulation content information for the cell.
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

    def get_division_number(self, cell: "Cell") -> int:
        """
        Retrieves the number of divisions a cell has undergone.

        This method is a placeholder and is not implemented.

        Parameters
        ----------
        cell : Cell
            The cell from which to retrieve the division count.

        Returns
        -------
        int
            The number of divisions the cell has undergone.

        Raises
        ------
        NotImplementedError
            Indicates that the method is not yet implemented.
        """
        raise NotImplementedError
        return 0
