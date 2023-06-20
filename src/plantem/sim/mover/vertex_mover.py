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
        self.propogate_deltas()
        self.execute_vertex_movement()
        self.cell_deltas.clear()
        self.vertex_deltas.clear()

    def propogate_deltas(self) -> None:
        for cell in self.cell_deltas:
            this_delta = self.cell_deltas[cell]
            self.add_cell_b_vertices_to_vertex_deltas(cell, this_delta)
            self.recursively_propogate_deltas_to_b_neighbors(cell, this_delta)

    def add_cell_b_vertices_to_vertex_deltas(self, cell : GrowingCell, delta : float) -> None:
        bottom_left_v = cell.get_quad_perimeter().get_bottom_left()
        bottom_right_v = cell.get_quad_perimeter().get_bottom_right()
        if bottom_left_v in self.vertex_deltas:
            self.vertex_deltas[bottom_left_v] = self.vertex_deltas[bottom_left_v] + delta
        else:
            self.vertex_deltas[bottom_left_v] = delta
        if bottom_right_v in self.vertex_deltas:
            self.vertex_deltas[bottom_right_v] = self.vertex_deltas[bottom_right_v] + delta
        else:
            self.vertex_deltas[bottom_right_v] = delta

    def recursively_propogate_deltas_to_b_neighbors(self, cell : GrowingCell, delta : float) -> None:
        for b_neighbor in cell.get_b_neighbors():
            self.add_cell_b_vertices_to_vertex_deltas(b_neighbor, delta)
            self.recursively_propogate_deltas_to_b_neighbors(b_neighbor, delta)

    def execute_vertex_movement(self) -> None:
        for vertex in self.vertex_deltas:
            vertex.set_y(vertex.get_y() + self.vertex_deltas[vertex])