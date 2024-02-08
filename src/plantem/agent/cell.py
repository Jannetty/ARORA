import arcade
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.circ_module_disc import BaseCirculateModuleDisc
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.default_geo_neighbor_helper import CellNeighborHelpers

# Growth rate of cells in meristematic zone in um per um per hour from Van den Berg et al. 2018
MERISTEMATIC_GROWTH_RATE = -0.0179

# Growth rate cells in transition zone in um per um per hour from Van den Berg et al. 2018
TRANSITION_GROWTH_RATE = -0.0179

# Growth rate cells in elongation zone in um per um per hour from Van den Berg et al. 2018
ELONGATION_GROWTH_RATE = -0.00112

# Growth rate cells in differentiation zone in um per um per hour from Van den Berg et al. 2018
DIFFERENTIATION_GROWTH_RATE = -0.00112

# um Y distance from tip at which cells pass from root tip to meristematic zone, inferred from Van dn Berg et al. 2018
ROOT_TIP_DIST_FROM_TIP = 74

# um Y distance from tip at which cells pass from meristemtic to transition zone from Van den Berg et al. 2018
MERISTEMATIC_MAX_DIST_FROM_TIP = 160

# um Y distance from tip at which cells pass from transition to elongation zone from Van den Berg et al. 2018
TRANSITION_MAX_DIST_FROM_TIP = 340

# um Y distance from tip at which cells pass from elongation to differentiation zone from Van den Berg et al. 2018
ELONGATION_MAX_DIST_FROM_TIP = 460

# um Y distance from tip at which cells leave differentiation zone from Van den Berg et al. 2018
DIFFERENTIATION_MAX_DIST_FROM_TIP = 960

# max um X distance vasc cells can be from self.sim.get_root_midpointx() from Salvi et al. 2020
VASC_CELL_DIST_FROM_ROOT_MIDPOINTX = 12

# max um X distance peri cells can be from self.sim.get_root_midpointx() from Salvi et al. 2020
PERI_CELL_DIST_FROM_ROOT_MIDPOINTX = 17

# max um X distance endo cells can be from self.sim.get_root_midpointx() from Salvi et al. 2020
ENDO_CELL_DIST_FROM_ROOT_MIDPOINTX = 24

# max um X distance cortex cells can be from self.sim.get_root_midpointx() from Salvi et al. 2020
CORTEX_CELL_DIST_FROM_ROOT_MIDPOINTX = 35

# max um X distance epidermis cells can be from self.sim.get_root_midpointx() from Salvi et al. 2020
EPIDERMIS_CELL_DIST_FROM_ROOT_MIDPOINTX = 45


class GrowingCell(arcade.Sprite):
    id = None
    quad_perimeter = None
    circ_mod = None
    sim = None
    a_neighbors = None
    b_neighbors = None
    l_neighbors = None
    m_neighbors = None
    dev_zone = None
    cell_type = None

    def __init__(self, simulation, corners: list, init_vals: dict, id: int):
        self.id = id
        super().__init__()
        self.a_neighbors = []
        self.b_neighbors = []
        self.l_neighbors = []
        self.m_neighbors = []
        self.sim = simulation
        simulation.increment_next_cell_id()
        # Quad perimeter must be made before circ mod
        self.quad_perimeter = QuadPerimeter(corners)
        if init_vals.get("circ_mod") == "disc":
            self.circ_mod = BaseCirculateModuleDisc(self, init_vals)
        else:
            self.circ_mod = BaseCirculateModuleCont(self, init_vals)
        self.growing = init_vals.get("growing")
        self.dev_zone = self.calculate_dev_zone(self.get_distance_from_tip())
        self.cell_type = self.calculate_cell_type()
        self.color = self.calculate_color()

    def calculate_cell_type(self) -> str:
        """Calculates the type of cell based on its x location in relation to center of root

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
        if cell_type == None:
            raise ValueError("Cell type not recognized")
        return cell_type



    # Sets color based on self.circ_mod.get_auxin()
    def calculate_color(self):
        auxin = self.circ_mod.get_auxin()
        max_auxin = 2000  # TODO make this not hard coded
        normalized_auxin = (auxin) / (max_auxin)
        rgba = self.sim.cmap(normalized_auxin)
        # Scale and round the RGB values
        r, g, b = (int(rgba[0] * 255 + 0.5), int(rgba[1] * 255 + 0.5), int(rgba[2] * 255 + 0.5))
        return [r, g, b]

    def get_quad_perimeter(self):
        return self.quad_perimeter

    def get_id(self):
        return self.id

    def get_dev_zone(self):
        return self.dev_zone

    def set_dev_zone(self, zone):
        self.dev_zone = zone

    def set_growing(self, growing: bool) -> None:
        self.growing = growing

    def get_growing(self) -> bool:
        return self.growing

    def add_neighbor(self, neighbor: "GrowingCell") -> None:
        if self.check_if_neighbor(neighbor) == False:
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
            elif neighbor_location == None:
                print(f"cell {self.id} is not neighbors with cell {neighbor.get_id()}")
                raise ValueError("Non-neighbor added as neighbor")
            else:
                raise ValueError("Non-neighbor added as neighbor")
        else:
            raise ValueError("Neighbor being added twice")

    def find_new_neighbor_relative_location(self, neighbor: "GrowingCell") -> str:
        self_vs = self.get_quad_perimeter().get_vs()
        neighbor_vs = neighbor.get_quad_perimeter().get_vs()
        # With default geometry, neighbors sharing fewer than 2 vertices are assigned manually in helper functions
        if len(set(self_vs).intersection(set(neighbor_vs))) == 1 and self.sim.geometry == "default":
            return CellNeighborHelpers.get_neighbor_direction_when_neighbor_shares_one_v_default_geo(self, neighbor)
        if len(set(self_vs).intersection(set(neighbor_vs))) == 0 and self.sim.geometry == "default":
            return CellNeighborHelpers.get_neighbor_direction_when_neighbor_shares_no_vs_default_geo(self, neighbor)
        # Without default geometry, cells can only be neighbors if they share two or one vertices
        if len(set(self_vs).intersection(set(neighbor_vs))) == 2:
            return self.get_neighbor_direction_when_neighbor_shares_two_vs(neighbor)
        if len(set(self_vs).intersection(set(neighbor_vs))) == 1:
            return CellNeighborHelpers.get_neighbor_direction_when_neighbor_shares_one_v(self, neighbor)
        raise ValueError("Neighbor not recognized")

    def get_neighbor_direction_when_neighbor_shares_two_vs(self, neighbor: "GrowingCell") -> str:
        # standard case, check which vertices neighbor shares with self
        # if neighbor shares top left and bottom left, neighbor is to the left
        if (self.quad_perimeter.get_top_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_left() in neighbor.get_quad_perimeter().get_vs()
        ):
            if (
                self.quad_perimeter.get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            else:
                return "m"
        # if neighbor shares top right and bottom right, neighbor is to the right
        elif (self.quad_perimeter.get_top_right() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            if (
                self.quad_perimeter.get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            else:
                return "m"
        elif (self.quad_perimeter.get_top_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_top_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            return "a"
        elif (self.quad_perimeter.get_bottom_left() in neighbor.get_quad_perimeter().get_vs()) and (
            self.quad_perimeter.get_bottom_right() in neighbor.get_quad_perimeter().get_vs()
        ):
            return "b"

    def get_a_neighbors(self):
        return self.a_neighbors

    def get_b_neighbors(self):
        return self.b_neighbors

    def get_m_neighbors(self):
        return self.m_neighbors

    def get_l_neighbors(self):
        return self.l_neighbors

    def get_all_neighbors(self):
        return (
            self.get_a_neighbors()
            + self.get_b_neighbors()
            + self.get_m_neighbors()
            + self.get_l_neighbors()
        )

    def get_sim(self):
        return self.sim

    def get_circ_mod(self):
        return self.circ_mod

    def remove_neighbor(self, cell: "GrowingCell") -> None:
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

    def check_if_neighbor(self, cell: "GrowingCell") -> bool:
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
        return self.quad_perimeter.get_area()

    def get_quad_perimeter(self) -> QuadPerimeter:
        return self.quad_perimeter

    def draw(self) -> None:
        self.color = self.calculate_color()
        point_list = self.quad_perimeter.get_corners_for_disp()
        arcade.draw_polygon_filled(point_list=point_list, color=self.color)
        arcade.draw_polygon_outline(point_list=point_list, color=[0, 0, 0])

    def grow(self) -> None:
        self.sim.get_vertex_mover().add_cell_delta_val(self, self.calculate_delta())

    def get_distance_from_tip(self) -> float:
        root_tip_y = self.sim.get_root_tip_y()
        self_y = self.quad_perimeter.get_midpointy()
        return abs(self_y - root_tip_y)

    def calculate_dev_zone(self, dist_to_root_tip) -> str:
        root_cap_cells = [60,90,120,136,166,210,296,75,105,135,151,181,225,311]
        if self.id in root_cap_cells:
            return "roottip"
        if dist_to_root_tip < ROOT_TIP_DIST_FROM_TIP:
            return "roottip"
        elif dist_to_root_tip < MERISTEMATIC_MAX_DIST_FROM_TIP:
            return "meristematic"
        elif dist_to_root_tip < TRANSITION_MAX_DIST_FROM_TIP:
            return "transition"
        elif dist_to_root_tip < ELONGATION_MAX_DIST_FROM_TIP:
            return "elongation"
        elif dist_to_root_tip < DIFFERENTIATION_MAX_DIST_FROM_TIP:
            return "differentiation"
        else:
            return "differentiation"

    def get_growth_rate(self) -> float:
        if self.get_quad_perimeter().get_height() >= 250:
            print(f"cell {self.id} has reached max height")
            self.growing = False
            return 0
        if self.dev_zone == "roottip":
            return 0
        if self.dev_zone == "meristematic":
            return MERISTEMATIC_GROWTH_RATE
        elif self.dev_zone == "transition":
            return TRANSITION_GROWTH_RATE
        elif self.dev_zone == "elongation":
            return ELONGATION_GROWTH_RATE
        elif self.dev_zone == "differentiation":
            return DIFFERENTIATION_GROWTH_RATE
        print(f"Cell {self.id} distance to root tip = {self.get_distance_from_tip()}")
        raise ValueError("Cell has no recognizable dev zone")

    def calculate_delta(self) -> float:
        dist_to_root_tip = self.get_distance_from_tip()
        self.dev_zone = self.calculate_dev_zone(dist_to_root_tip)
        return self.get_growth_rate()

    def calculate_pin_weights(self) -> dict:
        return self.circ_mod.pin_weights

    def update(self) -> None:
        if self.growing:
            self.grow()
        self.pin_weights = self.calculate_pin_weights() 
        self.circ_mod.update(self.pin_weights)