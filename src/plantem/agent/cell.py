import arcade
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.loc.vertex.vertex import Vertex


class GrowingCell(arcade.Sprite):
    quad_perimeter = None
    circ_mod = None
    sim = None
    a_neighbors = None
    b_neighbors = None
    l_neighbors = None
    m_neighbors = None

    def __init__(self, simulation, corners: list, init_vals):
        super().__init__()
        self.a_neighbors = []
        self.b_neighbors = []
        self.l_neighbors = []
        self.m_neighbors = []
        self.sim = simulation
        self.quad_perimeter = QuadPerimeter(corners)
        self.color = [0, 200, 5]
        self.circ_mod = BaseCirculateModuleCont(self, init_vals)

    def get_quad_perimeter(self):
        return self.quad_perimeter

    def add_neighbor(self, cell: "GrowingCell") -> None:
        if self.check_if_neighbor(cell) == False:
            neighbor_location = self.find_new_neighbor_relative_location(cell)
            if neighbor_location == "a":
                self.a_neighbors.append(cell)
            elif neighbor_location == "b":
                self.b_neighbors.append(cell)
            elif neighbor_location == "l":
                self.l_neighbors.append(cell)
            elif neighbor_location == "m":
                self.m_neighbors.append(cell)
            else:
                raise ValueError("Neighbor direction incorrectly found")
        else:
            raise ValueError("Neighbor being added twice")

    def find_new_neighbor_relative_location(self, cell: "GrowingCell") -> str:
        if self.quad_perimeter.get_midpointx() == cell.quad_perimeter.get_midpointx():
            return self.find_apical_or_basal(cell)
        else:
            return self.find_lateral_or_medial(cell)

    def find_apical_or_basal(self, cell: "GrowingCell") -> str:
        if self.quad_perimeter.get_top_left().get_y() < cell.quad_perimeter.get_top_left().get_y():
            return "a"
        else:
            return "b"

    def find_lateral_or_medial(self, cell: "GrowingCell") -> str:
        sim_midpointx = self.sim.get_root_midpointx()
        if self.quad_perimeter.get_midpointx() < sim_midpointx:
            # cell is left of midpoint
            if self.quad_perimeter.get_midpointx() < cell.quad_perimeter.get_midpointx():
                return "m"
            else:
                return "l"
        elif self.quad_perimeter.get_midpointx() > sim_midpointx:
            # cell is right of midpoint
            if self.quad_perimeter.get_midpointx() < cell.quad_perimeter.get_midpointx():
                return "l"
            else:
                return "m"
        elif self.quad_perimeter.get_midpointx() == sim_midpointx:
            # cell is over midpoint
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
        return self.get_a_neighbors() + self.get_b_neighbors() + self.get_m_neighbors() + self.get_l_neighbors()

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
            #raise ValueError("Non neighbor cell being removed from neighbor list")

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
        self.sim.get_vertex_mover().add_cell_delta_val(self, self.calculate_delta())

    def calculate_delta(self) -> float:
        return -0.5

    def update(self) -> None:
        self.grow()

class NonGrowingCell(arcade.Sprite):
    quad_perimeter = None
    circ_mod = None
    sim = None
    a_neighbors = None
    b_neighbors = None
    l_neighbors = None
    m_neighbors = None

    def __init__(self, simulation, corners: list, init_vals):
        super().__init__()
        self.a_neighbors = []
        self.b_neighbors = []
        self.l_neighbors = []
        self.m_neighbors = []
        self.sim = simulation
        self.quad_perimeter = QuadPerimeter(corners)
        self.color = [0, 200, 5]
        self.circ_mod = BaseCirculateModuleCont(self, init_vals)

    def get_quad_perimeter(self):
        return self.quad_perimeter

    def add_neighbor(self, cell: "GrowingCell") -> None:
        if self.check_if_neighbor(cell) == False:
            neighbor_location = self.find_new_neighbor_relative_location(cell)
            if neighbor_location == "a":
                self.a_neighbors.append(cell)
            elif neighbor_location == "b":
                self.b_neighbors.append(cell)
            elif neighbor_location == "l":
                self.l_neighbors.append(cell)
            elif neighbor_location == "m":
                self.m_neighbors.append(cell)
            else:
                raise ValueError("Neighbor direction incorrectly found")
        else:
            raise ValueError("Neighbor being added twice")

    def find_new_neighbor_relative_location(self, cell: "GrowingCell") -> str:
        if self.quad_perimeter.get_midpointx() == cell.quad_perimeter.get_midpointx():
            return self.find_apical_or_basal(cell)
        else:
            return self.find_lateral_or_medial(cell)

    def find_apical_or_basal(self, cell: "GrowingCell") -> str:
        if self.quad_perimeter.get_top_left().get_y() < cell.quad_perimeter.get_top_left().get_y():
            return "a"
        else:
            return "b"

    def find_lateral_or_medial(self, cell: "GrowingCell") -> str:
        sim_midpointx = self.sim.get_root_midpointx()
        if self.quad_perimeter.get_midpointx() < sim_midpointx:
            # cell is left of midpoint
            if self.quad_perimeter.get_midpointx() < cell.quad_perimeter.get_midpointx():
                return "m"
            else:
                return "l"
        elif self.quad_perimeter.get_midpointx() > sim_midpointx:
            # cell is right of midpoint
            if self.quad_perimeter.get_midpointx() < cell.quad_perimeter.get_midpointx():
                return "l"
            else:
                return "m"
        elif self.quad_perimeter.get_midpointx() == sim_midpointx:
            # cell is over midpoint
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
        return self.get_a_neighbors() + self.get_b_neighbors() + self.get_m_neighbors() + self.get_l_neighbors()

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
        arcade.draw_polygon_filled(
            point_list=self.quad_perimeter.get_corners_for_disp(), color=self.color
        )
        arcade.draw_polygon_outline(
            point_list=self.quad_perimeter.get_corners_for_disp(), color=[0, 0, 0]
        )

    def circulate(self) -> None:
        self.circ_mod.update()

    def update(self) -> None:
        self.circulate()