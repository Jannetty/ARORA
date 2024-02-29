from arcade import Sprite
from arcade import draw_polygon_filled, draw_polygon_outline
from typing import TYPE_CHECKING, Any, cast
from src.agent.circ_module_cont import BaseCirculateModuleCont
from src.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.agent.default_geo_neighbor_helpers import NeighborHelpers

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim
    from src.loc.vertex.vertex import Vertex

# Growth rate of cells in meristematic zone in um per um per hour from Van den Berg et al. 2018
MERISTEMATIC_GROWTH_RATE: float = -0.0179

# Growth rate cells in transition zone in um per um per hour from Van den Berg et al. 2018
TRANSITION_GROWTH_RATE: float = -0.0179

# Growth rate cells in elongation zone in um per um per hour from Van den Berg et al. 2018
ELONGATION_GROWTH_RATE: float = -0.00112

# Growth rate cells in differentiation zone in um per um per hour from Van den Berg et al. 2018
DIFFERENTIATION_GROWTH_RATE: float = -0.00112

# um Y distance from tip at which cells pass from root tip to meristematic zone
# Inferred from Van dn Berg et al. 2018
ROOT_TIP_DIST_FROM_TIP: int = 74

# um Y distance from tip at which cells pass from meristemtic to transition zone
# from Van den Berg et al. 2018
MERISTEMATIC_MAX_DIST_FROM_TIP: int = 160

# um Y distance from tip at which cells pass from transition to elongation zone
# from Van den Berg et al. 2018
TRANSITION_MAX_DIST_FROM_TIP: int = 340

# um Y distance from tip at which cells pass from elongation to differentiation zone
# from Van den Berg et al. 2018
ELONGATION_MAX_DIST_FROM_TIP: int = 460

# um Y distance from tip at which cells leave differentiation zone
# from Van den Berg et al. 2018
DIFFERENTIATION_MAX_DIST_FROM_TIP: int = 960

# max um X distance vasc cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
VASC_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 12

# max um X distance peri cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
PERI_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 17

# max um X distance endo cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
ENDO_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 24

# max um X distance cortex cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
CORTEX_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 35

# max um X distance epidermis cells can be from self.sim.get_root_midpointx()
# from Salvi et al. 2020
EPIDERMIS_CELL_DIST_FROM_ROOT_MIDPOINTX: int = 45


class Cell(Sprite):
    """
    Represents a cell in the simulation.

    Args:
        simulation (GrowingSim): The simulation object.
        corners (list): The Vertex corners of the cell.
        init_vals (dict): Initial values for cell Circ Mod.
        id (int): The ID of the cell.

    Attributes:
        c_id (int): The ID of the cell.
        a_neighbors (list): List of apical neighbors.
        b_neighbors (list): List of basal neighbors.
        l_neighbors (list): List of lateral neighbors.
        m_neighbors (list): List of medial neighbors.
        sim (GrowingSim): The simulation object that calls this cell.
        quad_perimeter (QuadPerimeter): The quad perimeter object defining
                                        this cell's location.
        circ_mod (BaseCirculateModule): The circ module object that will manage
                                        hormone circulation for this cell.
        growing (bool): Indicates if the cell is growing.
        dev_zone (float): The development zone of the cell.
        cell_type (str): The type of the cell.
        color (str): The color of the cell.
    """

    def __init__(
        self,
        simulation: "GrowingSim",
        corners: list["Vertex"],
        init_vals: dict[str, Any],
        c_id: int,
    ):
        """
        Initializes a new instance of the Cell class.
        """
        self.c_id = c_id
        super().__init__()
        self.a_neighbors: list["Cell"] = []
        self.b_neighbors: list["Cell"] = []
        self.l_neighbors: list["Cell"] = []
        self.m_neighbors: list["Cell"] = []
        self.sim: "GrowingSim" = simulation
        simulation.increment_next_cell_id()
        self.quad_perimeter = QuadPerimeter(corners)
        if init_vals.get("circ_mod") == "cont":
            self.circ_mod = BaseCirculateModuleCont(self, init_vals)
        else:
            print("Circ mod not recognized, using continuous circ mod")
            self.circ_mod = BaseCirculateModuleCont(self, init_vals)
        self.pin_weights: dict[str, float] = self.calculate_pin_weights()
        self.growing: bool = cast(bool, init_vals.get("growing"))
        self.dev_zone: str = self.calculate_dev_zone(self.get_distance_from_tip())
        self.cell_type: str = self.calculate_cell_type()
        self.color: tuple[int, int, int, int] = self.calculate_color()

    def calculate_cell_type(self) -> str:
        """
        Calculates the type of cell based on its x location in relation to center of root.
        Note: This only works for the default geometry.

        Returns:
            Type of cell (str)
        """
        root_tip_midpoint_x = self.sim.get_root_midpointx()
        cell_midpoint_x = self.quad_perimeter.get_midpointx()
        dist_from_root_midpoint = abs(root_tip_midpoint_x - cell_midpoint_x)
        cell_type = None
        if self.dev_zone == "roottip":
            cell_type = "roottip"
        elif dist_from_root_midpoint < VASC_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "vasc"
        elif dist_from_root_midpoint < PERI_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "peri"
        elif dist_from_root_midpoint < ENDO_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "endo"
        elif dist_from_root_midpoint < CORTEX_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "cortex"
        elif dist_from_root_midpoint < EPIDERMIS_CELL_DIST_FROM_ROOT_MIDPOINTX:
            cell_type = "epidermis"
        if cell_type is None:
            raise ValueError("Cell type not recognized")
        return cell_type
    
    def get_cell_type(self) -> str:
        """
        Returns the type of cell.

        Returns
        -------
        str 
            The type of cell.
        """
        return self.cell_type

    def calculate_color(self) -> tuple[int, int, int, int]:
        """
        Calculates the color of the cell based on the auxin concentration and sim's cmap.

        Returns:
            list: A list containing the RGB values of the calculated color.
        """
        auxin = self.circ_mod.get_auxin()
        max_auxin = 2000  # TODO make this not hard coded
        normalized_auxin = (auxin) / (max_auxin)
        rgba = self.sim.cmap(normalized_auxin)
        # Scale and round the RGB values
        red, green, blue = (
            int(rgba[0] * 255 + 0.5),
            int(rgba[1] * 255 + 0.5),
            int(rgba[2] * 255 + 0.5),
        )
        alpha = 255
        return (red, green, blue, alpha)

    def get_quad_perimeter(self) -> "QuadPerimeter":
        """
        Returns the quad perimeter object defining the cell's location

        Returns:
            float: The quad perimeter object defining the cell's location.
        """
        return self.quad_perimeter

    def get_c_id(self) -> int:
        """
        Returns the ID of the cell.

        Returns:
            int: The ID of the cell.
        """
        return self.c_id

    def get_dev_zone(self) -> str:
        """
        Returns the development zone of the cell.

        Returns:
            string: The development zone of the cell.
        """
        return self.dev_zone

    def set_dev_zone(self, zone: str) -> None:
        """
        Sets the development zone of the cell.

        Args:
            zone (string): The development zone to set for the cell.
        """
        self.dev_zone = zone

    def set_growing(self, growing: bool) -> None:
        """
        Sets the growing status of the cell.

        Args:
            growing (bool): The growing status to set for the cell.
        """
        self.growing = growing

    def get_growing(self) -> bool:
        """
        Returns the growing status of the cell.

        Returns:
            bool: The growing status of the cell.
        """
        return self.growing

    def add_neighbor(self, neighbor: "Cell") -> None:
        """
        Adds a neighbor to the cell's correct neighbor list.

        Args:
            neighbor (Cell): The neighbor to add to the cell's neighbor list.
        """
        if not self.check_if_neighbor(neighbor):
            neighbor_location = self.find_new_neighbor_relative_location(neighbor)
            if neighbor_location == "a":
                self.a_neighbors.append(neighbor)
            elif neighbor_location == "b":
                self.b_neighbors.append(neighbor)
            elif neighbor_location == "l":
                self.l_neighbors.append(neighbor)
            elif neighbor_location == "m":
                self.m_neighbors.append(neighbor)
            elif neighbor_location == "cell no longer root cap cell neighbor":
                pass
            elif neighbor_location is None:
                print(f"cell {self.c_id} is not neighbors with cell {neighbor.get_c_id()}")
                raise ValueError("Non-neighbor added as neighbor")
            else:
                raise ValueError("Non-neighbor added as neighbor")
        else:
            raise ValueError("Neighbor being added twice")

    def find_new_neighbor_relative_location(self, neighbor: "Cell") -> str:
        """
        Finds the relative location of a new neighbor to the cell.

        Args:
            neighbor (Cell): The neighbor to find the relative location of.

        Returns:
            string: The relative location of the neighbor to the cell.
        """
        self_vs = self.get_quad_perimeter().get_vs()
        neighbor_vs = neighbor.get_quad_perimeter().get_vs()
        if len(set(self_vs).intersection(set(neighbor_vs))) == 1 and self.sim.geometry == "default":
            return NeighborHelpers.get_neighbor_dir_neighbor_shares_one_v_default_geo(
                self, neighbor
            )
        if len(set(self_vs).intersection(set(neighbor_vs))) == 0 and self.sim.geometry == "default":
            return NeighborHelpers.get_neighbor_dir_neighbor_shares_no_vs_default_geo(
                self, neighbor
            )
        if len(set(self_vs).intersection(set(neighbor_vs))) == 2:
            return self.get_neighbor_di_neighbor_shares_two_vs_std(neighbor)
        if len(set(self_vs).intersection(set(neighbor_vs))) == 1:
            return self.get_neighbor_dir_neighbor_shares_one_v_std(neighbor)
        raise ValueError("Neighbor not recognized")

    def get_a_neighbors(self) -> list["Cell"]:
        """
        Returns the list of apical neighbors.

        Returns:
            list: The list of apical neighbors.
        """
        return self.a_neighbors

    def get_b_neighbors(self) -> list["Cell"]:
        """
        Returns the list of basal neighbors.

        Returns:
            list: The list of basal neighbors.
        """
        return self.b_neighbors

    def get_m_neighbors(self) -> list["Cell"]:
        """
        Returns the list of medial neighbors.

        Returns:
            list: The list of medial neighbors.
        """
        return self.m_neighbors

    def get_l_neighbors(self) -> list["Cell"]:
        """
        Returns the list of lateral neighbors.

        Returns:
            list: The list of lateral neighbors.
        """
        return self.l_neighbors

    def get_all_neighbors(self) -> list["Cell"]:
        """
        Returns the list of all neighbors.

        Returns:
            list: The list of all neighbors.
        """
        return (
            self.get_a_neighbors()
            + self.get_b_neighbors()
            + self.get_m_neighbors()
            + self.get_l_neighbors()
        )

    def get_sim(self) -> "GrowingSim":
        """
        Returns the simulation object that calls this cell.

        Returns:
            Simulation: The simulation object that calls this cell.
        """
        return self.sim

    def get_circ_mod(self) -> "BaseCirculateModuleCont":
        """
        Returns the circ module object that will manage hormone circulation for this cell.

        Returns:
            BaseCirculateModule: The circ module object that will manage
                                 hormone circulation for this cell.
        """
        return self.circ_mod

    def remove_neighbor(self, cell: "Cell") -> None:
        """
        Removes a neighbor from the cell's neighbor list.

        Args:
            cell (Cell): The neighbor to remove from the cell's neighbor list.
        """
        if cell in self.a_neighbors:
            self.a_neighbors.remove(cell)
        elif cell in self.b_neighbors:
            self.b_neighbors.remove(cell)
        elif cell in self.l_neighbors:
            self.l_neighbors.remove(cell)
        elif cell in self.m_neighbors:
            self.m_neighbors.remove(cell)
        else:
            raise ValueError("Non neighbor cell being removed from neighbor list")

    def check_if_neighbor(self, cell: "Cell") -> bool:
        """
        Checks if a cell is a neighbor of the cell.

        Args:
            cell (Cell): The cell to check if it is a neighbor.

        Returns:
            bool: True if the cell is a neighbor (in the neighbor lists), False if not.
        """
        if cell in self.a_neighbors:
            return True
        if cell in self.b_neighbors:
            return True
        if cell in self.l_neighbors:
            return True
        if cell in self.m_neighbors:
            return True
        return False

    def get_area(self) -> float:
        """
        Returns the area of the cell.

        Returns:
            float: The area of the cell.
        """
        return self.quad_perimeter.get_area()

    def draw(
        self, *, filter: Any = None, pixelated: Any = None, blend_function: Any = None
    ) -> None:
        """
        Draws the cell on the screen.
        """
        super().draw(filter=filter, pixelated=pixelated, blend_function=blend_function)
        self.color = self.calculate_color()
        point_list = self.quad_perimeter.get_corners_for_disp()
        draw_polygon_filled(point_list=point_list, color=self.color)
        draw_polygon_outline(point_list=point_list, color=(0, 0, 0, 255), line_width=1)

    def grow(self) -> None:
        """
        Grows the cell by adding the cell and calculated delta to the sim's vertex mover.
        """
        self.sim.get_vertex_mover().add_cell_delta_val(self, self.calculate_delta())

    def get_distance_from_tip(self) -> float:
        """
        Returns the distance of the cell from the root tip.

        Returns:
            float: The distance of the cell from the root tip.
        """
        root_tip_y = self.sim.get_root_tip_y()
        self_y = self.quad_perimeter.get_midpointy()
        return abs(self_y - root_tip_y)

    def calculate_dev_zone(self, dist_to_root_tip: float) -> str:
        """
        Calculates the development zone of the cell based on its distance from the root tip.
        Note: This only works for the default geometry.

        Args:
            dist_to_root_tip (float): The distance of the cell from the root tip.

        Returns:
            string: The development zone of the cell.
        """
        root_cap_cells = [
            60,
            90,
            120,
            136,
            166,
            210,
            296,
            75,
            105,
            135,
            151,
            181,
            225,
            311,
        ]
        if self.c_id in root_cap_cells:
            return "roottip"
        if dist_to_root_tip < ROOT_TIP_DIST_FROM_TIP:
            return "roottip"
        if dist_to_root_tip < MERISTEMATIC_MAX_DIST_FROM_TIP:
            return "meristematic"
        if dist_to_root_tip < TRANSITION_MAX_DIST_FROM_TIP:
            return "transition"
        if dist_to_root_tip < ELONGATION_MAX_DIST_FROM_TIP:
            return "elongation"
        return "differentiation"

    def get_growth_rate(self) -> float:
        """
        Returns the growth rate of the cell based on its development zone.
        Note: This only works for the default geometry.

        Returns:
            float: The growth rate of the cell.
        """
        if self.get_quad_perimeter().get_height() >= 250:
            print(f"cell {self.c_id} has reached max height")
            self.growing = False
            return 0
        if self.dev_zone == "roottip":
            return 0
        if self.dev_zone == "meristematic":
            return MERISTEMATIC_GROWTH_RATE
        if self.dev_zone == "transition":
            return TRANSITION_GROWTH_RATE
        if self.dev_zone == "elongation":
            return ELONGATION_GROWTH_RATE
        if self.dev_zone == "differentiation":
            return DIFFERENTIATION_GROWTH_RATE
        print(f"Cell {self.c_id} distance to root tip = {self.get_distance_from_tip()}")
        raise ValueError("Cell has no recognizable dev zone")

    def calculate_delta(self) -> float:
        """
        Calculates the growth delta of the cell.
        Note: This only works for the default geometry.

        Returns:
            float: The growth delta of the cell.
        """
        dist_to_root_tip = self.get_distance_from_tip()
        self.dev_zone = self.calculate_dev_zone(dist_to_root_tip)
        return self.get_growth_rate()

    def calculate_pin_weights(self) -> dict:
        """
        Calculates the pin weights of each membrane the cell.

        Returns:
            dict{str: float}: The pin weights for each membrane of the cell.
                              Keys are "a", "b", "l", and "m".
        """
        return self.circ_mod.pin_weights

    def get_pin_weights(self) -> dict:
        """
        Returns the pin weights of each membrane the cell.

        Returns:
            dict{str: float}: The pin weights for each membrane of the cell.
                              Keys are "a", "b", "l", and "m".
        """
        return self.pin_weights

    def update(self) -> None:
        """
        Updates the cell by growing, calculating pin weights, and updating the circ module.
        """
        if self.growing:
            self.grow()
        self.pin_weights = self.calculate_pin_weights()
        self.circ_mod.update()

    def get_neighbor_di_neighbor_shares_two_vs_std(self, neighbor: "Cell") -> str:
        """
        Returns the direction of a neighbor when the neighbor shares two vertices with the cell
        assuming regular geometry.

        Args:
            neighbor (Cell): The neighbor to find the direction of.

        Returns:
            string: The direction of the neighbor.
        """
        # standard case, check which vertices neighbor shares with self
        # if neighbor shares top left and bottom left, neighbor is to the left
        if (self.quad_perimeter.get_top_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_left() in neighbor.get_quad_perimeter().get_vs()
        ):
            if (
                self.quad_perimeter.get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            else:
                neighbor_direction = "m"
        # if neighbor shares top right and bottom right, neighbor is to the right
        elif (self.quad_perimeter.get_top_right() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            if (
                self.quad_perimeter.get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            else:
                neighbor_direction = "m"
        elif (self.quad_perimeter.get_top_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_top_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            neighbor_direction = "a"
        elif (self.quad_perimeter.get_bottom_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            neighbor_direction = "b"
        return neighbor_direction

    def get_neighbor_dir_neighbor_shares_one_v_std(self, neighbor: "Cell") -> str:
        """
        Returns the direction of a neighbor when the neighbor shares one vertex with the cell
        assuming regular geometry.

        Args:
            neighbor (Cell): The neighbor to find the direction of.

        Returns:
            string: The direction of the neighbor.
        """
        if (
            self.get_quad_perimeter().get_top_left()
            == neighbor.get_quad_perimeter().get_top_right()
        ):
            if (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            elif (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                neighbor_direction = "m"

        elif (
            self.get_quad_perimeter().get_top_right()
            == neighbor.get_quad_perimeter().get_top_left()
        ):
            if (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            elif (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                neighbor_direction = "m"

        elif (
            self.get_quad_perimeter().get_bottom_left()
            == neighbor.get_quad_perimeter().get_bottom_right()
        ):
            if (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            elif (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                neighbor_direction = "m"

        elif (
            self.get_quad_perimeter().get_bottom_right()
            == neighbor.get_quad_perimeter().get_bottom_left()
        ):
            if (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                neighbor_direction = "l"
            elif (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                neighbor_direction = "m"
        elif (
            self.get_quad_perimeter().get_top_left()
            == neighbor.get_quad_perimeter().get_bottom_left()
        ):
            neighbor_direction = "a"
        elif (
            self.get_quad_perimeter().get_top_right()
            == neighbor.get_quad_perimeter().get_bottom_right()
        ):
            neighbor_direction = "a"
        elif (
            self.get_quad_perimeter().get_bottom_left()
            == neighbor.get_quad_perimeter().get_top_left()
        ):
            neighbor_direction = "b"
        elif (
            self.get_quad_perimeter().get_bottom_right()
            == neighbor.get_quad_perimeter().get_top_right()
        ):
            neighbor_direction = "b"
        return neighbor_direction
