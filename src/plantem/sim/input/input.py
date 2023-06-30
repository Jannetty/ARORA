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

    def get_vertex(self) -> dict:
        vertex_dict = dict()
        for index, row in self.vertex_input.iterrows():
            vertex_dict["{0}".format(index)] = row.to_dict()
        # update the vertex_dict to store vertcies in Vertex format
        for each in vertex_dict:
            x = vertex_dict[each]["x"]
            y = vertex_dict[each]["y"]
            vertex_dict[each] = Vertex(x, y)
        return vertex_dict

    def get_init_vals(self) -> dict:
        init_vals_dict = dict()
        for index, row in self.init_vals_input.iloc[:, :15].iterrows():
            init_vals_dict["init_vals_set{0}".format(index)] = row.to_dict()
        return init_vals_dict

    # def get_vertex_assignment(self) -> dict:
    #     vertex_assign = dict()

    def create_cell(self):
        pass

    def update_neighbors(self):
        pass
