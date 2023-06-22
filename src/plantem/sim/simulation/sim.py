import arcade
import src.plantem.agent.cell as cell
from src.plantem.sim.circulator.circulator import Circulator
from src.plantem.sim.divider import divider
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.sim.mover.vertex_mover import VertexMover

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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
    
    def get_circulator(self) -> Circulator:
        return self.circulator
    
    def get_vertex_mover(self) -> VertexMover:
        return self.vertex_mover

    def setup(self):
        """Set up the Simulation. Call to re-start the Simulation."""
        self.tick = 0
        self.circulator = Circulator()
        self.vertex_mover = VertexMover()
        self.divider = divider.Divider()
        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.cell_list = arcade.SpriteList(use_spatial_hash=False)
        init_vals = {"auxin": 2, "arr": 3, "aux_lax": 3, "pina": 0.5, "pinb": 0.7,
                 "pinl": 0.4, "pinm": 0.2, "k_arr_arr": 1, "k_auxin_auxlax": 1,
                 "k_auxin_pin": 1, "k_arr_pin": 1, "ks": 0.005, "kd": 0.0015}
        this_cell = cell.GrowingCell(
            self,
            [
                Vertex(100.0, 100.0),
                Vertex(100.0, 300.0),
                Vertex(300.0, 300.0),
                Vertex(300.0, 100.0),
            ],
            init_vals
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
        self.vertex_mover.update()


def main(timestep, root_midpoint_x):
    """Main function"""
    simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x)
    simulation.setup()
    arcade.run()
