

class Output():
    def __init__(self, sim, filename):
        self.sim = sim
        self.filename = filename

    def output_cells(self) -> None:
        # gets self.cell_list from sim
        # gets contents of each cell including
            # - Auxin concentration
            # - Location (x,y of corners retrieved from vertex class)
            # - all circ contents (PINA, PINB, PINL, PINM)
