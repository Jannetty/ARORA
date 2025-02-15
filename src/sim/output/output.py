import csv
import json
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
    filename_csv : str
        The name of the CSV file to which output data will be written.
    filename_json : str
        The name of the JSON file to which output data will be written.

    Parameters
    ----------
    sim : GrowingSim
        The simulation instance associated with this output.
    filename_csv : str
        The filename for the output CSV file.
    filename_json : str
        The filename for the output JSON file.
    """

    def __init__(self, sim: "GrowingSim", filename_csv: str, filename_json: str):
        """
        Initializes the Output object with a simulation instance and output filenames.

        Parameters
        ----------
        sim : GrowingSim
            The simulation instance associated with this output.
        filename_csv : str
            The filename for the output CSV file.
        filename_json : str
            The filename for the output JSON file.
        """
        self.sim = sim
        self.filename_csv = filename_csv
        self.filename_json = filename_json
        self.title_labels_written_to_output_file = False

    def output_cells(self) -> None:
        """
        Writes the current state of all cells to the output files.

        This method gathers data from each cell within the simulation, including
        concentrations, locations, and PIN distributions, and writes this information
        to the specified output files.
        """
        if self.title_labels_written_to_output_file == False:
            if len(self.sim.get_cell_list()) <= 0:
                print("No Cells added to simulation. Cannot output simulation contents.")
                return
            sim_and_cell_contents = [
                "tick",
                "cell",
                "location",
                "apical_memlen",
                "basal_memlen",
                "left_memlen",
                "right_memlen",
                "dev_zone",
                "cell_type",
            ]
            self.sim_and_cell_contents = sim_and_cell_contents
            circ_contents = list(self.sim.get_cell_list()[0].get_circ_mod().get_state().keys())
            self.circ_contents = circ_contents
            with open(self.filename_csv, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(sim_and_cell_contents + circ_contents)
            self.title_labels_written_to_output_file = True
        output = []
        cell_list = list(self.sim.get_cell_list())
        for cell in cell_list:
            summary: dict[str, Any] = {}
            summary["tick"] = self.sim.get_tick()
            summary["cell"] = cell.get_c_id()
            summary["location"] = cell.quad_perimeter.get_corners_for_disp()
            summary["apical_memlen"] = cell.quad_perimeter.get_apical_memlen()
            summary["basal_memlen"] = cell.quad_perimeter.get_basal_memlen()
            summary["left_memlen"] = cell.quad_perimeter.get_left_memlen()
            summary["right_memlen"] = cell.quad_perimeter.get_right_memlen()
            summary["dev_zone"] = cell.get_dev_zone()
            summary["cell_type"] = cell.get_cell_type()
            summary.update(self.get_circ_contents(summary, cell))
            output.append(summary)

        # Generate CSV
        header = output[0].keys()
        with open(self.filename_csv, "a", newline="") as file:
            csv_writer = csv.DictWriter(file, fieldnames=header)
            csv_writer.writerows(output)

        # Generate JSON
        with open(self.filename_json, "a") as file:
            json.dump(output, file, indent=4)

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
        return cell.get_circ_mod().get_state()

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
