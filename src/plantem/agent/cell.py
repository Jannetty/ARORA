import arcade
from agent.circ_module import BaseCirculateModule
from loc.quad_perimeter import QuadPerimeter
from loc.vertex import Vertex

class GrowingCell(arcade.Sprite):

    quad_perimeter = None
    circulator = None
    sim = None

    def __init__(self, simulation, corners: list):
        super().__init__()

        perimeter = []
        for corner in corners:
            v = Vertex(corner[0], corner[1])
            perimeter.append(v)
        self.quad_perimeter = QuadPerimeter(perimeter)

        self.color = [0,200,5]
        circulator = BaseCirculateModule(self)
        sim = simulation

    def draw(self):
        arcade.draw_polygon_filled(point_list=self.quad_perimeter.get_corners(), color=self.color)
        arcade.draw_polygon_outline(point_list=self.quad_perimeter.get_corners(), color=[0,0,0])

    def update(self):
        corners = self.quad_perimeter.get_corners()
        new_corners = []
        for idx, corner in enumerate(corners):
            new_corner = corner
            if idx == 1 or idx == 2:
                new_corner[1] = corner[1] + .3
            new_corners.append(new_corner)
        self.quad_perimeter.set_corners(new_corners)