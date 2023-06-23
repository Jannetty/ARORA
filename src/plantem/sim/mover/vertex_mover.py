from src.plantem.agent.cell import GrowingCell
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.loc.vertex.vertex import Vertex

class VertexMover():

    def __init__(self) -> None:
        # dictionary, key is cell, value is amount bottom vertices should move downward
        self.cell_deltas = {}
        # dictionary, key is vertex, value is amount vertex should move total
        self.vertex_deltas = {}

    def add_cell_delta_val(self, cell: GrowingCell, deltaX: float) -> None:
        if cell in self.cell_deltas:
            raise ValueError (f"Multiple delta vals added to VertexMover for cell {cell}")
        else:
            self.cell_deltas[cell] = deltaX
    
    def get_cell_delta_val(self, cell : GrowingCell) -> float:
        return self.cell_deltas[cell]
    
    def get_vertex_delta_val(self, vertex : Vertex) -> float:
        return self.vertex_deltas[vertex]

    def update(self) -> None:
        top_row = self.get_top_row()
        sorted_top_row = self.sort_top_row(top_row)
        self.propogate_deltas(sorted_top_row)
        self.execute_vertex_movement()
        self.cell_deltas.clear()
        self.vertex_deltas.clear()

    def get_top_row(self) -> list: # NEED TO TEST
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
    
    def sort_top_row(self, top_row : list) -> list: # NEED TO TEST
        left_xs = []
        for cell in top_row:
            left_xs.append(cell.get_quad_perimeter().get_top_left().get_x())
        return [cell for _, cell in sorted(zip(left_xs, top_row))]


    def propogate_deltas(self, top_row : list) -> None:
        for cell in top_row:
            this_delta = self.cell_deltas[cell]
            self.add_cell_b_vertices_to_vertex_deltas(cell, this_delta)
            self.recursively_propogate_deltas_to_b_neighbors(cell, this_delta)

    def add_cell_b_vertices_to_vertex_deltas(self, cell : GrowingCell, delta : float) -> None:
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

    def recursively_propogate_deltas_to_b_neighbors(self, cell : GrowingCell, delta : float) -> None:
        for b_neighbor in cell.get_b_neighbors():
            if b_neighbor in self.cell_deltas:
                neighbor_delta = self.cell_deltas[b_neighbor]
            else:
                neighbor_delta = 0
            self.add_cell_b_vertices_to_vertex_deltas(b_neighbor, delta + neighbor_delta)
            self.recursively_propogate_deltas_to_b_neighbors(b_neighbor, delta + neighbor_delta)

    def execute_vertex_movement(self) -> None:
        for vertex in self.vertex_deltas:
            vertex.set_y(vertex.get_y() + self.vertex_deltas[vertex])