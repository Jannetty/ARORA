class Divider:
    cells_to_divide = []

    def __init__(self, sim):
        self.sim = sim

    def add_cell(self, cell) -> None:
        self.cells_to_divide.append(cell)
    
    def get_cells_to_divide(self) -> None:
        return self.cells_to_divide

    def update(self) -> None:
        pass