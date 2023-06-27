from src.plantem.loc.vertex.vertex import Vertex

class Divider:
    cells_to_divide = []

    def __init__(self, sim):
        self.sim = sim

    def add_cell(self, cell) -> None:
        self.cells_to_divide.append(cell)
    
    def get_cells_to_divide(self) -> None:
        return self.cells_to_divide

    def update(self) -> None:
        for cell in self.cells_to_divide:
            new_vs = self.get_new_vs(cell)
            # check if those vertices exist by iterating through all vs in all neighbor cells' qps
            # if not, make new vertices
            # make new cells using those vertices
            # divide and assign all circ_components
            # add two new cells to sim.cell_list
            self.sim.get_cell_list().remove(cell)

        self.cells_to_divide.clear()
    

    def get_new_vs(self, cell) -> list:
        topleft = cell.get_quad_perimeter().get_top_left()
        topright = cell.get_quad_perimeter().get_top_right()
        bottomleft = cell.get_quad_perimeter().get_bottom_left()
        bottomright = cell.get_quad_perimeter().get_bottom_right()
        new_left = Vertex(topleft.get_x(), (topleft.get_y()+bottomleft.get_y())/2)
        new_right = Vertex(topright.get_x(), (topright.get_y()+bottomright.get_y())/2)
        return [new_left, new_right]