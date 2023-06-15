import arcade
import src.plantem.agent.cell as cell
from src.plantem.sim.circulator import circulator
from src.plantem.sim.divider import divider
from src.plantem.loc.vertex.vertex import Vertex

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class GrowingSim(arcade.Window):
    """
    Main application class.
    """

    timestep = None
    circulator = None
    divider = None
    root_midpointx = None
    cell_list = None

    def __init__(self, width, height, title, timestep, root_midpoint_x):
        super().__init__(width, height, title)
        self.timestep = timestep
        arcade.set_background_color(color=[250, 250, 250])
        self.root_midpointx = root_midpoint_x

    def get_root_midpointx(self):
        return self.root_midpointx

    def get_timestep(self):
        return self.timestep

    def get_tick(self) -> int:
        return self.tick

    def setup(self):
        """Set up the Simulation. Call to re-start the Simulation."""
        self.tick = 0
        self.circulator = circulator.Circulator()
        self.divider = divider.Divider()
        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.cell_list = arcade.SpriteList(use_spatial_hash=False)
        this_cell = cell.GrowingCell(
            self,
            [
                Vertex(100.0, 100.0),
                Vertex(100.0, 300.0),
                Vertex(300.0, 300.0),
                Vertex(300.0, 100.0),
            ],
            1,
        )
        self.cell_list.append(this_cell)

    def on_draw(self):
        """
        Render the screen.
        """
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


def main(timestep, root_midpoint_x):
    """Main function"""
    simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x)
    simulation.setup()
    arcade.run()
