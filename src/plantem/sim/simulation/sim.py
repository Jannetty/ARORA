import arcade
import src.plantem.agent.cell as cell
from src.plantem.sim.circulator import circulator
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

    def __init__(self, width, height, title, timestep):
        super().__init__(width, height, title)

        self.timestep = timestep
        self.circulator = circulator.Circulator()
        self.tick = 0
        arcade.set_background_color(color=[250,250,250])
        self.cell_list = None

    def get_timestep():
        return self.timestep

    def get_tick(self) -> int:
        return self.tick

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """

        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.cell_list = arcade.SpriteList(use_spatial_hash=False)
        this_cell = cell.GrowingCell(self, [Vertex(100.0,100.0), Vertex(100.0,300.0), Vertex(300.0,300.0), Vertex(300.0,100.0)], 1)
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




def main(timestep):
    """ Main function """
    simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep)
    simulation.setup()
    arcade.run()