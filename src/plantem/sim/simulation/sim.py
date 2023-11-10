import arcade
import pandas
import numpy as np
import matplotlib.pyplot as plt
import time
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
    cell_val_file = None
    v_file = None
    input_from_file = False

    def __init__(self, width, height, title, timestep, root_midpoint_x, vis: bool, cell_val_file=None, v_file=None, gparam_series=None):
        if vis:
            super().__init__(width, height, title)
            arcade.set_background_color(color=[250, 250, 250])
        if cell_val_file != None and v_file != None:
            self.input = Input(cell_val_file, v_file, self)
            self.input_from_file = True
        if type(gparam_series) == pandas.core.series.Series:
            self.input.replace_default_to_gparam(gparam_series)
        self.root_midpointx = root_midpoint_x
        self.timestep = timestep
        self.vis = vis
        self.cmap = plt.get_cmap("RdYlBu")
        self.cmap = self.cmap.reversed() # reverse the colormap so that the lowest value is blue and the highest is red
        self.setup()

    def get_root_midpointx(self):
        return self.root_midpointx
    
    def get_cell_by_ID(self, ID):
        for cell in self.cell_list:
            if cell.id == ID:
                return cell
        raise ValueError(f"Cell with ID {ID} not found in cell_list")

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

    def add_to_cell_list(self, cell) -> None:
        self.cell_list.append(cell)
    
    def remove_from_cell_list(self, cell) -> None:
        if cell not in self.cell_list:
            raise ValueError("Cell not in cell_list being removed from cell_list")
        else:
            self.cell_list.remove(cell)

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
        if self.input_from_file:
            self.input.input()
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
        Update cells, vertexes, circulator, and divider
        """
        self.tick += 1
        if self.tick < 2592000:
            print(f"tick {self.tick}, before vis")
            if self.vis:
                curr_cam_position = self.camera_sprites.position
                self.camera_sprites.move((0, self.root_tip_y-2))
                self.camera_sprites.update()
                self.camera_sprites.use()
            print("after vis, before sleep")
            time.sleep(.5)
            print("after sleep")
            self.cell_list.update()
            self.vertex_mover.update()
            self.circulator.update()
            self.divider.update()
            self.root_tip_y = self.get_root_tip_y()

        else:
            print("Simulation Complete")
            arcade.close_window()

def main(timestep, root_midpoint_x, vis, cell_val_file=None, v_file=None, gparam_series=None):
    """Main function"""
    simulation = GrowingSim(
        SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, vis, cell_val_file, v_file, gparam_series
    )
    print("Running Simulation")
    arcade.run()