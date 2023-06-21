import arcade
from src.plantem.agent.circ_module import BaseCirculateModule
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.loc.vertex.vertex import Vertex


class GrowingCell(arcade.Sprite):
    quad_perimeter = None
    circulator = None
    sim = None
    a_neighbors = []
    b_neighbors = []
    l_neighbors = []
    m_neighbors = []

    def __init__(self, simulation, corners: list, init_vals):
        super().__init__()
        self.quad_perimeter = QuadPerimeter(corners)
        self.color = [0, 200, 5]
        self.circulator = BaseCirculateModule(self, init_vals)
        self.sim = simulation

    def get_quad_perimeter(self):
        return self.quad_perimeter

    def add_neighbor(self, cell: "GrowingCell") -> None:
        neighbor_location = self.find_new_neighbor_relative_location(cell)

    def find_new_neighbor_relative_location(self, cell: "GrowingCell") -> str:
        sim_midpointx = self.sim.get_midpointx()

    def get_a_neighbors(self):
        return self.a_neighbors

    def get_b_neighbors(self):
        return self.b_neighbors

    def get_m_neighbors(self):
        return self.m_neighbors

    def get_l_neighbors(self):
        return self.l_neighbors

    def remove_neighbor(self, cell: "GrowingCell") -> None:
        if isinstance(cell, self.a_neighbors):
            self.a_neighbors.remove(cell)
        if isinstance(cell, self.b_neighbors):
            self.b_neighbors.remove(cell)
        if isinstance(cell, self.l_neighbors):
            self.l_neighbors.remove(cell)
        if isinstance(cell, self.m_neighbors):
            self.m_neighbors.remove(cell)

    def get_area(self) -> float:
        return self.quad_perimeter.get_area()

    def draw(self) -> None:
        arcade.draw_polygon_filled(
            point_list=self.quad_perimeter.get_corners_for_disp(), color=self.color
        )
        arcade.draw_polygon_outline(
            point_list=self.quad_perimeter.get_corners_for_disp(), color=[0, 0, 0]
        )

    def grow(self) -> None:
        self.quad_perimeter.get_top_left().set_y(self.quad_perimeter.get_top_left().get_y() + 0.3)
        self.quad_perimeter.get_top_right().set_y(self.quad_perimeter.get_top_right().get_y() + 0.3)

    def update(self) -> None:
        self.grow()
