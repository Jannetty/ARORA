from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.cell import GrowingCell


class Divider:
    cells_to_divide = []

    def __init__(self, sim):
        self.sim = sim
        self.cells_to_divide = []

    def add_cell(self, cell) -> None:
        self.cells_to_divide.append(cell)

    def get_cells_to_divide(self) -> None:
        return self.cells_to_divide

    def update(self) -> None:
        for cell in self.cells_to_divide:
            if (cell.get_dev_zone() != 'meristematic'):
                print(f"Cell is in the {cell.get_dev_zone()} zone, not dividing")
                continue
            new_vs = self.get_new_vs(cell)
            # check if those vertices exist by iterating through all vs in all neighbor cells' qps
            left_v = self.check_neighbors_for_v_existence(cell, new_vs[0])
            right_v = self.check_neighbors_for_v_existence(cell, new_vs[1])

            # make new cell qp lists
            new_upper_vs = [
                cell.get_quad_perimeter().get_top_left(),
                cell.get_quad_perimeter().get_top_right(),
                right_v,
                left_v,
            ]
            new_lower_vs = [
                left_v,
                right_v,
                cell.get_quad_perimeter().get_bottom_right(),
                cell.get_quad_perimeter().get_bottom_left(),
            ]

            # make new cells using those vertices
            new_top_cell = GrowingCell(
                self.sim, new_upper_vs, cell.get_circ_mod().get_state(), self.sim.get_next_cell_id()
            )
            new_bottom_cell = GrowingCell(
                self.sim, new_lower_vs, cell.get_circ_mod().get_state(), self.sim.get_next_cell_id()
            )

            # update neighbor lists
            self.update_neighbor_lists(new_top_cell, new_bottom_cell, cell)

            # add two new cells to sim.cell_list
            self.sim.get_cell_list().append(new_top_cell)
            self.sim.get_cell_list().append(new_bottom_cell)

            self.sim.get_cell_list().remove(cell)
        self.cells_to_divide = []

    def get_new_vs(self, cell) -> list:
        topleft = cell.get_quad_perimeter().get_top_left()
        topright = cell.get_quad_perimeter().get_top_right()
        bottomleft = cell.get_quad_perimeter().get_bottom_left()
        bottomright = cell.get_quad_perimeter().get_bottom_right()
        new_left = Vertex(topleft.get_x(), (topleft.get_y() + bottomleft.get_y()) / 2)
        new_right = Vertex(topright.get_x(), (topright.get_y() + bottomright.get_y()) / 2)
        return [new_left, new_right]

    def check_neighbors_for_v_existence(self, cell, v: Vertex):
        # returns neighbor v is one exists with same x,y, otherwise returns input v
        for neighbor in cell.get_all_neighbors():
            qp = neighbor.get_quad_perimeter()
            for nv in qp.get_vs():
                if v.get_xy() == nv.get_xy():
                    return nv
        return v

    def update_neighbor_lists(self, new_top_cell, new_bottom_cell, cell):
        new_top_cell.add_neighbor(new_bottom_cell)
        new_bottom_cell.add_neighbor(new_top_cell)
        for an in cell.get_a_neighbors():
            self.swap_neighbors(new_top_cell, an, cell)
        for bn in cell.get_b_neighbors():
            self.swap_neighbors(new_bottom_cell, bn, cell)
        self.set_one_side_neighbors(new_top_cell, new_bottom_cell, cell.get_l_neighbors(), cell)
        self.set_one_side_neighbors(new_top_cell, new_bottom_cell, cell.get_m_neighbors(), cell)

    def set_one_side_neighbors(self, new_top_cell, new_bottom_cell, neighbor_list, cell):
        if len(neighbor_list) == 0:
            return
        elif len(neighbor_list) == 1:
            self.swap_neighbors(new_top_cell, neighbor_list[0], cell)
            self.swap_neighbors(new_bottom_cell, neighbor_list[0], cell)
            return
        else:
            for n in neighbor_list:
                if (
                    n.get_quad_perimeter().get_top_left().get_y()
                    == new_top_cell.get_quad_perimeter().get_top_left().get_y()
                ):
                    self.swap_neighbors(new_top_cell, n, cell)
                elif (
                    n.get_quad_perimeter().get_top_left().get_y()
                    == new_bottom_cell.get_quad_perimeter().get_top_left().get_y()
                ):
                    self.swap_neighbors(new_bottom_cell, n, cell)

    def swap_neighbors(self, new_cell, old_n, old_cell):
        new_cell.add_neighbor(old_n)
        old_n.remove_neighbor(old_cell)
        old_n.add_neighbor(new_cell)
