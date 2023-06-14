from loc.vertex import Vertex

class QuadPerimeter():

    _perimeter = None
    _top_left = None
    _top_right = None
    _bottom_left = None
    _bottom_right = None

    def __init__(self, vertex_list : list):
        self.perimeter = vertex_list
        self.__assign_corners()

    def __assign_corners(self):
        top_row = get_apical(self.perimeter)
        bottom_row = [v for v in self.perimeter if v not in top_row]
        left_col = get_left(self.perimeter)
        right_col = [v for v in self.perimeter if v not in left_col]

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
        for vertex in self.perimeter:
            corners.append(vertex.get_xy())

    def get_corners_for_disp(self)-> list:
        return [self._bottom_right.get_xy(), self._bottom_left.get_xy(), self._top_left.get_xy(), self._top_right.get_xy()]
    
    def set_corners(self, vertex_list : list):
        self.perimeter = vertex_list

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