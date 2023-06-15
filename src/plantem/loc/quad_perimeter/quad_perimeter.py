from math import dist
from src.plantem.loc.vertex.vertex import Vertex

class QuadPerimeter():

    _perimeter_vs = None # list of vertices
    _top_left = None
    _top_right = None
    _bottom_left = None
    _bottom_right = None
    _midpointx = None

    def __init__(self, vertex_list : list):
        self._perimeter_vs = vertex_list
        self.__assign_corners()
        self.__calc_midpointx()
    
    def __calc_midpointx(self):
        sumx = sum([corner.get_x() for corner in self._perimeter_vs])
        return sumx/len(self._perimeter_vs)
    
    def get_midpointx(self) -> float:
        return self._midpointx
    
    def get_perimeter_len(self):
        return dist(self._top_left.get_xy(), self._top_right.get_xy())+\
            dist(self._top_right.get_xy(), self._bottom_right.get_xy())+\
            dist(self._bottom_right.get_xy(), self._bottom_left.get_xy())+\
            dist(self._bottom_left.get_xy(), self._top_left.get_xy())


    def __assign_corners(self) -> None:
        top_row = get_apical(self._perimeter_vs)
        bottom_row = [v for v in self._perimeter_vs if v not in top_row]
        left_col = get_left(self._perimeter_vs)
        right_col = [v for v in self._perimeter_vs if v not in left_col]

        top_left = [v for v in top_row if v in left_col]
        self._top_left = top_left[0]
        top_right = [v for v in top_row if v in right_col]
        self._top_right = top_right[0]
        bottom_left = [v for v in bottom_row if v in left_col]
        self._bottom_left = bottom_left[0]
        bottom_right = [v for v in bottom_row if v in right_col]
        self._bottom_right = bottom_right[0]


    def get_corners(self) -> list:
        corners = []
        for vertex in self._perimeter_vs:
            corners.append(vertex.get_xy())

    def get_corners_for_disp(self)-> list:
        return [self._bottom_right.get_xy(), self._bottom_left.get_xy(), self._top_left.get_xy(), self._top_right.get_xy()]
    
    def set_corners(self, vertex_list : list) -> None:
        self.perimeter_vs = vertex_list
        self.__assign_corners()

    def get_top_left(self) -> Vertex:
        return self._top_left
    def get_top_right(self) -> Vertex:
        return self._top_right
    def get_bottom_left(self) -> Vertex:
        return self._bottom_left
    def get_bottom_right(self) -> Vertex:
        return self._bottom_right
    
    def get_area(self) -> float:
        width = (self.top_right.get_x() - self.top_left.get_x())
        height = (self.top_left.get_y() - self.bottom_left.get_y())
        return (width*height)


def get_len_perimeter_in_common(cell1, cell2):
    # calculates and returns length of perimeter two cells have in common
    return 5

def get_apical(vertex_list : list)-> list:
    yvals = []
    for v in vertex_list:
        yvals.append(v.get_y())
    maxy = max(yvals)
    apical_vs = [v for v in vertex_list if v.get_y() == maxy]
    return apical_vs

def get_basal(vertex_list : list)-> list:
    apical = get_apical(vertex_list)
    return [v for v in vertex_list if v not in apical]

def get_left(vertex_list : list)-> list:
    xvals = []
    for v in vertex_list:
        xvals.append(v.get_x())
    minx = min(xvals)
    left_vs = [v for v in vertex_list if v.get_x() == minx]
    return left_vs

def get_right(vertex_list : list)-> list:
    left = get_left(vertex_list)
    return [v for v in vertex_list if v not in left]