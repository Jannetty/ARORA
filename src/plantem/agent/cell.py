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

        self.color = [0,200,5]
        circulator = BaseCirculateModule(self, init_vals)
        sim = simulation

    def add_neighbor(self, cell: 'GrowingCell') -> None:
        neighbor_location = self.find_new_neighbor_relative_location(cell)

    def find_new_neighbor_relative_location(self, cell: 'GrowingCell') -> str:
        sim_midpointx = self.sim.get_midpointx()

    def get_a_neighbors(self):
        return self.a_neighbors
    def get_b_neighbors(self):
        return self.b_neighbors
    def get_m_neighbors(self):
        return self.m_neighbors
    def get_l_neighbors(self):
        return self.l_neighbors


    def remove_neighbor(self, cell: 'GrowingCell') -> None:
        if isinstance(cell, self.a_neighbor):
            self.a_neighbor.remove(cell)
        if isinstance(cell, self.b_neighbor):
            self.b_neighbor.remove(cell)
        if isinstance(cell, self.l_neighbor):
            self.l_neighbor.remove(cell)
        if isinstance(cell, self.m_neighbor):
            self.m_neighbor.remove(cell)

    def get_area(self) -> float:
        return self.quad_perimeter.get_area()

    def draw(self) -> None:
        arcade.draw_polygon_filled(point_list=self.quad_perimeter.get_corners_for_disp(), color=self.color)
        arcade.draw_polygon_outline(point_list=self.quad_perimeter.get_corners_for_disp(), color=[0,0,0])

    def grow(self) -> None:
        pass

    def update(self) -> None:
        new_bottom_left = self.quad_perimeter.get_bottom_left()
        new_bottom_right = self.quad_perimeter.get_bottom_right()
        old_top_left_xy = self.quad_perimeter.get_top_left().get_xy()
        old_top_right_xy = self.quad_perimeter.get_top_right().get_xy()
        new_top_left = Vertex(old_top_left_xy[0], old_top_left_xy[1]+.3)
        new_top_right = Vertex(old_top_right_xy[0], old_top_right_xy[1]+.3)
        self.quad_perimeter.set_corners([new_top_left,new_top_right, new_bottom_right, new_bottom_left])