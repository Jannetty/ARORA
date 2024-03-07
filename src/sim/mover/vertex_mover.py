from typing import TYPE_CHECKING
from src.agent.cell import Cell
from src.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.loc.vertex.vertex import Vertex
from src.agent.default_geo_neighbor_helpers import NeighborHelpers

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim


class VertexMover:
    """
    Moves vertices based on the growth of cells

    Attributes:
        cell_deltas: dictionary, key is cell, value is amount bottom vertices should move
        vertex_deltas: dictionary, key is vertex, value is total amount each vertex
                       should move total
        sim: The simulation object
    """

    def __init__(self, sim: "GrowingSim") -> None:
        self.cell_deltas: dict["Cell", float] = {}
        self.vertex_deltas: dict["Vertex", float] = {}
        self.sim = sim

    def add_cell_delta_val(self, cell: Cell, deltaX: float) -> None:
        """
        Adds a delta value for a cell to the VertexMover.
        Delta values represent the amount a cell has grown this time point.

        Args:
            cell (Cell): The cell for which the delta value is being added.
            deltaX (float): The delta value to be added.
        """
        if cell in self.cell_deltas:
            raise ValueError(
                f"Multiple delta vals added to VertexMover for cell {cell.get_c_id()}. VertexMover must be updated between cell updates."
            )
        else:
            self.cell_deltas[cell] = deltaX

    def get_cell_delta_val(self, cell: Cell) -> float:
        """
        Returns the delta value for a cell.

        Args:
            cell (Cell): The cell for which the delta value is being returned.

        Returns:
            float: The delta value for the cell.
        """
        return self.cell_deltas[cell]

    def get_vertex_delta_val(self, vertex: Vertex) -> float:
        """
        Returns the delta value for a vertex.

        Args:
            vertex (Vertex): The vertex for which the delta value is being returned.
        Returns:
            float: The delta value for the vertex.
        """
        return self.vertex_deltas[vertex]

    def update(self) -> None:
        """
        Moves the vertices based on the growth of the cells at this time point.
        """
        if self.cell_deltas:
            top_row = self.get_top_row()
            sorted_top_row = self.sort_top_row(top_row)
            self.propogate_deltas(sorted_top_row)
            max_delta = self.get_max_delta()
            self.execute_vertex_movement(max_delta)
            self.check_if_divide([cell for cell in self.cell_deltas.keys()])
            self.cell_deltas.clear()
            self.vertex_deltas.clear()
            if self.sim.geometry == "default":
                NeighborHelpers.fix_lrc_neighbors_after_growth(self.sim)

    def get_max_delta(self) -> float:
        """
        Returns the maximum delta value in the vertex_deltas dictionary.

        Returns:
            float: The maximum delta value.
        """
        max_delta = -float("inf")
        max_abs_delta = -float("inf")
        for delta in self.vertex_deltas.values():
            absolute_delta = abs(delta)
            if absolute_delta > max_abs_delta:
                max_abs_delta = absolute_delta
                max_delta = delta
        return max_delta

    def get_top_row(self) -> list:
        """
        Returns the top row of cells managed by this VertexMover.
        The top row is defined as the row of cells with the highest y locations.

        Returns:
            list: The top row of cells in the root tip.
        """
        top_ys = []
        for cell in self.cell_deltas:
            top_y = cell.get_quad_perimeter().get_top_left().get_y()
            top_ys.append(top_y)
        max_top_y = max(top_ys)
        top_row = []
        for cell in self.cell_deltas:
            top_y = cell.get_quad_perimeter().get_top_left().get_y()
            if top_y == max_top_y:
                top_row.append(cell)
        return top_row

    def sort_top_row(self, top_row: list["Cell"]) -> list["Cell"]:
        """
        Sorts the top row of cells by their x locations.

        Args:
            top_row (list): The top row of cells in the root tip.

        Returns:
            list: The sorted top row of cells.
        """
        left_xs = []
        for cell in top_row:
            left_xs.append(cell.get_quad_perimeter().get_top_left().get_x())
        return [cell for _, cell in sorted(zip(left_xs, top_row))]

    def propogate_deltas(self, top_row: list["Cell"]) -> None:
        """
        Propogates delta values to all basal neighbors of the top row of cells
        and adds the delta values to the bottom vertices of the cells.

        Args:
            top_row (list): The top row of cells in the root tip.
        """
        for cell in top_row:
            this_delta = self.cell_deltas[cell]
            self.add_cell_b_vertices_to_vertex_deltas(cell, this_delta)
            self.propogate_deltas_to_b_neighbors(cell, this_delta)

    def add_cell_b_vertices_to_vertex_deltas(self, cell: Cell, delta: float) -> None:
        """
        Adds the delta value to the bottom vertices of a cell to the vertex_deltas dictionary.

        Args:
            cell (Cell): The cell for which the delta value is being added.
            delta (float): The delta value to be added.
        """
        bottom_left_v = cell.get_quad_perimeter().get_bottom_left()
        bottom_right_v = cell.get_quad_perimeter().get_bottom_right()
        if bottom_left_v in self.vertex_deltas:
            pass
        else:
            self.vertex_deltas[bottom_left_v] = delta
        if bottom_right_v in self.vertex_deltas:
            pass
        else:
            self.vertex_deltas[bottom_right_v] = delta

    def propogate_deltas_to_b_neighbors(self, cell: Cell, delta: float) -> None:
        """
        Propogates the delta value to all basal neighbor cells.

        Args:
            cell (Cell): The cell for which the delta value is being propogated.
            delta (float): The delta value to be propogated.
        """
        stack = [(cell, delta)]
        while stack:
            cell, delta = stack.pop()
            for b_neighbor in cell.get_b_neighbors():
                if b_neighbor.get_growing():
                    if b_neighbor in self.cell_deltas:
                        neighbor_delta = self.cell_deltas[b_neighbor]
                    else:
                        neighbor_delta = 0
                    self.add_cell_b_vertices_to_vertex_deltas(b_neighbor, delta + neighbor_delta)
                    stack.append((b_neighbor, delta + neighbor_delta))

    def execute_vertex_movement(self, max_delta: float) -> None:
        """
        Moves the vertices based on the delta values in the vertex_deltas dictionary.

        Args:
            max_delta (int): The maximum delta value in the vertex_deltas dictionary.
        """
        for vertex in self.vertex_deltas:
            vertex.set_y(vertex.get_y() + self.vertex_deltas[vertex])
        # iterate through all nongrowing cells in root tip, move all basal vertices not yet moved
        moved_vs = list(self.vertex_deltas.keys())
        for cell in self.sim.get_cell_list():
            if not cell.get_growing() and cell.get_dev_zone() is "roottip":
                vertices = cell.get_quad_perimeter().get_vs()
                for vertex in vertices:
                    if vertex not in moved_vs:
                        vertex.set_y(vertex.get_y() + max_delta)
                        moved_vs.append(vertex)

    def check_if_divide(self, cells: list["Cell"]) -> None:
        """
        Checks if growth executed by this VertexMover this time point
        should make any cells divide.

        Args:
            cells (list): The list of cells this VertexMover affected this time point.
        """
        for cell in cells:
            if cell.get_quad_perimeter().get_area() >= (
                2 * cell.get_quad_perimeter().get_init_area()
            ):
                self.sim.get_divider().add_cell(cell)
