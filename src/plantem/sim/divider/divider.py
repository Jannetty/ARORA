from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.sim.circulator.circulator import 

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
            left_v = self.check_neighbors_for_v_existence(cell, new_vs[0])
            right_v = self.check_neighbors_for_v_existence(cell, new_vs[1])

            # divide circ components
            new_top_circ = None
            # make new cells using those vertices
            
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
    
    def check_neighbors_for_v_existence(self, cell, v):
        # returns neighbor v is one exists with same x,y, otherwise returns input v
        for neighbor in cell.get_all_neighbors():
            qp = neighbor.get_quad_perimeter()
            for nv in qp.get_vs():
                if v.get_xy() == nv.get_xy():
                    return nv 
        return v