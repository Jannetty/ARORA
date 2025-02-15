from typing import TYPE_CHECKING
import os
import pyglet
import pandas
from pandas import Series
import matplotlib.pyplot as plt
from arcade import Window, draw_polygon_filled
from arcade import SpriteList
from arcade import set_background_color
from arcade import close_window, set_window
import time
from src.sim.circulator.circulator import Circulator
from src.sim.divider.divider import Divider
from src.sim.mover.vertex_mover import VertexMover
from src.sim.input.input import Input
from src.sim.output.output import Output

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "ARORA"

if TYPE_CHECKING:
    from src.agent.cell import Cell
    from pandas import Series


class GrowingSim(Window):
    """
    Manages the simulation process, including cell growth, division, and vertex movement.

    This class extends the `Window` class from the `arcade` library to visualize the simulation process. It handles
    the initialization of the simulation environment, the execution of simulation steps, and the rendering of simulation
    results. It also manages simulation components such as the circulator, divider, and vertex mover.

    Attributes
    ----------
    timestep : int
        The size of the timestep of the simulation, in seconds.
    circulator : Circulator
        Manages the circulation of auxin within the simulation.
    vertex_mover : VertexMover
        Manages the movement of vertices as cells grow or divide.
    divider : Divider
        Manages the division of cells when they reach a certain size.
    root_midpointx : float
        The x-coordinate of the midpoint of the root, used for positioning.
    cell_list : SpriteList
        A list of cells currently present in the simulation.
    vertex_list : list
        A list of vertices currently present in the simulation.
    vis : bool
        Indicates whether the simulation should be visualized.
    next_cell_id : int
        The ID to be assigned to the next new cell.
    root_tip_y : float
        The y-coordinate of the tip of the root, updated as the simulation progresses.
    cell_val_file : str
        Path to the file containing initial cell values.
    v_file : str
        Path to the file containing vertex information.
    input_from_file : bool, optional
        Specifies whether initial values for the simulation are being loaded from files.

    Parameters
    ----------
    width : int
        The width of the simulation window.
    height : int
        The height of the simulation window.
    title : str
        The title of the simulation window.
    timestep : int
        The timestep size for the simulation, in seconds.
    vis : bool
        Flag to indicate whether the simulation should be visualized.
    cell_val_file : str, optional
        The filename containing cell values to initialize the simulation.
    v_file : str, optional
        The filename containing vertex information to initialize the simulation.
    gparam_series : pandas.Series, optional
        Series containing global parameters for the simulation.
    geometry : str, optional
        Indicates the geometric configuration of the simulation.

    """

    timestep: int
    circulator: "Circulator"
    vertex_mover: "VertexMover"
    divider: "Divider"
    root_midpointx: float
    cell_list: SpriteList
    vertex_list: list
    vis: bool
    next_cell_id: int
    root_tip_y: float = 0
    cell_val_file: str
    v_file: str
    input_from_file: bool = False

    def __init__(
        self,
        width: int,
        height: int,
        title: str,
        timestep: int,
        vis: bool,
        cell_val_file: str = "",
        v_file: str = "",
        gparam_series: pandas.core.series.Series | str = "",
        geometry: str = "",
        output_file: str = "output",
    ):
        """
        Initializes a new instance of the GrowingSim class, setting up the simulation environment and parameters.
        """
        self.cell_list = SpriteList(use_spatial_hash=False)
        self.vertex_list = []
        if vis is False:
            print("Running headless")
            # for mac
            pyglet.options["headless"] = True
            # for PC
            os.environ["ARCADE_HEADLESS"] = "true"
            super().__init__(width, height, title, visible=False)
        if vis is True:
            super().__init__(width, height, title)
            set_background_color(color=(250, 250, 250, 250))
        if cell_val_file != "" and v_file != "":
            self.input = Input(cell_val_file, v_file, self)
            self.input_from_file = True
            self.root_tip_y: float = self.input.get_initial_v_miny()
            self.root_midpointx = self.calculate_root_midpoint_x_from_input()
        if isinstance(gparam_series, pandas.core.series.Series):
            self.input.replace_default_to_gparam(gparam_series)
        self.geometry = geometry
        self.timestep = timestep
        self.vis = vis
        self.cmap = plt.get_cmap("coolwarm")
        self.setup()
        self.output = Output(self, f"{output_file}.csv", f"{output_file}.json")
        self.exit_flag = False

    def get_root_midpointx(self) -> float:
        """
        Retrieves the x-coordinate of the midpoint of the root.

        Returns
        -------
        float
            The x-coordinate of the midpoint of the root.
        """
        return self.root_midpointx

    def get_cell_by_ID(self, ID: int) -> "Cell":
        """
        Retrieves a cell object from the simulation's cell list by its ID.

        Parameters
        ----------
        ID : int
            The ID of the cell to retrieve.

        Returns
        -------
        Cell
            The cell object with the specified ID.

        Raises
        ------
        ValueError
            If no cell with the given ID is found in the cell list.
        """
        for cell in self.cell_list:
            if cell.get_c_id() == ID:
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

    def get_next_cell_id(self) -> int:
        """Returns the next ID to assign to a cell."""
        return self.next_cell_id

    def get_root_tip_y(self) -> float:
        """Returns the y-coordinate of the tip of the root."""
        return self.root_tip_y

    def increment_next_cell_id(self) -> None:
        """Increments the next ID to assign to a cell."""
        self.next_cell_id += 1

    def add_to_cell_list(self, cell: "Cell") -> None:
        """Adds a cell to the cell_list."""
        self.cell_list.append(cell)
        new_vs = cell.get_quad_perimeter().get_vs()
        self.vertex_list.extend(new_vs)
        self.root_midpointx = self.calculate_root_midpoint_x_from_vertex_list()
        cell.get_circ_mod().update_left_right()

    def remove_from_cell_list(self, cell: "Cell") -> None:
        """Removes a cell from the cell_list."""
        if cell not in self.cell_list:
            raise ValueError("Cell not in cell_list being removed from cell_list")
        self.cell_list.remove(cell)

    def setup(self) -> None:
        """
        Sets up the simulation, initializing its components and loading initial conditions.

        This method is called to (re)start the simulation, setting up initial cell configurations,
        and preparing the simulation environment.
        """
        # find midpoint x of root basd on vertices that exist
        self.tick = 0
        self.next_cell_id = 0
        self.circulator = Circulator(self)
        self.vertex_mover = VertexMover(self)
        self.divider = Divider(self)
        if self.input_from_file:
            self.input.make_cells_from_input_files()
        self.root_tip_y = self.calculate_root_tip_y()
        self.root_midpointx = self.calculate_root_midpoint_x_from_vertex_list()

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

    def calculate_root_midpoint_x_from_vertex_list(self) -> float:
        """Calculates the midpoint of the x-coordinates from the vertex list."""
        xs = []
        if len(self.vertex_list) == 0:
            return 0
        for vertex in self.vertex_list:
            x = vertex.get_x()
            xs.append(x)
        min_x = min(xs)
        max_x = max(xs)
        mid_x = (min_x + max_x) / 2
        return mid_x

    def calculate_root_midpoint_x_from_input(self) -> float:
        """Calculates the midpoint of the x-coordinates from the input vertex file."""
        vertex_input = self.input.vertex_input
        if len(vertex_input) == 0:
            return 0
        xs = vertex_input["x"].tolist()
        min_x = min(xs)
        max_x = max(xs)
        mid_x = (min_x + max_x) / 2
        return mid_x

    def on_draw(self) -> None:
        """
        Renders the screen.
        """
        print("Drawing")
        self.switch_to()  # Ensure the OpenGL context is active
        if self.vis:
            self.clear()
            for cell in self.cell_list:
                cell.draw()
        self.flip()  # Flip the buffers to update the display

    def update_viewport_position(self) -> None:
        """
        Updates the position of the viewport.
        """
        self.set_viewport(
            0,
            SCREEN_WIDTH,
            self.root_tip_y - 100,
            SCREEN_HEIGHT + self.root_tip_y - 100,
        )
        self.window_offset = self.root_tip_y - 100

    def on_update(self, delta_time: float) -> None:
        """
        Update cells, vertexes, circulator, and divider

        Args:
            delta_time: The time step.
        """
        print("----")
        self.output.output_cells()
        self.tick += 1
        # max_tick = 24 * 8
        try:
            if self.tick < 27:
                self.output.output_cells()
                print(f"tick: {self.tick}")
                if self.vis:
                    self.update_viewport_position()
                    self.on_draw()
                self.cell_list.update()
                self.vertex_mover.update()
                self.circulator.update()
                self.divider.update()
                self.root_tip_y = self.calculate_root_tip_y()
                total_aux = sum([cell.get_circ_mod().get_auxin() for cell in self.cell_list])
                total_area = sum([cell.get_quad_perimeter().get_area() for cell in self.cell_list])
                print(f"Total auxin: {total_aux}")
                print(f"Total area: {total_area}")
                print(f"Total auxin/area = {total_aux/total_area}")
            else:
                print("Simulation Complete")
                self.exit_flag = True  # Set the exit flag
        except (ValueError, OverflowError) as e:
            print(e)
            print("Ending Simulation")
            self.exit_flag = True  # Set the exit flag
            raise e

    def run_sim(self) -> None:
        while not self.exit_flag:
            pyglet.clock.tick()
            self.dispatch_events()
            self.on_update(1 / 60.0)
        print("CLOSING WINDOW")
        self.close()  # Close the window
        print("WINDOW CLOSED")
        pyglet.app.exit()  # Exit the pyglet event loop


def main(
    timestep: int,
    vis: bool,
    cell_val_file: str = "",
    v_file: str = "",
    gparam_series: Series | str = "",
) -> int:
    """Creates and runs the ABM."""
    print("Making GrowingSim")
    geometry = ""
    if cell_val_file == "default" and v_file == "default":
        cell_val_file = "src/sim/input/aux_syndegonly_init_vals.json"
        v_file = "src/sim/input/default_vs.json"
        geometry = "default"
    output_file_name = "2024100801"
    simulation = GrowingSim(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SCREEN_TITLE,
        timestep,
        vis,
        cell_val_file,
        v_file,
        gparam_series,
        geometry,
        output_file_name,
    )
    set_window(simulation)
    print("Running Simulation")
    simulation.run_sim()
    return simulation.get_tick()
