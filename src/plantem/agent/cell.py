import arcade
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.circ_module_disc import BaseCirculateModuleDisc
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.loc.vertex.vertex import Vertex

# Growth rate of cells in meristematic zone in um per um per hour from Van den Berg et al. 2018
MERISTEMATIC_GROWTH_RATE = -.0179

# Growth rate cells in transition zone in um per um per hour from Van den Berg et al. 2018 
TRANSITION_GROWTH_RATE = -.0179

# Growth rate cells in elongation zone in um per um per hour from Van den Berg et al. 2018 
ELONGATION_GROWTH_RATE = -.00112

# Growth rate cells in differentiation zone in um per um per hour from Van den Berg et al. 2018 
DIFFERENTIATION_GROWTH_RATE = -.00112

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
        super().__init__()
        self.a_neighbors = []
        self.b_neighbors = []
        self.l_neighbors = []
        self.m_neighbors = []
        self.sim = simulation
        simulation.increment_next_cell_id()
        self.quad_perimeter = QuadPerimeter(corners)
        self.color = [0, 200, 5]
        if init_vals.get('circ_mod') == 'disc':
            self.circ_mod = BaseCirculateModuleDisc(self, init_vals)
        else:
            self.circ_mod = BaseCirculateModuleCont(self, init_vals)
        self.growing = init_vals.get('growing')

    def get_quad_perimeter(self):
        return self.quad_perimeter

    def get_id(self):
        return self.id
    
    def get_dev_zone(self):
        return self.dev_zone
    
    def set_dev_zone(self, zone):
        self.dev_zone = zone

    def set_growing(self, growing:bool) -> None:
        self.growing = growing

    def get_growing(self) -> bool:
        return self.growing

    def add_neighbor(self, neighbor: "GrowingCell") -> None:
        print(f"cell {self.id} adding cell {neighbor.id} as neighbor")
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
            else:
                raise ValueError("Non-neighbor added as neighbor")
        else:
            raise ValueError("Neighbor being added twice")

    def find_new_neighbor_relative_location(self, neighbor:"GrowingCell") -> str:
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
        self_top_left = self.quad_perimeter.get_top_left()
        self_bottom_left = self.quad_perimeter.get_bottom_left()
        self_top_right = self.quad_perimeter.get_top_right()
        self_bottom_right = self.quad_perimeter.get_bottom_right()
        neighbor_vs = neighbor.get_quad_perimeter().get_vs()
        # standard case, check which vertices neighbor shares with self
        # if neighbor shares top left and bottom left, neighbor is lateral if sim midpoint to the right, medial otherwise
        if (self_top_left in neighbor_vs) and (self_bottom_left in neighbor_vs):
            if self_top_left.get_x() < self.sim.get_root_midpointx():
                return "l"
            else:
                return "m"
        # if neighbor shares top right and bottom right, neighbor is medial if sim midpoint to the right, lateral otherwise
        elif (self_top_right in neighbor_vs) and (self_bottom_right in neighbor_vs):
            if self_top_right.get_x() < self.sim.get_root_midpointx():
                return "m"
            else:
                return "l"
        # if neighbor shares top left and top right, neighbor is above
        elif (self_top_left in neighbor_vs) and (self_top_right in neighbor_vs):
            return "a"
        # if neighbor shares bottom left and bottom right, neighbor is below
        elif (self_bottom_left in neighbor_vs) and (self_bottom_right in neighbor_vs):
            return "b"   

    def get_neighbor_direction_when_neighbor_shares_one_v(self, neighbor: "GrowingCell") -> str:
        self_top_left = self.quad_perimeter.get_top_left()
        self_bottom_left = self.quad_perimeter.get_bottom_left()
        self_top_right = self.quad_perimeter.get_top_right()
        self_bottom_right = self.quad_perimeter.get_bottom_right()
        neighbor_top_left = neighbor.get_quad_perimeter().get_top_left()
        neighbor_bottom_left = neighbor.get_quad_perimeter().get_bottom_left()
        neighbor_top_right = neighbor.get_quad_perimeter().get_top_right()
        neighbor_bottom_right = neighbor.get_quad_perimeter().get_bottom_right()
        # if self's top right is neighbor's top left, neighbor is medial if sim midpoint to the right, lateral otherwise
        if self_top_right.get_xy() == neighbor_top_left.get_xy():
            if self_top_right.get_x() < self.sim.get_root_midpointx():
                return "m"
            else:
                return "l"
        # if self's bottom right is neighbor's bottom left, neighbor is medial if sim midpoint to the right, lateral otherwise
        elif self_bottom_right.get_xy() == neighbor_bottom_left.get_xy():
            if self_bottom_right.get_x() < self.sim.get_root_midpointx():
                return "m"
            else:
                return "l"
        # if self's top left is neighbor's top right, neighbor is lateral if sim midpoint to the right, medial otherwise
        elif self_top_left.get_xy() == neighbor_top_right.get_xy():
            if self_top_left.get_x() < self.sim.get_root_midpointx():
                return "l"
            else:
                return "m"
        # if self's bottom left is neighbor's bottom right, neighbor is lateral if sim midpoint to the right, medial otherwise
        elif self_bottom_left.get_xy() == neighbor_bottom_right.get_xy():
            if self_bottom_left.get_x() < self.sim.get_root_midpointx():
                return "l"
            else:
                return "m"

        self_top_vs = [self_top_left, self_top_right]
        self_bottom_vs = [self_bottom_left, self_bottom_right]
        neighbor_top_vs = [neighbor_top_left, neighbor_top_right]
        neighbor_bottom_vs = [neighbor_bottom_left, neighbor_bottom_right]

        # if either of self's bottom vs are either neighbor's top vs, neighbor is below
        if (len(set(self_bottom_vs).intersection(set(neighbor_top_vs))) == 1) :
            return "b"
        # if either of self's top vs are either neighbor's bottom vs, neighbor is above
        elif (len(set(self_top_vs).intersection(set(neighbor_bottom_vs))) == 1) :
            return "a"

    def get_neighbor_direction_when_neighbor_shares_no_vs(self, neighbor: "GrowingCell") -> str:
        if self.get_id() == 17 and neighbor.get_id() == 20:
            return "l"
        elif self.get_id() == 20 and neighbor.get_id() == 17:
            return "m"
        elif self.get_id() == 18 and neighbor.get_id() == 25:
            return "m"
        elif self.get_id() == 25 and neighbor.get_id() == 18:
            return "l"

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
            pass
            # raise ValueError("Non neighbor cell being removed from neighbor list")

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
        arcade.draw_polygon_filled(
            point_list=self.quad_perimeter.get_corners_for_disp(), color=self.color
        )
        arcade.draw_polygon_outline(
            point_list=self.quad_perimeter.get_corners_for_disp(), color=[0, 0, 0]
        )

    def grow(self) -> None:
        print(f"cell {self.id} adding delta {self.calculate_delta()} to vertex_mover")
        self.sim.get_vertex_mover().add_cell_delta_val(self, self.calculate_delta())

    def get_distance_from_tip(self) -> float:
        root_tip_y = self.sim.get_root_tip_y()
        self_y = self.quad_perimeter.get_bottom_left().get_y()
        return self_y - root_tip_y
    
    def calculate_dev_zone(self, dist_to_root_tip) -> None:
        if (dist_to_root_tip < MERISTEMATIC_MAX_DIST_FROM_TIP) :
            self.dev_zone = "meristematic"
        elif (dist_to_root_tip < TRANSITION_MAX_DIST_FROM_TIP) :
            self.dev_zone = "transition"
        elif (dist_to_root_tip < ELONGATION_MAX_DIST_FROM_TIP) :
            self.dev_zone = "elongation"
        elif (dist_to_root_tip < DIFFERENTIATION_MAX_DIST_FROM_TIP) :
            self.dev_zone = "differentiation"

    def get_growth_rate(self) -> float:
        if self.get_quad_perimeter().get_height() >= 100:
            growthRate = 0
        if (self.dev_zone == "meristematic"):
            growthRate = MERISTEMATIC_GROWTH_RATE
        elif (self.dev_zone == "transition"):
            growthRate = TRANSITION_GROWTH_RATE
        elif (self.dev_zone == "elongation"):
            growthRate = ELONGATION_GROWTH_RATE
        elif (self.dev_zone == "differentiation"):
            growthRate = DIFFERENTIATION_GROWTH_RATE
        return growthRate

    def calculate_delta(self) -> float:
        dist_to_root_tip = self.get_distance_from_tip()
        self.calculate_dev_zone(dist_to_root_tip)
        return self.get_growth_rate()

    def update(self) -> None:
        print(f"updating cell {self.id}")
        if self.growing:
            self.grow()
        # self.circ_mod.update() TODO: Turn this back on after growth is checked
        #print(f"Cell {self.id} state: {self.circ_mod.get_state()}")
        #print(f"Cell {self.id} auxin = {self.get_circ_mod().get_auxin()}")