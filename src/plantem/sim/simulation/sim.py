import os
import pyglet
import pandas
import matplotlib.pyplot as plt
from arcade import Window
from arcade import SpriteList
from arcade import set_background_color
from arcade import close_window
import time
from src.plantem.sim.circulator.circulator import Circulator
from src.plantem.sim.divider.divider import Divider
from src.plantem.sim.mover.vertex_mover import VertexMover
from src.plantem.sim.input.input import Input
from src.plantem.sim.output.output import Output

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "ARORA"


class GrowingSim(Window):
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
    geometry = None

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
        geometry=None,
    ):
        """
        Constructs a new Simulation instance.

        Args:
            width: The width of the simulation window.
            height: The height of the simulation window.
            title: The title of the simulation window.
            timestep: The size of the timestep of the simulation (in hours).
            root_midpoint_x: The x-coordinate of the midpoint of the root.
            vis: Whether or not to visualize the simulation.
            cell_val_file: The file containing the cell values.
            v_file: The file containing the vertex values.
        """
        if vis is False:
            print("Running headless")
            # for mac
            pyglet.options["headless"] = True
            # for PC
            os.environ["ARCADE_HEADLESS"] = "true"
            super().__init__(width, height, title, visible=False)
        if vis is True:
            super().__init__(width, height, title)
        set_background_color(color=[250, 250, 250])
        if cell_val_file is not None and v_file is not None:
            self.input = Input(cell_val_file, v_file, self)
            self.input_from_file = True
            self.root_tip_y = self.input.initial_v_miny
        if isinstance(gparam_series, pandas.core.series.Series):
            self.input.replace_default_to_gparam(gparam_series)
        self.root_midpointx = root_midpoint_x
        self.geometry = geometry
        self.timestep = timestep
        self.vis = vis
        self.cmap = plt.get_cmap("coolwarm")
        # self.output = Output(self, "yes_aux_exchange_scaling_mem_pin_allocation_by_weight.csv")
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

    def get_cell_list(self) -> SpriteList:
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
        # find midpoint x of root basd on vertices that exist
        # I think function will be (max_x - min_x) / 2
        self.tick = 0
        self.next_cell_id = 0
        self.circulator = Circulator(self)
        self.vertex_mover = VertexMover(self)
        self.divider = Divider(self)
        self.cell_list = SpriteList(use_spatial_hash=False)
        if self.input_from_file:
            self.input.make_cells_from_input_files()
        self.root_tip_y = self.calculate_root_tip_y()

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
            y = cell.get_quad_perimeter().get_min_y()
            ys.append(y)
        return min(ys)

    def calculate_root_midpoint_x(self) -> float:
        xs = []
        if len(self.cell_list) == 0:
            return 0
        for cell in self.cell_list:
            x = cell.get_quad_perimeter().vertex_list
            xs.append(x)
        min_x = min(xs)
        max_x = max(xs)
        mid_x = (min_x + max_x) / 2
        return mid_x

    def on_draw(self) -> None:
        """
        Renders the screen.
        """
        print("Drawing")
        if self.vis:
            self.clear()
            for cell in self.cell_list:
                cell.draw()

    def update_viewport_position(self) -> None:
        """
        Updates the position of the viewport.
        """
        self.set_viewport(
            0,
            SCREEN_WIDTH,
            # 0,
            # 1200,
            self.root_tip_y - 2,
            SCREEN_HEIGHT + self.root_tip_y - 2,
        )
        self.window_offset = self.root_tip_y - 2

    def on_update(self, delta_time):
        """
        Update cells, vertexes, circulator, and divider

        Args:
            delta_time: The time step.
        """
        print("--------------------")
        self.tick += 1
        max_tick = 200
        # max_tick = 2592
        try:
            if self.tick < max_tick:
                # self.output.output_cells()
                print(f"tick: {self.tick}")
                if self.vis:
                    self.update_viewport_position()
                self.cell_list.update()
                self.vertex_mover.update()
                self.circulator.update()
                self.divider.update()
                self.root_tip_y = self.calculate_root_tip_y()

            else:
                print("Simulation Complete")
                close_window()
        except (ValueError, OverflowError) as e:
            print(e)
            print("Ending Simulation")
            close_window()

    # def on_mouse_press(self, x, y, button, modifiers):
    #     print("Mouse press!")
    #     print(f"X: {x}, Y: {y}")
    #     y = self.window_offset + y
    #     print(f"with, windowoffset, X: {x}, Y: {y}")
    #     for cell in self.cell_list:
    #         if cell.get_quad_perimeter().point_inside(x, y):
    #             print(f"Cell {cell.get_id()}, growing = {cell.growing}")


def main(
    timestep, root_midpoint_x, vis, cell_val_file=None, v_file=None, gparam_series=None
) -> int:
    """Creates and runs the ABM."""
    print("Making GrowingSim")
    geometry = None
    if cell_val_file == "default" and v_file == "default":
        cell_val_file = "src/plantem/sim/input/default_init_vals.csv"
        v_file = "src/plantem/sim/input/default_vs.csv"
        geometry = "default"
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
        geometry,
    )
    print("Running Simulation")
    pyglet.app.run(0)

    return simulation.get_tick()
