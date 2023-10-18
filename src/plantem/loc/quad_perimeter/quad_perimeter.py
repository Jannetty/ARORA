from math import dist
from src.plantem.loc.vertex.vertex import Vertex


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
        return dist(self._top_left.get_xy(), self._bottom_left.get_xy())

    def get_right_memlen(self) -> float:
        return dist(self._top_right.get_xy(), self._bottom_right.get_xy())

    def get_apical_memlen(self) -> float:
        return dist(self._top_left.get_xy(), self._top_right.get_xy())

    def get_basal_memlen(self) -> float:
        return dist(self._bottom_left.get_xy(), self._bottom_right.get_xy())

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
        width = self._top_right.get_x() - self._top_left.get_x()
        height = self._top_left.get_y() - self._bottom_left.get_y()
        return width * height

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



def get_len_perimeter_in_common(cellqp, neighborqp, neighbor_direction: str) -> float:
    len = 0
    if neighbor_direction == "l" or neighbor_direction == "m":
        if cellqp.get_top_left().get_x() == neighborqp.get_top_right().get_x():
            # cell shares left membrane with neighbor's right membrane
            len = get_overlap(
                [cellqp.get_top_left().get_y(), cellqp.get_bottom_left().get_y()],
                [neighborqp.get_top_right().get_y(), neighborqp.get_bottom_right().get_y()],
            )
        else:
            # cell shares right membrane with neighbor's left membrane
            len = get_overlap(
                [cellqp.get_top_right().get_y(), cellqp.get_bottom_right().get_y()],
                [neighborqp.get_top_left().get_y(), neighborqp.get_bottom_left().get_y()],
            )
    else:
        if cellqp.get_top_left().get_y() == neighborqp.get_bottom_left().get_y():
            # cell shares top membrane with neighbor's bottom membrane
            len = get_overlap(
                [cellqp.get_top_left().get_x(), cellqp.get_top_right().get_x()],
                [neighborqp.get_bottom_left().get_x(), neighborqp.get_bottom_right().get_x()],
            )
        else:
            # cell shares bottom membrane with neighbor's top membrane
            len = get_overlap(
                [cellqp.get_bottom_left().get_x(), cellqp.get_bottom_right().get_x()],
                [neighborqp.get_top_left().get_x(), neighborqp.get_top_right().get_x()],
            )
    if len == 0:
        raise Exception("Neighbor list is incorrect, neighbor does not share membrane with cell")
    return len


def get_overlap(membrane1, membrane2):
    return max(0, min(max(membrane1), max(membrane2)) - max(min(membrane1), min(membrane2)))


def get_apical(vertex_list: list) -> list:
    vs = vertex_list
    maxy = 0
    apical_v = None
    apical_vs = []
    for v in vs:
        if v.get_y() > maxy:
            maxy = v.get_y()
            apical_v = v
    apical_vs.append(apical_v)
    maxy = 0
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
