from typing import TYPE_CHECKING
from src.sim.util.math_helpers import round_to_sf

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim
    from src.agent.cell import Cell


class Circulator:
    """
    Manages the delta auxins in a simulation to update cells' auxin levels.

    This class is responsible for tracking and updating the changes (delta) in auxin levels
    for each cell during a simulation. Cells report their auxin changes to the Circulator, which
    aggregates these changes and applies them at the end of each time step.

    Attributes
    ----------
    delta_auxins : dict[Cell, float]
        A dictionary to store the delta auxins for each cell, where keys are `Cell` instances
        and values are the delta auxins.
    sim : GrowingSim
        The simulation instance that this Circulator is a part of.

    Parameters
    ----------
    sim : GrowingSim
        The simulation instance to which this Circulator belongs.
    """

    def __init__(self, sim: "GrowingSim"):
        """
        Initializes a new Circulator instance for managing delta auxins within a simulation.

        Parameters
        ----------
        sim : GrowingSim
            The simulation instance to which this Circulator belongs.
        """
        self.delta_auxins: dict["Cell", float] = dict()
        self.sim = sim

    def get_delta_auxins(self) -> dict["Cell", float]:
        """
        Retrieve the current delta auxins managed by the Circulator.

        Returns
        -------
        dict[Cell, float]
            A dictionary of delta auxins, where keys are `Cell` instances and values
            are the delta auxins.
        """
        return self.delta_auxins

    def add_delta(self, cell: "Cell", delta: float) -> None:
        """
        Adds a delta auxin value for a specified cell.

        If the cell already exists in the Circulator, the new delta is added to the existing value.
        If the cell does not exist, it is added with the specified delta auxin value. Values are
        rounded to significant figures for precision management.

        Parameters
        ----------
        cell : Cell
            The cell for which the delta auxin is being reported.
        delta : float
            The delta auxin value to add.

        Notes
        -----
        Infinites are checked and logged, and values are rounded to 10 significant figures.
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
        Apply the accumulated delta auxins to each cell's current auxin level.

        This method iterates over all cells with recorded delta auxins, updates their
        auxin levels accordingly, and then resets the delta auxins for the next time step.
        """
        for cell in self.delta_auxins:
            old_aux = cell.get_circ_mod().get_auxin()
            new_aux = round_to_sf(old_aux + self.delta_auxins[cell], 6)
            cell.get_circ_mod().set_auxin(new_aux)
        self.delta_auxins = dict()
