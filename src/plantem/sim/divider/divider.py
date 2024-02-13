from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.cell import Cell


class Divider:
    """
    Divider manages the division of cells in a simulation. Each time step cells
    that are ready to divide are added to the divider. At the end of the time
    step, the divider divides the cells and adds the new cells to the simulation.

    Attributes:
        cells_to_divide: A list of cells that are ready to divide.
        sim: The simulation that this divider is part of.
    """

    cells_to_divide = []

    def __init__(self, sim):
        """
        Constructs a new Divider instance.

        Args:
            sim: The simulation that this divider is part of.
        """
        self.sim = sim
        self.cells_to_divide = []

    def add_cell(self, cell) -> None:
        """
        Adds a cell to the list of cells that are ready to divide.

        Args:
            cell: The cell to add to the list of cells that are ready to divide.
        """
        self.cells_to_divide.append(cell)

    def get_cells_to_divide(self) -> None:
        """
        Returns the list of cells that are ready to divide.

        Returns:
            The list of cells that are ready to divide.
        """
        return self.cells_to_divide

    def update(self) -> None:
        """
        Divides all cells that are ready to divide and adds the new cells to the
        simulation.
        """
        if len(self.cells_to_divide) != 0:
            meristematic_cells_to_divide = [
                cell
                for cell in self.cells_to_divide
                if cell.get_dev_zone() == "meristematic"
            ]
            for cell in meristematic_cells_to_divide:
                # print(f"Dividing cell {cell.get_c_id()}")
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
                new_top_cell = Cell(
                    self.sim,
                    new_upper_vs,
                    cell.get_circ_mod().get_state(),
                    self.sim.get_next_cell_id(),
                )

                new_top_cell.set_growing(cell.get_growing())
                new_bottom_cell = Cell(
                    self.sim,
                    new_lower_vs,
                    cell.get_circ_mod().get_state(),
                    self.sim.get_next_cell_id(),
                )

                # TODO: reconsider why I am setting growing here as opposed to when the cells are made?
                new_bottom_cell.set_growing(cell.get_growing())
                # update neighbor lists
                self.update_neighbor_lists(new_top_cell, new_bottom_cell, cell)

                # add two new cells to sim.cell_list
                self.sim.get_cell_list().append(new_top_cell)
                self.sim.get_cell_list().append(new_bottom_cell)

                self.sim.get_cell_list().remove(cell)
            self.cells_to_divide = []

    def get_new_vs(self, cell) -> list:
        """
        Gets the new vertices for the new cells that will be created by dividing
        the input cell.

        Args:
            cell: The cell to divide.

        Returns:
            A list of the two new vertices for the new cells that will be created
            by dividing the input cell.
        """
        topleft = cell.get_quad_perimeter().get_top_left()
        topright = cell.get_quad_perimeter().get_top_right()
        bottomleft = cell.get_quad_perimeter().get_bottom_left()
        bottomright = cell.get_quad_perimeter().get_bottom_right()
        new_left = Vertex(topleft.get_x(), (topleft.get_y() + bottomleft.get_y()) / 2)
        new_right = Vertex(
            topright.get_x(), (topright.get_y() + bottomright.get_y()) / 2
        )
        return [new_left, new_right]

    def check_neighbors_for_v_existence(self, cell, new_vertex: Vertex):
        """
        Checks if a vertex exists in the neighbor cells of a cell.

        Args:
            cell: The cell whose neighbors to check.
            v: The vertex to check for existence.

        Returns:
            The vertex if it exists in a neighbor cell, otherwise the input vertex.
        """
        for neighbor in cell.get_all_neighbors():
            neighbor_quad_p = neighbor.get_quad_perimeter()
            for neighbor_vertex in neighbor_quad_p.get_vs():
                if new_vertex.get_xy() == neighbor_vertex.get_xy():
                    return neighbor_vertex
        return new_vertex

    def update_neighbor_lists(self, new_top_cell, new_bottom_cell, cell):
        """
        Updates the neighbor lists of the new cells to include the appropriate
        neighbors of the old cell.

        Args:
            new_top_cell: The new cell comprising the top half of the old cell.
            new_bottom_cell: The new cell comprising the bottom half of the old cell.
            cell: The old cell.
        """
        new_top_cell.add_neighbor(new_bottom_cell)
        new_bottom_cell.add_neighbor(new_top_cell)
        for apical_neighbor in cell.get_a_neighbors():
            self.swap_neighbors(new_top_cell, apical_neighbor, cell)
        for basal_neighbor in cell.get_b_neighbors():
            self.swap_neighbors(new_bottom_cell, basal_neighbor, cell)
        self.set_one_side_neighbors(
            new_top_cell, new_bottom_cell, cell.get_l_neighbors(), cell
        )
        self.set_one_side_neighbors(
            new_top_cell, new_bottom_cell, cell.get_m_neighbors(), cell
        )

    def set_one_side_neighbors(
        self, new_top_cell, new_bottom_cell, neighbor_list, cell
    ):
        """
        Sets new cells' neighbors to the neighbors of the old cell that each
        neighbors

        Args:
            new_top_cell: The new cell comprising the top half of the old cell.
            new_bottom_cell: The new cell comprising the bottom half of the old cell.
            neighbor_list: The list of lateral or medial neighbors of the old cell.
            cell: The old cell.
        """
        if len(neighbor_list) == 0:
            return
        if len(neighbor_list) == 1:
            print("Here 4 ------------------")
            self.swap_neighbors(new_top_cell, neighbor_list[0], cell)
            print("Here after swap neighbors ------------------")
            self.swap_neighbors(new_bottom_cell, neighbor_list[0], cell)
            return

        for neighbor in neighbor_list:
            if (
                neighbor.get_quad_perimeter().get_top_left().get_y()
                == new_top_cell.get_quad_perimeter().get_top_left().get_y()
            ):
                self.swap_neighbors(new_top_cell, neighbor, cell)
            elif (
                neighbor.get_quad_perimeter().get_top_left().get_y()
                == new_bottom_cell.get_quad_perimeter().get_top_left().get_y()
            ):
                self.swap_neighbors(new_bottom_cell, neighbor, cell)

    def swap_neighbors(self, new_cell, old_n, old_cell):
        """
        Swaps a neighbor from an old cell to a new cell

        Args:
            new_cell: The new cell to add the neighbor to.
            old_n: The neighbor to add to the new cell.
            old_cell: The old cell to remove the neighbor from.
        """
        print("Here 5 ------------------")
        print(
            f"new cell vertices {[vertex.get_xy() for vertex in new_cell.get_quad_perimeter().get_vs()]}"
        )
        print(
            f"new neighbor vertices {[vertex.get_xy() for vertex in old_n.get_quad_perimeter().get_vs()]}"
        )
        new_cell.add_neighbor(old_n)
        print("Here 6 ------------------")
        old_n.add_neighbor(new_cell)
        if old_n.check_if_neighbor(old_cell):
            old_n.remove_neighbor(old_cell)
