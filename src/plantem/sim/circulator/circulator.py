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

    def add_delta(self, cell, delta: float) -> None:
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
        # if cell.id == 30 or cell.id == 31:
        #     print(f"adding delta {delta} to cell {cell.get_id()}")
        if cell in self.delta_auxins:
            old_delta = self.delta_auxins[cell]
            new_delta = old_delta + delta
            self.delta_auxins[cell] = new_delta
        else:
            self.delta_auxins[cell] = delta

    def update(self) -> None:
        """
        Updates the auxin of each cell in the circulator by adding the delta auxin to each cell's
        existing auxin.

        Returns:
            None
        """
        for cell in self.delta_auxins:
            old_aux = cell.get_circ_mod().get_auxin()
            new_aux = old_aux + self.delta_auxins[cell]
            cell.get_circ_mod().set_auxin(new_aux)
        self.delta_auxins = dict()
        # THIS IS JUST FOR BUG HUNTING
        keys = [0,6,13,22,30,40,55,2,8,12,21,29,39,54,4,10,17,26,28,38,46,53,16,20,34,44,50,36,48,52]
        value = [1,7,14,23,31,41,56,3,9,15,24,32,42,57,5,11,18,27,33,43,47,58,19,25,35,45,51,37,49,59]
        equal_dict = dict(zip(keys, value))
        for id in keys:
            if self.sim.get_cell_by_ID(id).get_circ_mod().get_auxin() != self.sim.get_cell_by_ID(equal_dict[id]).get_circ_mod().get_auxin():
                print(f"cell {id} auxin {self.sim.get_cell_by_ID(id).get_circ_mod().get_auxin()}")
                print(f"cell {equal_dict[id]} auxin {self.sim.get_cell_by_ID(equal_dict[id]).get_circ_mod().get_auxin()}")
                raise ValueError("auxins not equal")