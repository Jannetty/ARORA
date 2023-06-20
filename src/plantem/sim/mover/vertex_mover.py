from src.plantem.agent.cell import GrowingCell

class VertexMover():

    # dictionary, key is cell, value is amount bottom vertices should move downward
    cells = {}

    def __init__(self) -> None:
        pass

    def add_delta_val(self, cell: GrowingCell, deltaX: float):
        if cell in self.cells:
            old_deltaX = self.cells.pop(cell)
            new_deltaX = old_deltaX + deltaX
            self.cells[cell] = new_deltaX
        else:
            self.cells[cell] = deltaX
        
        for basal_neighbor_cell in cell.get_b_neighbors():
            self.add_delta_val(basal_neighbor_cell, deltaX)

