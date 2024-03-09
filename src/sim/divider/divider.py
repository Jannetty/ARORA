from typing import TYPE_CHECKING
from src.loc.vertex.vertex import Vertex
from src.agent.cell import Cell
from src.agent.default_geo_neighbor_helpers import NeighborHelpers

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim


class Divider:
    """
    Manages cell division within a simulation.

    This class is responsible for tracking cells that are ready to divide and performing
    the division process, creating new cells and updating the simulation cell list accordingly.

    Attributes
    ----------
    cells_to_divide : list[Cell]
        A list of cells that are ready to divide.
    sim : GrowingSim
        The simulation instance this Divider is part of.

    Parameters
    ----------
    sim : GrowingSim
        The simulation instance to which the Divider belongs.
    """

    cells_to_divide: list["Cell"] = []

    def __init__(self, sim: "GrowingSim"):
        """
        Initializes a new Divider instance.

        Parameters
        ----------
        sim : GrowingSim
            The simulation instance to which the Divider belongs.
        """
        self.sim = sim
        self.cells_to_divide = []

    def add_cell(self, cell: "Cell") -> None:
        """
        Adds a cell to the list of cells that are ready to divide.

        Parameters
        ----------
        cell : Cell
            The cell to be added to the division queue.
        """

        self.cells_to_divide.append(cell)

    def get_cells_to_divide(self) -> list["Cell"]:
        """
        Retrieves the list of cells that are ready to divide.

        Returns
        -------
        list[Cell]
            The list of cells queued for division.
        """
        return self.cells_to_divide

    def update(self) -> None:
        """
        Divides all queued cells, creating new cells, and updates the simulation cell list.

        This method iterates over cells that are ready to divide, divides them to create
        new cells, and then updates the simulation's cell list accordingly.
        """
        if len(self.cells_to_divide) != 0:
            meristematic_cells_to_divide = [
                cell for cell in self.cells_to_divide if cell.get_dev_zone() == "meristematic"
            ]
            for cell in meristematic_cells_to_divide:
                new_vs = self.get_new_vs(cell)
                # check if those vertices exist by iterating through all vs in all neighbor cells' qps
                left_v = self.check_neighbors_for_v_existence(cell, new_vs[0])
                right_v = self.check_neighbors_for_v_existence(cell, new_vs[1])

                # make new cell qp lists
                new_upper_vs: list["Vertex"] = [
                    cell.get_quad_perimeter().get_top_left(),
                    cell.get_quad_perimeter().get_top_right(),
                    right_v,
                    left_v,
                ]
                new_lower_vs: list["Vertex"] = [
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

    def get_new_vs(self, cell: "Cell") -> list["Vertex"]:
        """
        Calculates locations of new vertices needed to dividide a given cell.

        Parameters
        ----------
        cell : Cell
            The cell to be divided.

        Returns
        -------
        list[Vertex]
            A list containing two new vertices at necessary locations to divide 'cell'.
        """
        topleft = cell.get_quad_perimeter().get_top_left()
        topright = cell.get_quad_perimeter().get_top_right()
        bottomleft = cell.get_quad_perimeter().get_bottom_left()
        bottomright = cell.get_quad_perimeter().get_bottom_right()
        new_left = Vertex(topleft.get_x(), (topleft.get_y() + bottomleft.get_y()) / 2)
        new_right = Vertex(topright.get_x(), (topright.get_y() + bottomright.get_y()) / 2)
        return [new_left, new_right]

    def check_neighbors_for_v_existence(self, cell: "Cell", new_vertex: Vertex) -> Vertex:
        """
        Checks the neighboring cells for the existence of a given vertex.

        Parameters
        ----------
        cell : Cell
            The cell whose neighbors are to be checked.
        new_vertex : Vertex
            The vertex to check for in the neighbors.

        Returns
        -------
        Vertex
            The existing vertex from neighbors if found; otherwise, the input new_vertex.
        """
        for neighbor in cell.get_all_neighbors():
            neighbor_quad_p = neighbor.get_quad_perimeter()
            for neighbor_vertex in neighbor_quad_p.get_vs():
                if new_vertex.get_xy() == neighbor_vertex.get_xy():
                    return neighbor_vertex
        return new_vertex

    def update_neighbor_lists(
        self, new_top_cell: "Cell", new_bottom_cell: "Cell", cell: "Cell"
    ) -> None:
        """
        Updates neighbor lists of new cells and old cell neighbors to account
        for division.

        Parameters
        ----------
        new_top_cell : Cell
            The new cell forming in location of the top part of the divided cell.
        new_bottom_cell : Cell
            The new cell forming in location of the bottom part of the divided cell.
        cell : Cell
            The original cell that was divided.
        """
        new_top_cell.add_neighbor(new_bottom_cell)
        new_bottom_cell.add_neighbor(new_top_cell)
        for apical_neighbor in cell.get_a_neighbors():
            self.swap_neighbors(new_top_cell, apical_neighbor, cell)
        for basal_neighbor in cell.get_b_neighbors():
            self.swap_neighbors(new_bottom_cell, basal_neighbor, cell)
        self.set_one_side_neighbors(new_top_cell, new_bottom_cell, cell.get_l_neighbors(), cell)
        self.set_one_side_neighbors(new_top_cell, new_bottom_cell, cell.get_m_neighbors(), cell)

    def set_one_side_neighbors(
        self,
        new_top_cell: "Cell",
        new_bottom_cell: "Cell",
        neighbor_list: list["Cell"],
        cell: "Cell",
    ) -> None:
        """
        Assigns neighbors to one side of divided cells based on the old cell's neighbors.

        Parameters
        ----------
        new_top_cell : Cell
            The new cell forming the top part of the divided cell.
        new_bottom_cell : Cell
            The new cell forming the bottom part of the divided cell.
        neighbor_list : list[Cell]
            The list of neighbors (lateral or medial) of the original cell.
        cell : Cell
            The original cell that was divided.

        Notes
        -----
        This method is used for assigning lateral or medial neighbors to new cells.
        """
        if len(neighbor_list) == 0:
            return
        if len(neighbor_list) == 1:
            self.swap_neighbors(new_top_cell, neighbor_list[0], cell)
            self.swap_neighbors(new_bottom_cell, neighbor_list[0], cell)
            return

        for neighbor in neighbor_list:

            if (
                self.sim.geometry == "default"
                and neighbor.get_c_id() in NeighborHelpers.ROOTCAP_CELL_IDs
            ):
                NeighborHelpers.check_if_now_neighbors_with_new_root_cap_cell(
                    new_top_cell, self.sim
                )
                NeighborHelpers.check_if_now_neighbors_with_new_root_cap_cell(
                    new_bottom_cell, self.sim
                )
                neighbor.remove_neighbor(cell)

            elif (
                neighbor.get_quad_perimeter().get_top_left().get_y()
                == new_top_cell.get_quad_perimeter().get_top_left().get_y()
            ):
                self.swap_neighbors(new_top_cell, neighbor, cell)
            elif (
                neighbor.get_quad_perimeter().get_top_left().get_y()
                == new_bottom_cell.get_quad_perimeter().get_top_left().get_y()
            ):
                self.swap_neighbors(new_bottom_cell, neighbor, cell)

    def swap_neighbors(self, new_cell: "Cell", old_n: "Cell", old_cell: "Cell") -> None:
        """
        Replaces an old cell with a new cell in the neighbor list of an old neighbor.

        Parameters
        ----------
        new_cell : Cell
            The new cell to be added to the neighbor's list.
        old_n : Cell
            The neighbor cell whose neighbor list is to be updated.
        old_cell : Cell
            The old cell to be replaced by new_cell in the old_n's neighbor list
        """
        new_cell.add_neighbor(old_n)
        old_n.add_neighbor(new_cell)
        if old_n.check_if_neighbor(old_cell):
            old_n.remove_neighbor(old_cell)
