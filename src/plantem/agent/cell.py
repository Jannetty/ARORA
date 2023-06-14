import arcade
from circ_module import BaseCirculateModule

class GrowingCell(arcade.Sprite):

    corners = None
    circulator = None
    sim = None

    def __init__(self, simulation, corners: list, init_aux):
        super().__init__()
        self.corners = corners
        self.color = [0,200,5]
        circulator = BaseCirculateModule(self, init_aux)
        sim = simulation

    def draw(self):
        arcade.draw_polygon_filled(point_list=self.corners, color=self.color)
        arcade.draw_polygon_outline(point_list=self.corners, color=[0,0,0])

    def update(self):
        for idx, corner in enumerate(self.corners):
            if idx == 1 or idx == 2:
                new_corner = corner
                new_corner[1] = corner[1] + .3