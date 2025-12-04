import csv
import json
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim
    from src.agent.cell import Cell


class Output:
    """
    Handles the generation and management of simulation output data.

    This class is responsible for creating and writing simulation results to a CSV file
    and to per-tick JSON files, including detailed information about each cell.

    Attributes
    ----------
    sim : GrowingSim
        The simulation instance from which to gather output data.
    filename_csv : str
        The name of the CSV file to which output data will be written.
    filename_json : str
        The *base* name of the JSON file. A per-tick suffix will be added, e.g.
        'ARORA_output_tick_10.json'.

    Parameters
    ----------
    sim : GrowingSim
        The simulation instance associated with this output.
    filename_csv : str
        The filename for the output CSV file.
    filename_json : str
        The base filename for the output JSON files.
    """

    def __init__(self, sim: "GrowingSim", filename_csv: str, filename_json: str):
        self.sim = sim
        self.filename_csv = filename_csv
        self.filename_json = filename_json
        self.title_labels_written_to_output_file = False
        self.sim_and_cell_contents: list[str] | None = None
        self.circ_contents: list[str] | None = None

    def _json_filename_for_tick(self, tick: int) -> str:
        """
        Build a per-tick JSON filename from the base filename_json.

        Example:
            base: 'ARORA_output.json', tick: 10 ->
                'ARORA_output_tick_10.json'
        """
        base, ext = os.path.splitext(self.filename_json)
        if not ext:
            ext = ".json"
        return f"{base}_tick_{tick}{ext}"

    def output_cells(self) -> None:
        """
        Writes the current state of all cells to the CSV file and a per-tick JSON file.

        For each call:
          - Appends rows for all cells at the current tick to the CSV.
          - Writes all cell summaries for this tick to a separate JSON file whose name
            includes the current tick.
        """
        cell_list = list(self.sim.get_cell_list())
        if not cell_list:
            print("No Cells added to simulation. Cannot output simulation contents.")
            return

        # Initialize CSV header once
        if not self.title_labels_written_to_output_file:
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
            circ_contents = list(cell_list[0].get_circ_mod().get_state().keys())
            self.circ_contents = circ_contents

            with open(self.filename_csv, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(sim_and_cell_contents + circ_contents)

            self.title_labels_written_to_output_file = True

        # Build summaries for all cells at this tick
        tick = self.sim.get_tick()
        output: list[dict[str, Any]] = []

        for cell in cell_list:
            summary: dict[str, Any] = {}
            summary["tick"] = tick
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

        # --- CSV: append rows ---
        header = list(output[0].keys())
        with open(self.filename_csv, "a", newline="") as file:
            csv_writer = csv.DictWriter(file, fieldnames=header)
            csv_writer.writerows(output)

        # --- JSON: write one file per tick ---
        json_filename = self._json_filename_for_tick(tick)
        with open(json_filename, "w") as file:
            json.dump(output, file, indent=4)

    def get_circ_contents(self, summary: dict[str, Any], cell: "Cell") -> dict[str, Any]:
        """
        Populates the summary dictionary with circulation content information for a given cell.
        """
        return cell.get_circ_mod().get_state()

    def get_division_number(self, cell: "Cell") -> int:
        """
        Placeholder for division number retrieval.
        """
        raise NotImplementedError