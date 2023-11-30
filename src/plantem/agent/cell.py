import arcade
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.circ_module_disc import BaseCirculateModuleDisc
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.loc.vertex.vertex import Vertex

# Growth rate of cells in meristematic zone in um per um per hour from Van den Berg et al. 2018
MERISTEMATIC_GROWTH_RATE = -0.0179

# Growth rate cells in transition zone in um per um per hour from Van den Berg et al. 2018
TRANSITION_GROWTH_RATE = -0.0179

# Growth rate cells in elongation zone in um per um per hour from Van den Berg et al. 2018
ELONGATION_GROWTH_RATE = -0.00112

# Growth rate cells in differentiation zone in um per um per hour from Van den Berg et al. 2018
DIFFERENTIATION_GROWTH_RATE = -0.00112

# um distance from tip at which cells pass from meristeamtic to transition zone from Van den Berg et al. 2018
MERISTEMATIC_MAX_DIST_FROM_TIP = 160

# um distance from tip at which cells pass from transition to elongation zone from Van den Berg et al. 2018
TRANSITION_MAX_DIST_FROM_TIP = 340

# um distance from tip at which cells pass from elongation to differentiation zone from Van den Berg et al. 2018
ELONGATION_MAX_DIST_FROM_TIP = 460

# um distance from tip at which cells leave differentiation zone from Van den Berg et al. 2018
DIFFERENTIATION_MAX_DIST_FROM_TIP = 960


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

    def __init__(self, simulation, corners: list, init_vals: dict, id: int):
        self.id = id
        # print(f"making cell {id}")
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
        self.color = self.get_color()
        self.pin_weights = self.initialize_pin_weights()

    def initialize_pin_weights(self):
        # return a dictionary of pin weights for each direction
        # each weight should be proportional to the initial PIN in each respective direction
        # pin in a direction / sum of pins in all direction
        # NOT unlocalized PIN
        pin_weights_dict = {}
        pina = self.circ_mod.get_apical_pin()
        pinb = self.circ_mod.get_basal_pin()
        pinl = self.circ_mod.get_lateral_pin()
        pinm = self.circ_mod.get_medial_pin()
        pin_vals = [pina, pinb, pinl, pinm]
        pin_sum = pina + pinb + pinl + pinm
        for (val, direction) in zip(pin_vals, ["a", "b", "l", "m"]):
            pin_weights_dict[direction] = val / pin_sum
        return pin_weights_dict

    # Sets color based on self.circ_mod.get_auxin()
    def get_color(self):
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
                #print(f"cell {self.id} and cell {neighbor.id} are not neighbors anymore")
                pass
            elif neighbor_location == None:
                raise ValueError("Non-neighbor added as neighbor")
            else:
                raise ValueError("Non-neighbor added as neighbor")
        else:
            raise ValueError("Neighbor being added twice")

    def find_new_neighbor_relative_location(self, neighbor: "GrowingCell") -> str:
        self_vs = self.get_quad_perimeter().get_vs()
        neighbor_vs = neighbor.get_quad_perimeter().get_vs()
        # if neighbor shares two vertices with self, check which ones
        if len(set(self_vs).intersection(set(neighbor_vs))) == 2:
            return self.get_neighbor_direction_when_neighbor_shares_two_vs(neighbor)
        # if neighbor shares only one vertex with self, check which one
        if len(set(self_vs).intersection(set(neighbor_vs))) == 1:
            return self.get_neighbor_direction_when_neighbor_shares_one_v(neighbor)
        # if neighbor shares no vertices with self, check for very specific edge cases in root tip
        if len(set(self_vs).intersection(set(neighbor_vs))) == 0:
            return self.get_neighbor_direction_when_neighbor_shares_no_vs(neighbor)

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

    def get_neighbor_direction_when_neighbor_shares_one_v(self, neighbor: "GrowingCell") -> str:
        # going to assign these manually for now
        if self.get_id() == 10 and neighbor.get_id() == 20:
            return "a"
        elif self.get_id() == 20 and neighbor.get_id() == 10:
            return "b"

        elif self.get_id() == 11 and neighbor.get_id() == 25:
            return "a"
        elif self.get_id() == 25 and neighbor.get_id() == 11:
            return "b"

        elif self.get_id() == 16 and neighbor.get_id() == 36:
            return "a"
        elif self.get_id() == 36 and neighbor.get_id() == 16:
            return "b"

        elif self.get_id() == 19 and neighbor.get_id() == 37:
            return "a"
        elif self.get_id() == 37 and neighbor.get_id() == 19:
            return "b"

        elif self.get_id() == 20 and neighbor.get_id() == 26:
            return "b"
        elif self.get_id() == 26 and neighbor.get_id() == 20:
            return "l"

        elif self.get_id() == 20 and neighbor.get_id() == 36:
            return "a"
        elif self.get_id() == 36 and neighbor.get_id() == 20:
            return "b"

        elif self.get_id() == 25 and neighbor.get_id() == 27:
            return "b"
        elif self.get_id() == 27 and neighbor.get_id() == 25:
            return "l"

        elif self.get_id() == 25 and neighbor.get_id() == 37:
            return "a"
        elif self.get_id() == 37 and neighbor.get_id() == 25:
            return "b"

        elif self.get_id() == 38 and neighbor.get_id() == 39:
            return "m"
        elif self.get_id() == 39 and neighbor.get_id() == 38:
            return "l"

        elif self.get_id() == 39 and neighbor.get_id() == 46:
            return "l"
        elif self.get_id() == 46 and neighbor.get_id() == 39:
            return "m"

        elif self.get_id() == 42 and neighbor.get_id() == 43:
            return "l"
        elif self.get_id() == 43 and neighbor.get_id() == 42:
            return "m"

        elif self.get_id() == 42 and neighbor.get_id() == 47:
            return "l"
        elif self.get_id() == 47 and neighbor.get_id() == 42:
            return "m"

        elif self.get_id() == 44 and neighbor.get_id() == 50:
            return "m"
        elif self.get_id() == 50 and neighbor.get_id() == 44:
            return "l"

        elif self.get_id() == 45 and neighbor.get_id() == 51:
            return "m"
        elif self.get_id() == 51 and neighbor.get_id() == 45:
            return "l"

        elif self.get_id() == 50 and neighbor.get_id() == 52:
            return "l"
        elif self.get_id() == 52 and neighbor.get_id() == 50:
            return "m"

        elif self.get_id() == 51 and neighbor.get_id() == 59:
            return "l"
        elif self.get_id() == 59 and neighbor.get_id() == 51:
            return "m"

        elif self.get_id() == 54 and neighbor.get_id() == 65:
            return "a"
        elif self.get_id() == 65 and neighbor.get_id() == 54:
            return "b"

        elif self.get_id() == 54 and neighbor.get_id() == 66:
            return "a"
        elif self.get_id() == 66 and neighbor.get_id() == 54:
            return "b"

        elif self.get_id() == 57 and neighbor.get_id() == 69:
            return "a"
        elif self.get_id() == 69 and neighbor.get_id() == 57:
            return "b"

        elif self.get_id() == 57 and neighbor.get_id() == 70:
            return "a"
        elif self.get_id() == 70 and neighbor.get_id() == 57:
            return "b"

        # This catches assignment of neighbor of root cap cells
        rootcap_cellIDs = [60, 90, 120, 136, 166, 210, 296, 75, 105, 135, 151, 181, 225, 311]
        if self.get_id() in rootcap_cellIDs:
            return "m"
        if neighbor.get_id() in rootcap_cellIDs:
            return "l"

        # This catches direction of neighbor sharing one vertex in regular geometry
        if (
            self.get_quad_perimeter().get_top_left()
            == neighbor.get_quad_perimeter().get_top_right()
        ):
            if (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            elif (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                return "m"

        elif (
            self.get_quad_perimeter().get_top_right()
            == neighbor.get_quad_perimeter().get_top_left()
        ):
            if (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            elif (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                return "m"

        elif (
            self.get_quad_perimeter().get_bottom_left()
            == neighbor.get_quad_perimeter().get_bottom_right()
        ):
            if (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            elif (
                self.get_quad_perimeter().get_left_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                return "m"

        elif (
            self.get_quad_perimeter().get_bottom_right()
            == neighbor.get_quad_perimeter().get_bottom_left()
        ):
            if (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "lateral"
            ):
                return "l"
            elif (
                self.get_quad_perimeter().get_right_lateral_or_medial(self.sim.get_root_midpointx())
                == "medial"
            ):
                return "m"

        return None

    def get_neighbor_direction_when_neighbor_shares_no_vs(self, neighbor: "GrowingCell") -> str:
        # This catches explicit edge cases in root tip initialization
        # TODO: Consider manually assigning neighbors for all nongrowing cells
        if self.get_id() == 17 and neighbor.get_id() == 20:
            return "l"
        elif self.get_id() == 20 and neighbor.get_id() == 17:
            return "b"
        elif self.get_id() == 18 and neighbor.get_id() == 25:
            return "l"
        elif self.get_id() == 25 and neighbor.get_id() == 18:
            return "b"

        # This catches assignment of neighbor of root cap cells
        rootcap_cellIDs = [60, 90, 120, 136, 166, 210, 296, 75, 105, 135, 151, 181, 225, 311]
        if self.get_id() in rootcap_cellIDs:
            neighbor_midpointy = neighbor.get_quad_perimeter().get_midpointy()
            if (
                neighbor_midpointy < self.get_quad_perimeter().get_max_y()
                and neighbor_midpointy > self.get_quad_perimeter().get_min_y()
            ):
                return "m"
            else:
                return "cell no longer root cap cell neighbor"
        if neighbor.get_id() in rootcap_cellIDs:
            self_midpointy = self.get_quad_perimeter().get_midpointy()
            if (
                self_midpointy < neighbor.get_quad_perimeter().get_max_y()
                and self_midpointy > neighbor.get_quad_perimeter().get_min_y()
            ):
                return "l"
            else:
                return "cell no longer root cap cell neighbor"
        raise ValueError("Neighbor shares no Vs, is not in root tip, and is not a root cap cell")

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
        self.color = self.get_color()
        point_list = self.quad_perimeter.get_corners_for_disp()
        arcade.draw_polygon_filled(point_list=point_list, color=self.color)
        arcade.draw_polygon_outline(point_list=point_list, color=[0, 0, 0])

    def grow(self) -> None:
        self.sim.get_vertex_mover().add_cell_delta_val(self, self.calculate_delta())

    def get_distance_from_tip(self) -> float:
        root_tip_y = self.sim.get_root_tip_y()
        self_y = self.quad_perimeter.get_bottom_left().get_y()
        return self_y - root_tip_y

    def calculate_dev_zone(self, dist_to_root_tip) -> None:
        if dist_to_root_tip < MERISTEMATIC_MAX_DIST_FROM_TIP:
            self.dev_zone = "meristematic"
        elif dist_to_root_tip < TRANSITION_MAX_DIST_FROM_TIP:
            self.dev_zone = "transition"
        elif dist_to_root_tip < ELONGATION_MAX_DIST_FROM_TIP:
            self.dev_zone = "elongation"
        elif dist_to_root_tip < DIFFERENTIATION_MAX_DIST_FROM_TIP:
            self.dev_zone = "differentiation"

    def get_growth_rate(self) -> float:
        if self.get_quad_perimeter().get_height() >= 250:
            print(f"cell {self.id} has reached max height")
            self.growing = False
            return 0
        if self.dev_zone == "meristematic":
            return MERISTEMATIC_GROWTH_RATE
        elif self.dev_zone == "transition":
            return TRANSITION_GROWTH_RATE
        elif self.dev_zone == "elongation":
            return ELONGATION_GROWTH_RATE
        elif self.dev_zone == "differentiation":
            return DIFFERENTIATION_GROWTH_RATE
        raise ValueError("Cell has no recognizable dev zone")

    def calculate_delta(self) -> float:
        dist_to_root_tip = self.get_distance_from_tip()
        self.calculate_dev_zone(dist_to_root_tip)
        return self.get_growth_rate()

    def calculate_pin_weights(self) -> dict:
        return self.pin_weights

    def update(self) -> None:
        print(f"updating cell {self.id}")
        if self.growing:
            self.grow()
        self.pin_weights = self.calculate_pin_weights() 
        self.circ_mod.update(self.pin_weights)
        #print(f"cell {self.id} auxin: {self.circ_mod.get_auxin()}")
