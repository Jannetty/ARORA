import arcade
import agent.cell as cell

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class GrowingSim(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.tick = 0
        arcade.set_background_color(color=[250,250,250])

        self.cell_list = None

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """

        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.cell_list = arcade.SpriteList(use_spatial_hash=False)
        this_cell = cell.GrowingCell([[100.0,100.0], [100.0,300.0], [300.0,300.0], [300.0,100.0],])
        self.cell_list.append(this_cell)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        for cell in self.cell_list:
            cell.draw()
        #arcade.finish_render()
        

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.tick += 1
        if self.tick % 1 == 0:
            self.cell_list.update()




def main():
    """ Main function """
    simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    simulation.setup()
    arcade.run()