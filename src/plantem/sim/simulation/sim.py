import arcade
import src.plantem.agent.cell as cell
from src.plantem.sim.circulator.circulator import Circulator
from src.plantem.sim.divider.divider import Divider
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.sim.mover.vertex_mover import VertexMover
from src.plantem.sim.input.input import Input

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Starting Template"


class GrowingSim(arcade.Window):
    """
    Main application class.
    """

    timestep = None
    circulator = None
    vertex_mover = None
    divider = None
    root_midpointx = None
    cell_list = None
    vis = None
    next_cell_id = None
    root_tip_y = 0

    def __init__(self, width, height, title, timestep, root_midpoint_x, vis: bool):
        if vis:
            super().__init__(width, height, title)
            arcade.set_background_color(color=[250, 250, 250])
        self.root_midpointx = root_midpoint_x
        self.timestep = timestep
        self.vis = vis
        # self.input = Input("src/plantem/sim/input/default_init_vals.csv", "src/plantem/sim/input/default_vs.csv", self)
        self.setup()

    def get_root_midpointx(self):
        return self.root_midpointx

    def get_timestep(self):
        return self.timestep

    def get_tick(self) -> int:
        return self.tick

    def get_circulator(self) -> Circulator:
        return self.circulator

    def get_divider(self) -> Divider:
        return self.divider

    def get_vertex_mover(self) -> VertexMover:
        return self.vertex_mover

    def get_cell_list(self) -> arcade.SpriteList:
        return self.cell_list

    def get_next_cell_id(self):
        return self.next_cell_id
    
    def get_root_tip_y(self):
        return self.root_tip_y

    def increment_next_cell_id(self):
        self.next_cell_id += 1

    def setup(self):
        """Set up the Simulation. Call to re-start the Simulation."""
        self.tick = 0
        self.next_cell_id = 0
        self.circulator = Circulator(self)
        self.vertex_mover = VertexMover(self)
        self.divider = Divider(self)
        if self.vis:
            self.camera_sprites = arcade.Camera(self.width, self.height)
        self.cell_list = arcade.SpriteList(use_spatial_hash=False)
        # self.input.input()
        self.root_tip_y = self.get_root_tip_y()
        self.set_dev_zones()

    def set_dev_zones(self):
        for cell in self.cell_list:
            cell.calculate_dev_zone(cell.get_distance_from_tip())

    def get_root_tip_y(self):
        ys = []
        if len(self.cell_list) == 0:
            return 0
        for cell in self.cell_list:
            y = cell.get_quad_perimeter().get_bottom_left().get_y()
            ys.append(y)
        return min(ys)
        

    def on_draw(self):
        """
        Render the screen.
        """
        if self.vis:
            self.clear()
            # Call draw() on all your sprite lists below
            for cell in self.cell_list:
                cell.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.tick += 1
        if self.tick % 1 == 0:
            self.cell_list.update()
            self.vertex_mover.update()
            self.circulator.update()
            self.divider.update()
            self.root_tip_y = self.get_root_tip_y()


def main(timestep, root_midpoint_x, vis):
    """Main function"""
    simulation = GrowingSim(
        SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, vis
    )
    simulation.setup()
    arcade.run()