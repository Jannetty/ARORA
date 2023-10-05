from src.plantem.agent.cell import GrowingCell
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.loc.vertex.vertex import Vertex


class VertexMover:
    def __init__(self, sim) -> None:
        # dictionary, key is cell, value is amount bottom vertices should move
        self.cell_deltas = {}
        # dictionary, key is vertex, value is amount vertex should move total
        self.vertex_deltas = {}
        self.sim = sim

    def add_cell_delta_val(self, cell: GrowingCell, deltaX: float) -> None:
        if cell in self.cell_deltas:
            raise ValueError(f"Multiple delta vals added to VertexMover for cell {cell}")
        else:
            self.cell_deltas[cell] = deltaX

    def get_cell_delta_val(self, cell: GrowingCell) -> float:
        return self.cell_deltas[cell]

    def get_vertex_delta_val(self, vertex: Vertex) -> float:
        return self.vertex_deltas[vertex]

    def update(self) -> None:
        top_row = self.get_top_row()
        sorted_top_row = self.sort_top_row(top_row)
        self.propogate_deltas(sorted_top_row)
        max_delta = self.get_max_delta()
        print(f"max_delta: {max_delta}")
        self.execute_vertex_movement(max_delta)
        self.check_if_divide(self.cell_deltas.keys())
        self.cell_deltas.clear()
        self.vertex_deltas.clear()

    def get_max_delta(self) -> float:
        max_delta = None
        max_abs_delta = None
        print(self.vertex_deltas)
        for delta in self.vertex_deltas.values():
            absolute_delta = abs(delta)
            if max_abs_delta is None or absolute_delta > max_abs_delta:
                max_abs_delta = absolute_delta
                max_delta = delta
        return max_delta

    def get_top_row(self) -> list:
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

    def sort_top_row(self, top_row: list) -> list:
        left_xs = []
        for cell in top_row:
            left_xs.append(cell.get_quad_perimeter().get_top_left().get_x())
        return [cell for _, cell in sorted(zip(left_xs, top_row))]

    def propogate_deltas(self, top_row: list) -> None:
        for cell in top_row:
            this_delta = self.cell_deltas[cell]
            self.add_cell_b_vertices_to_vertex_deltas(cell, this_delta)
            self.propogate_deltas_to_b_neighbors(cell, this_delta)

    def add_cell_b_vertices_to_vertex_deltas(self, cell: GrowingCell, delta: float) -> None:
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

    def propogate_deltas_to_b_neighbors(self, cell: GrowingCell, delta: float) -> None:
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

    def execute_vertex_movement(self, max_delta: int) -> None:
        for vertex in self.vertex_deltas:
            vertex.set_y(vertex.get_y() + self.vertex_deltas[vertex])
        # iterate through all nongrowing cells, move all basal vertices not yet moved
        moved_vs = list(self.vertex_deltas.keys())
        for cell in self.sim.get_cell_list():
            if not cell.get_growing():
                print(f"cell {cell.get_id()} vertices being considered")
                print(f"cell {cell.get_id()} vertices len: {len(cell.get_quad_perimeter().get_vs())}")
                vertices = cell.get_quad_perimeter().get_vs()
                for vertex in vertices:
                    if vertex not in moved_vs:
                        print(f"vertex {vertex.get_xy()} being moved")
                        vertex.set_y(vertex.get_y() + max_delta)
                        print(f"vertex {vertex.get_xy()} moved")
                        moved_vs.append(vertex)
        

    def check_if_divide(self, cells) -> None:
        for cell in cells:
            if cell.get_quad_perimeter().get_area() >= (
                2 * cell.get_quad_perimeter().get_init_area()
            ):
                self.sim.get_divider().add_cell(cell)
