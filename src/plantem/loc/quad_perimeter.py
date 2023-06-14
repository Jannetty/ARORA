from loc.vertex import Vertex

class QuadPerimeter():

    perimeter = None

    def __init__(self, vertex_list : list):
        self.perimeter = vertex_list

    def get_corners(self) -> list:
        point_list = []
        for vertex in self.perimeter:
            point_list.append([vertex.x, vertex.y])
        return point_list
    
    def set_corners(self, vertex_list : list):
        self.perimeter = vertex_list