

class Output():
    def __init__(self, sim, filename):
        self.sim = sim
        self.filename = filename

    def output_cells(self) -> None:
        # generates spreadsheet under name filename with contents of all cells
        # gets cell_list from sim
            # - for cell in self.sim.cell_list:
                # gets contents of each cell including
                    # - Auxin concentration
                    # - Location (x,y of corners retrieved from vertex class)
                    # - all circ contents (PINs in relation to left right instead of lateral/medial)
                    # - number of cell divisions
        pass
