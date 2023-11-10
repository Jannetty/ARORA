class Circulator:
    """
    Circulator manages the delta auxins in a simulation. Each time step cells save their delta auxin to the circulator
    and delta auxins of that cell's neighbors are updated. At the end of the time step, the circulator updates the auxin

    Attributes:
        delta_auxins: A dictionary to store the delta auxins for each cell. Keys are cells, values are delta auxins.
        sim: The simulation that this circulator is part of.
    """
    delta_auxins = None

    def __init__(self, sim):
        """
        Constructs a new Circulator instance.

        Args:
            sim: The simulation that this circulator is part of.
        """
        self.delta_auxins = dict()
        self.sim = sim

    def get_delta_auxins(self) -> dict:
        """
        Returns the dictionary of delta auxins that the circulator is managing. 
        Keys are cells, values are delta auxins.

        Returns:
            dict: The dictionary of delta auxins.
        """
        return self.delta_auxins

    def add_delta(self, cell, delta) -> None:
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
            old_delta = self.delta_auxins[cell]
            new_delta = old_delta + delta
            self.delta_auxins[cell] = new_delta
            if cell.id == 0 or cell.id == 1:
                print (f"cell {cell.get_id()} delta to be added is = {delta}, old delta = {old_delta}, new delta = {new_delta}")
        else:
            if cell.id == 0 or cell.id == 1 or cell.id == 2 or cell.id == 3 or cell.id == 6 or cell.id == 7:
                print (f"cell {cell.get_id()} being added to circulator for first time with delta = {delta}")
            self.delta_auxins[cell] = delta

    def update(self) -> None:
        """
        Updates the auxin of each cell in the circulator by adding the delta auxin to each cell's
        existing auxin.

        Returns:
            None
        """
        for cell in self.delta_auxins:
            if cell.id == 0 or cell.id == 1:
                print(f"cell {cell.get_id()} aux before = {cell.get_circ_mod().get_auxin()}")
            old_aux = cell.get_circ_mod().get_auxin()
            new_aux = old_aux + self.delta_auxins[cell]
            cell.get_circ_mod().set_auxin(new_aux)
            if cell.id == 0 or cell.id == 1:
                print(f"cell {cell.get_id()} aux after = {cell.get_circ_mod().get_auxin()}")
        self.delta_auxins = dict()

