import arcade
from src.plantem.agent.circ_module import BaseCirculateModule
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.loc.vertex.vertex import Vertex

class GrowingCell(arcade.Sprite):

    quad_perimeter = None
    circulator = None
    sim = None

    def __init__(self, simulation, corners: list, init_aux):
        super().__init__()

        self.quad_perimeter = QuadPerimeter(corners)

        self.color = [0,200,5]
        circulator = BaseCirculateModule(self, init_aux)
        sim = simulation

    def get_area(self):
        return self.quad_perimeter.get_area()

    def draw(self):
        arcade.draw_polygon_filled(point_list=self.quad_perimeter.get_corners_for_disp(), color=self.color)
        arcade.draw_polygon_outline(point_list=self.quad_perimeter.get_corners_for_disp(), color=[0,0,0])

    def update(self):
        pass