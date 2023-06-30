import pandas
from src.plantem.loc.vertex.vertex import Vertex


class Input:
    """
    Process input init_vals and vertex information
    """
    pass

    def __init__(self, init_vals_file: str, vertex_file: str):
        self.init_vals_input = pandas.read_csv(init_vals_file)
        self.vertex_input = pandas.read_csv(vertex_file)

    def get_vertex(self):
        pass

    def get_init_vals(self):
        pass

    def create_cell(self):
        pass

    def update_neighbors(self):
        pass
