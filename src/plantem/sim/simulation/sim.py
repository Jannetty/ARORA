import os
import pyglet
import time
import pandas
import matplotlib.pyplot as plt
import arcade
from src.plantem.sim.circulator.circulator import Circulator
from src.plantem.sim.divider.divider import Divider
from src.plantem.sim.mover.vertex_mover import VertexMover
from src.plantem.sim.input.input import Input

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "ARORA"


class GrowingSim(arcade.Window):
    """
    Simulation class. Manages the simulation and all of its components.

    Attributes:
        timestep: The sizee of the timestep of the simulation (in seconds).
        circulator: The circulator that manages the circulation of auxin in the
            simulation.
        vertex_mover: The vertex mover that manages the movement of vertices in
            the simulation.
        divider: The divider that manages the division of cells in the simulation.
        root_midpointx: The x-coordinate of the midpoint of the root.
        cell_list: The list of cells in the simulation.
        vis: Whether or not to visualize the simulation.
        next_cell_id: The next ID to assign to a cell.
        root_tip_y: The y-coordinate of the tip of the root.
        cell_val_file: The file containing the cell values.
        v_file: The file containing the vertex values.
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

    def __init__(
        self,
        width,
        height,
        title,
        timestep,
        root_midpoint_x,
        vis: bool,
        cell_val_file=None,
        v_file=None,
        gparam_series=None,
    ):
        """
        Constructs a new Simulation instance.

        Args:
            width: The width of the simulation window.
            height: The height of the simulation window.
            title: The title of the simulation window.
            timestep: The size of the timestep of the simulation (in seconds).
            root_midpoint_x: The x-coordinate of the midpoint of the root.
            vis: Whether or not to visualize the simulation.
            cell_val_file: The file containing the cell values.
            v_file: The file containing the vertex values.
        """
        if vis == True:
            super().__init__(width, height, title)
        else:
            super().__init__(width, height, title, visible=False)
        arcade.set_background_color(color=[250, 250, 250])
        if cell_val_file is not None and v_file is not None:
            self.input = Input(cell_val_file, v_file, self)
            self.input_from_file = True
        if isinstance(gparam_series, pandas.core.series.Series):
            self.input.replace_default_to_gparam(gparam_series)
        self.root_midpointx = root_midpoint_x
        self.timestep = timestep
        self.vis = vis
        self.cmap = plt.get_cmap("Blues")
        # self.cmap = (
        #     self.cmap.reversed()
        # )  # reverse the colormap so that the lowest value is blue and the highest is red
        self.setup()

    def get_root_midpointx(self) -> float:
        """
        Returns:
            The x-coordinate of the midpoint of the root.
        """
        return self.root_midpointx

    def get_cell_by_ID(self, ID):
        """
        Returns Cell object in cell_list with the given ID.

        Args:
            ID: The ID of the cell to return.

        Returns:
            The cell with the given ID.
        """
        for cell in self.cell_list:
            if cell.id == ID:
                return cell
        raise ValueError(f"Cell with ID {ID} not found in cell_list")

    def get_timestep(self) -> float:
        """Returns the timestep of the simulation (in seconds)."""
        return self.timestep

    def get_tick(self) -> int:
        """Returns the current tick (or step) of the simulation."""
        return self.tick

    def get_circulator(self) -> Circulator:
        """Returns the circulator of the simulation."""
        return self.circulator

    def get_divider(self) -> Divider:
        """Returns the divider of the simulation."""
        return self.divider

    def get_vertex_mover(self) -> VertexMover:
        """Returns the vertex mover of the simulation."""
        return self.vertex_mover

    def get_cell_list(self) -> arcade.SpriteList:
        """Returns the list of all cells in the simulation."""
        return self.cell_list

    def get_next_cell_id(self) -> None:
        """Returns the next ID to assign to a cell."""
        return self.next_cell_id

    def get_root_tip_y(self) -> None:
        """Returns the y-coordinate of the tip of the root."""
        return self.root_tip_y

    def increment_next_cell_id(self) -> None:
        """Increments the next ID to assign to a cell."""
        self.next_cell_id += 1

    def add_to_cell_list(self, cell) -> None:
        """Adds a cell to the cell_list."""
        self.cell_list.append(cell)

    def remove_from_cell_list(self, cell) -> None:
        """Removes a cell from the cell_list."""
        if cell not in self.cell_list:
            raise ValueError("Cell not in cell_list being removed from cell_list")
        self.cell_list.remove(cell)

    def setup(self):
        """Set up the Simulation. Call to re-start the Simulation."""
        self.tick = 0
        self.next_cell_id = 0
        self.circulator = Circulator(self)
        self.vertex_mover = VertexMover(self)
        self.divider = Divider(self)
        if self.vis:
            self.camera_sprites = arcade.Camera()
        self.cell_list = arcade.SpriteList(use_spatial_hash=False)
        if self.input_from_file:
            self.input.input()
        self.root_tip_y = self.get_root_tip_y()
        self.set_dev_zones()

    def set_dev_zones(self) -> None:
        """
        Assigns a development zone to each cell in the simulation based on
        distance from the root tip.
        """
        for cell in self.cell_list:
            cell.calculate_dev_zone(cell.get_distance_from_tip())

    def calculate_root_tip_y(self) -> float:
        """Calculates the y-coordinate of the tip of the root."""
        ys = []
        if len(self.cell_list) == 0:
            return 0
        for cell in self.cell_list:
            y = cell.get_quad_perimeter().get_bottom_left().get_y()
            ys.append(y)
        return min(ys)

    def on_draw(self) -> None:
        """
        Renders the screen.
        """
        if self.vis:
            self.clear()
            # Call draw() on all your sprite lists below
            for cell in self.cell_list:
                cell.draw()

    def on_update(self, delta_time):
        """
        Update cells, vertexes, circulator, and divider

        Args:
            delta_time: The time step.
        """
        self.tick += 1
        if self.tick < 2592:
            print(f"tick: {self.tick}")
            if self.vis:
                self.camera_sprites.move((0, self.root_tip_y - 2))
                self.camera_sprites.update()
                self.camera_sprites.use()
            self.cell_list.update()
            self.vertex_mover.update()
            self.circulator.update()
            self.divider.update()
            self.root_tip_y = self.calculate_root_tip_y()

        else:
            print("Simulation Complete")
            arcade.close_window()


def main(timestep, root_midpoint_x, vis, cell_val_file=None, v_file=None, gparam_series=None):
    """Creates and runs the ABM."""
    if vis == False:
        pyglet.options["headless"] = True
        print("Running headless")
    print("Making GrowingSim")
    simulation = GrowingSim(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SCREEN_TITLE,
        timestep,
        root_midpoint_x,
        vis,
        cell_val_file,
        v_file,
        gparam_series,
    )
    print("Running Simulation")
    arcade.run()
