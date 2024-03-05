from typing import TYPE_CHECKING
from src.sim.util.math_helpers import round_to_sf

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim
    from src.agent.cell import Cell


class Circulator:
    """
    Circulator manages the delta auxins in a simulation. Each time step cells save their delta auxin to the circulator
    and delta auxins of that cell's neighbors are updated. At the end of the time step, the circulator updates the auxin

    Attributes:
        delta_auxins: A dictionary to store the delta auxins for each cell. Keys are cells, values are delta auxins.
        sim: The simulation that this circulator is part of.
    """

    def __init__(self, sim: "GrowingSim"):
        """
        Constructs a new Circulator instance.

        Args:
            sim: The simulation that this circulator is part of.
        """
        self.delta_auxins: dict["Cell", float] = dict()
        self.sim = sim

    def get_delta_auxins(self) -> dict["Cell", float]:
        """
        Returns the dictionary of delta auxins that the circulator is managing.
        Keys are cells, values are delta auxins.

        Returns:
            dict: The dictionary of delta auxins.
        """
        return self.delta_auxins

    def add_delta(self, cell: "Cell", delta: float) -> None:
        """
        Adds a delta auxin to the circulator for a given cell. If the cell is already in the circulator,
        the delta auxin is added to the existing delta auxin. If the cell is not in the circulator, the
        delta auxin is added to the circulator.

        Args:
            cell: The cell that the delta auxin is for.
            delta: The delta auxin to add.

        Returns:
            None
        """
        if cell in self.delta_auxins:
            if delta == float("inf") or delta == float("-inf"):
                print(f"cell {cell.get_c_id()} delta = {delta}")
            delta = round_to_sf(delta, 10)
            old_delta = round_to_sf(self.delta_auxins[cell], 10)
            new_delta = round_to_sf(old_delta + delta, 10)
            self.delta_auxins[cell] = new_delta
        else:
            if delta == float("inf") or delta == float("-inf"):
                print(f"cell {cell.get_c_id()} delta = {delta}")
            self.delta_auxins[cell] = round_to_sf(delta, 10)

    def update(self) -> None:
        """
        Updates the auxin of each cell in the circulator by adding the delta auxin to each cell's
        existing auxin.

        Returns:
            None
        """
        for cell in self.delta_auxins:
            old_aux = cell.get_circ_mod().get_auxin()
            new_aux = round_to_sf(old_aux + self.delta_auxins[cell], 6)
            if new_aux < 0:
                print(f"cell {cell.get_c_id()} new_aux = {new_aux}")
                raise ValueError(f"Negative Auxin")
            cell.get_circ_mod().set_auxin(new_aux)
        self.delta_auxins = dict()
