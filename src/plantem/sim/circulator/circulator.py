class Circulator:
    delta_auxins = None

    def __init__(self, sim):
        self.delta_auxins = dict()
        self.sim = sim

    def get_delta_auxins(self) -> dict:
        return self.delta_auxins

    def add_delta(self, cell, delta) -> None:
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
        for cell in self.delta_auxins:
            if cell.id == 0 or cell.id == 1:
                print(f"cell {cell.get_id()} aux before = {cell.get_circ_mod().get_auxin()}")
            old_aux = cell.get_circ_mod().get_auxin()
            new_aux = old_aux + self.delta_auxins[cell]
            cell.get_circ_mod().set_auxin(new_aux)
            if cell.id == 0 or cell.id == 1:
                print(f"cell {cell.get_id()} aux after = {cell.get_circ_mod().get_auxin()}")
        self.delta_auxins = dict()

