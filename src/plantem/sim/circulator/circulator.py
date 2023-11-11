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
        # if cell.id == 60 or cell.id == 75:
        #     print(f"adding delta {delta} to cell {cell.get_id()}")
        if cell in self.delta_auxins:
            old_delta = self.delta_auxins[cell]
            new_delta = round(old_delta + delta,5)
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
            # if cell.id == 60 or cell.id == 75:
            #     print("------------------")
            #     print(f"IN CIRCULATOR updating cell {cell.get_id()}")
            #     print(f"old auxin {cell.get_circ_mod().get_auxin()}")
            #     print(f"delta auxin {self.delta_auxins[cell]}")
            #     print(f"new auxin {cell.get_circ_mod().get_auxin() + self.delta_auxins[cell]}")
            old_aux = cell.get_circ_mod().get_auxin()
            new_aux = round(old_aux + self.delta_auxins[cell],5)
            cell.get_circ_mod().set_auxin(new_aux)
        self.delta_auxins = dict()
        # THIS IS JUST FOR BUG HUNTING
        keys = [0,6,13,22,30,40,55,2,8,12,21,29,39,54,4,10,17,26,28,38,46,53,16,20,34,44,50,36,48,52,60,61,62,63,64,65,66,67,76,77,78,79,80,81,82,90,91,92,93,94,95,96,97,106,107,108,109,110,111,112,120,121,122,123,124,125,126,127,136,137,138,139,140,141,142,143,152,153,154,155,156,157,158,166,167,168,169,170,171,172,173,182,183,184,185,186,187,188,196,197,198,199,200,201,202,210,211,212,213,214,215,216,217,226,227,228,229,230,231,232,240,241,242,243,244,245,246,254,255,256,257,258,259,260,268,269,270,271,272,273,274,282,283,284,285,286,287,288]
        value = [1,7,14,23,31,41,56,3,9,15,24,32,42,57,5,11,18,27,33,43,47,58,19,25,35,45,51,37,49,59,75,74,73,72,71,70,69,68,89,88,87,86,85,84,83,105,104,103,102,101,100,99,98,119,118,117,116,115,114,113,135,134,133,132,131,130,129,128,151,150,149,148,147,146,145,144,165,164,163,162,161,160,159,181,180,179,178,177,176,175,174,195,194,193,192,191,190,189,209,208,207,206,205,204,203,225,224,223,222,221,220,219,218,239,238,237,236,235,234,233,253,252,251,250,249,248,247,267,266,265,264,263,262,261,281,280,279,278,277,276,275,295,294,293,292,291,290,289]
        equal_dict = dict(zip(keys, value))
        for id in keys:
            if self.sim.get_cell_by_ID(id).get_circ_mod().get_auxin() != self.sim.get_cell_by_ID(equal_dict[id]).get_circ_mod().get_auxin():
                print(f"cell {id} auxin {self.sim.get_cell_by_ID(id).get_circ_mod().get_auxin()}")
                print(f"cell {equal_dict[id]} auxin {self.sim.get_cell_by_ID(equal_dict[id]).get_circ_mod().get_auxin()}")
                raise ValueError("auxins not equal")