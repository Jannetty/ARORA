class Circulator:
    delta_auxins = None

    def __init__(self):
        self.delta_auxins = dict()

    def add_delta(self, cell, delta) -> None :
        if cell in self.delta_auxins:
            old_delta = self.delta_auxins[cell]
            new_delta = old_delta + delta
            self.delta_auxins[cell] = new_delta
        else:
            self.delta_auxins[cell] = delta