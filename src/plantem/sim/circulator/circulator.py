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
            self.delta_auxins[cell] += new_delta
        else:
            self.delta_auxins[cell] = delta

    def update(self) -> None:
        for cell in self.delta_auxins:
            old_aux = cell.get_circ_mod().get_auxin()
            new_aux = old_aux + self.delta_auxins[cell]
            cell.get_circ_mod().set_auxin(new_aux)
        self.delta_auxins = dict()

