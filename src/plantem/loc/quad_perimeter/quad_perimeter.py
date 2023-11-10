import math
from src.plantem.loc.vertex.vertex import Vertex

def intersection(lst1, lst2):
    intersection = [value for value in lst1 if value in lst2]
    return intersection

class QuadPerimeter:
    _perimeter_vs = None  # list of vertices
    _top_left = None
    _top_right = None
    _bottom_left = None
    _bottom_right = None
    _midpointx = None
    _init_area = None

    def __init__(self, vertex_list: list):
        self._perimeter_vs = vertex_list
        self.__assign_corners()
        self.__calc_midpointx()
        self._init_area = self.get_area()

    def __calc_midpointx(self):
        sumx = sum([corner.get_x() for corner in self._perimeter_vs])
        self._midpointx = sumx / len(self._perimeter_vs)

    def __calc_midpointy(self):
        sumy = sum([corner.get_y() for corner in self._perimeter_vs])
        return sumy / len(self._perimeter_vs)
    
    def get_max_y(self):
        return max([corner.get_y() for corner in self._perimeter_vs])
    
    def get_min_y(self):
        return min([corner.get_y() for corner in self._perimeter_vs])

    def get_midpointx(self) -> float:
        return self._midpointx
    
    def get_midpointy(self) -> float:
        return self.__calc_midpointy()

    def get_perimeter_len(self) -> float:
        return (
            self.get_left_memlen()
            + self.get_right_memlen()
            + self.get_apical_memlen()
            + self.get_basal_memlen()
        )

    def get_left_memlen(self) -> float:
        return math.dist(self._top_left.get_xy(), self._bottom_left.get_xy())

    def get_right_memlen(self) -> float:
        return math.dist(self._top_right.get_xy(), self._bottom_right.get_xy())

    def get_apical_memlen(self) -> float:
        return math.dist(self._top_left.get_xy(), self._top_right.get_xy())

    def get_basal_memlen(self) -> float:
        return math.dist(self._bottom_left.get_xy(), self._bottom_right.get_xy())

    def __assign_corners(self) -> None:
        top_row = get_apical(self._perimeter_vs)
        bottom_row = [v for v in self._perimeter_vs if v not in top_row]
        self._top_left = get_left(top_row)
        self._top_right = get_right(top_row)
        self._bottom_left = get_left(bottom_row)
        self._bottom_right = get_right(bottom_row)

    def get_corners_for_disp(self) -> list:
        return [
            self._bottom_right.get_xy(),
            self._bottom_left.get_xy(),
            self._top_left.get_xy(),
            self._top_right.get_xy(),
        ]

    def set_corners(self, vertex_list: list) -> None:
        self._perimeter_vs = vertex_list
        self.__assign_corners()

    def get_top_left(self) -> Vertex:
        return self._top_left

    def get_top_right(self) -> Vertex:
        return self._top_right

    def get_bottom_left(self) -> Vertex:
        return self._bottom_left

    def get_bottom_right(self) -> Vertex:
        return self._bottom_right

    def get_vs(self) -> list:
        return [
            self.get_top_left(),
            self.get_top_right(),
            self.get_bottom_right(),
            self.get_bottom_left(),
        ]

    def get_area(self) -> float:
        # Brahmagupta's formula
        s = self.get_perimeter_len() / 2
        a = math.dist(self._top_left.get_xy(), self._bottom_left.get_xy())
        b = math.dist(self._top_right.get_xy(), self._bottom_right.get_xy())
        c = math.dist(self._top_left.get_xy(), self._top_right.get_xy())
        d = math.dist(self._bottom_left.get_xy(), self._bottom_right.get_xy())
        area = math.sqrt((s - a) * (s - b) * (s - c) * (s - d))
        return area

    def get_init_area(self) -> float:
        return self._init_area
    
    def get_height(self) -> float:
        return self._top_left.get_y() - self._bottom_left.get_y()
    
    def determine_left_right(self, root_mid: float) -> tuple:
        cell_mid = self.get_midpointx()
        if cell_mid < root_mid:
            return ("lateral", "medial")
        elif cell_mid == root_mid:
            return ("lateral", "lateral")
        else:
            return ("medial", "lateral")
        
    def get_left(self, root_mid) -> str:
        return self.determine_left_right(root_mid)[0]
    
    def get_right(self, root_mid) -> str:
        return self.determine_left_right(root_mid)[1]

    def get_memfrac(self, direction: str, left: str) -> float:
        """
        Calculate fraction of total membrane one direction's membrane represents
        """
        cell_perimeter = self.get_perimeter_len()
        if direction == "a":
            return self.get_apical_memlen()/cell_perimeter
        elif direction == "b":
            return self.get_basal_memlen()/cell_perimeter
        elif direction == "l":
            if left == "lateral":
                return self.get_left_memlen()/cell_perimeter
            else:
                return self.get_right_memlen()/cell_perimeter
        elif direction == "m":
            if left == "medial":
                return self.get_left_memlen()/cell_perimeter
            else:
                return self.get_right_memlen()/cell_perimeter



def get_len_perimeter_in_common(cell, neighbor) -> float:
    #TODO: rewrite this function with two possibilities
    # 1. cells share two vertices with neighbor
    #        - find which two vertices, calculate euclidean distance between them, return that
    # 2. cells share one or fewer vertices with neighbor (if neighbor is lateral root cap cell, can check by cell number)
    #        - calculate length of lateral membrane and return that if lateral root cap neighbor, calculate neighbor's lateral membrane if lateral root cap cell
    length = 0
    rootcap_cellIDs = [60,90,120,136,166,210,296,75,105,135,151,181,225,311]
    cellqp = cell.get_quad_perimeter()
    neighborqp = neighbor.get_quad_perimeter()
    # if cellqp and neighborqp share two vertices, calculate euclidean distance between them
    cell_vs = cellqp.get_vs()
    neighbor_vs = neighborqp.get_vs()
    if len(intersection(cell_vs, neighbor_vs)) == 2:
        vs = list(set(cellqp.get_vs()).intersection(set(neighborqp.get_vs())))
        length = math.dist(vs[0].get_xy(), vs[1].get_xy())
    
    # cases for lateral root cap cells
    elif cell.get_id() in rootcap_cellIDs:
        if neighborqp.get_left(neighbor.get_sim().get_root_midpointx()) == "lateral":
            length = neighborqp.get_left_memlen()
        elif neighborqp.get_right(neighbor.get_sim().get_root_midpointx()) == "lateral":
            length = neighborqp.get_right_memlen()
            
    elif neighbor.get_id() in rootcap_cellIDs:
        if cellqp.get_left(neighbor.get_sim().get_root_midpointx()) == "lateral":
            length = cellqp.get_left_memlen()
        elif cellqp.get_right(neighbor.get_sim().get_root_midpointx()) == "lateral":
            length = cellqp.get_right_memlen()


    # cases for unusual geometry in roottip
    elif cell.get_id() == 10 and neighbor.get_id() == 20:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_id() == 20 and neighbor.get_id() == 10:
        length = neighbor.get_quad_perimeter().get_apical_memlen()
        
    elif cell.get_id() == 11 and neighbor.get_id() == 25:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_id() == 25 and neighbor.get_id() == 11:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_id() == 16 and neighbor.get_id() == 36:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_id() == 36 and neighbor.get_id() == 16:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_id() == 17 and neighbor.get_id() == 20:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_id() == 20 and neighbor.get_id() == 17:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_id() == 18 and neighbor.get_id() == 25:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_id() == 25 and neighbor.get_id() == 18:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_id() == 19 and neighbor.get_id() == 37:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_id() == 37 and neighbor.get_id() == 19:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_id() == 26 and neighbor.get_id() == 20:
        length = cell.get_quad_perimeter().get_left_memlen()
    elif cell.get_id() == 20 and neighbor.get_id() == 26:
        length = neighbor.get_quad_perimeter().get_left_memlen()
    
    elif cell.get_id() == 20 and neighbor.get_id() == 36:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_id() == 36 and neighbor.get_id() == 20:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_id() == 25 and neighbor.get_id() == 27:
        length = neighbor.get_quad_perimeter().get_right_memlen()
    elif cell.get_id() == 27 and neighbor.get_id() == 25:
        length = cell.get_quad_perimeter().get_right_memlen()

    elif cell.get_id() == 25 and neighbor.get_id() == 37:
        length = cell.get_quad_perimeter().get_apical_memlen()
    elif cell.get_id() == 37 and neighbor.get_id() == 25:
        length = neighbor.get_quad_perimeter().get_apical_memlen()

    elif cell.get_id() == 38 and neighbor.get_id() == 39:
        length = cell.get_quad_perimeter().get_right_memlen()
    elif cell.get_id() == 39 and neighbor.get_id() == 38:
        length = neighbor.get_quad_perimeter().get_right_memlen()

    elif cell.get_id() == 39 and neighbor.get_id() == 46:
        length = neighbor.get_quad_perimeter().get_right_memlen()
    elif cell.get_id() == 46 and neighbor.get_id() == 39:
        length = cell.get_quad_perimeter().get_right_memlen()

    elif cell.get_id() == 42 and neighbor.get_id() == 43:
        length = neighbor.get_quad_perimeter().get_left_memlen()
        if length != math.sqrt(10):
            raise Exception("cell 42 neighbor 43 wrong")
    elif cell.get_id() == 43 and neighbor.get_id() == 42:
        length = cell.get_quad_perimeter().get_left_memlen()
        if length != math.sqrt(10):
            raise Exception("cell 43 neighbor 42 wrong")

    elif cell.get_id() == 42 and neighbor.get_id() == 47:
        length = neighbor.get_quad_perimeter().get_left_memlen()
        if length != 5:
            raise Exception("cell 42 neighbor 47 wrong")
    elif cell.get_id() == 47 and neighbor.get_id() == 42:
        length = cell.get_quad_perimeter().get_left_memlen()
        if length != 5:
            raise Exception("cell 47 neighbor 42 wrong")

    elif cell.get_id() == 44 and neighbor.get_id() == 50:
        length = cell.get_quad_perimeter().get_right_memlen()
        if length != math.sqrt(74):
            raise Exception("cell 44 neighbor 50 wrong")
    elif cell.get_id() == 50 and neighbor.get_id() == 44:
        length = neighbor.get_quad_perimeter().get_right_memlen()
        if length != math.sqrt(74):
            raise Exception("cell 50 neighbor 44 wrong")

    elif cell.get_id() == 45 and neighbor.get_id() == 51:
        length = cell.get_quad_perimeter().get_left_memlen()
        if length != math.sqrt(74):
            raise Exception("cell 45 neighbor 51 wrong")
    elif cell.get_id() == 51 and neighbor.get_id() == 45:
        length = neighbor.get_quad_perimeter().get_left_memlen()
        if length != math.sqrt(74):
            raise Exception("cell 51 neighbor 45 wrong")

    elif cell.get_id() == 52 and neighbor.get_id() == 50:
        length = cell.get_quad_perimeter().get_right_memlen()
        if length != math.sqrt(5):
            raise Exception("cell 52 neighbor 50 wrong")
    elif cell.get_id() == 50 and neighbor.get_id() == 52:
        length = neighbor.get_quad_perimeter().get_right_memlen()
        if length != math.sqrt(5):
            raise Exception("cell 50 neighbor 52 wrong")

    elif cell.get_id() == 51 and neighbor.get_id() == 59:
        length = neighbor.get_quad_perimeter().get_left_memlen()
        if length != math.sqrt(5):
            raise Exception("cell 52 neighbor 50 wrong")
    elif cell.get_id() == 59 and neighbor.get_id() == 51:
        length = cell.get_quad_perimeter().get_left_memlen()
        if length != math.sqrt(5):
            raise Exception("cell 50 neighbor 52 wrong")

    elif cell.get_id() == 54 and neighbor.get_id() == 65:
        length = neighbor.get_quad_perimeter().get_apical_memlen()
        if length != 4:
            raise Exception("cell 54 neighbor 65 wrong")
    elif cell.get_id() == 65 and neighbor.get_id() == 54:
        length = cell.get_quad_perimeter().get_apical_memlen()
        if length != 4:
            raise Exception("cell 65 neighbor 54 wrong")

    elif cell.get_id() == 54 and neighbor.get_id() == 66:
        length = neighbor.get_quad_perimeter().get_apical_memlen()
        if length != 4:
            raise Exception("cell 54 neighbor 66 wrong")
    elif cell.get_id() == 66 and neighbor.get_id() == 54:
        length = cell.get_quad_perimeter().get_apical_memlen()
        if length != 4:
            raise Exception("cell 66 neighbor 54 wrong")

    elif cell.get_id() == 57 and neighbor.get_id() == 69:
        length = neighbor.get_quad_perimeter().get_apical_memlen()
        if length != 4:
            raise Exception("cell 57 neighbor 69 wrong")
    elif cell.get_id() == 69 and neighbor.get_id() == 57:
        length = cell.get_quad_perimeter().get_apical_memlen()
        if length != 4:
            raise Exception("cell 69 neighbor 57 wrong")

    elif cell.get_id() == 57 and neighbor.get_id() == 70:
        length = neighbor.get_quad_perimeter().get_apical_memlen()
        if length != 4:
            raise Exception("cell 57 neighbor 70 wrong")
    elif cell.get_id() == 70 and neighbor.get_id() == 57:
        length = cell.get_quad_perimeter().get_apical_memlen()
        if length != 4:
            raise Exception("cell 70 neighbor 57 wrong")

    if length == 0:
        raise Exception("Neighbor list is incorrect, neighbor does not share membrane with cell")
    return length


def get_overlap(membrane1, membrane2):
    return max(0, min(max(membrane1), max(membrane2)) - max(min(membrane1), min(membrane2)))


def get_apical(vertex_list: list) -> list:
    vs = vertex_list
    maxy = float('-inf')
    apical_v = None
    apical_vs = []
    for v in vs:
        if v.get_y() > maxy:
            maxy = v.get_y()
            apical_v = v
    apical_vs.append(apical_v)
    maxy = float('-inf')
    for v in vs:
        if v.get_y() > maxy and v not in apical_vs:
            maxy = v.get_y()
            apical_v = v
    apical_vs.append(apical_v)
    return apical_vs


def get_basal(vertex_list: list) -> list:
    apical = get_apical(vertex_list)
    return [v for v in vertex_list if v not in apical]


def get_left(vertex_list: list) -> Vertex:
    vs = vertex_list
    minx = float('inf')
    left_v = None
    for v in vs:
        if v.get_x() < minx:
            minx = v.get_x()
            left_v = v
    return left_v


def get_right(vertex_list: list) -> Vertex:
    left = get_left(vertex_list)
    right = None
    for v in vertex_list:
        if v is not left:
            right = v
    return right
