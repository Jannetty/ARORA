import pandas
import csv
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.cell import GrowingCell


class Input:
    """
    Process input init_vals and vertex information
    """

    def __init__(self, init_vals_file: str, vertex_file: str, sim):
        self.init_vals_input = pandas.read_csv(init_vals_file)
        self.vertex_input = pandas.read_csv(vertex_file)    
        self.sim = sim

    def input(self) -> None:
        """
        Add new cells to the cell_list and update their neighbors
        """
        cell_list = self.sim.get_cell_list()
        new_cells = self.create_cells()
        cell_neigbors = self.get_neighbors(new_cells)

        # add new cells to the cell_list
        for cell in new_cells:
            cell_list.append(new_cells[cell])

        # update neighbors
        self.update_neighbors(cell_neigbors, new_cells)

    # Helper functions
    def get_vertex(self) -> dict:
        """
        Returns vertices dictionary with index and Vertex object as value
        """
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
        """
        Returns inital values dictionary with cell index as key and its
        init_vals set as value
        """
        init_vals_dict = dict()
        for index, row in self.init_vals_input.iloc[:, :15].iterrows():
            init_vals_dict["c{0}".format(index)] = row.to_dict()
        return init_vals_dict
        #return self.set_arr_hist(init_vals_dict)
    
    #def set_arr_hist(self, init_vals_dict):
    #    init_vals_dict_cpy = init_vals_dict.copy()
    #    for cell in init_vals_dict:
    #        for hist in init_vals_dict[cell].get("arr_hist"):
    #            print("here")
    #            print(init_vals_dict[cell].get("arr_hist"))
    #            init_vals_dict_cpy[cell]["arr_hist"] = hist.replace(" ", "").replace("[", "").replace("]", "").split(",")
    #            #print(hist.replace(" ", "").replace("[", "").replace("]", "").split(","))
    #            #print(init_vals_dict_cpy[cell]["arr_hist"])
    #    return init_vals_dict

    def get_vertex_assignment(self) -> dict:
        """
        Returns vertex assignment dictionary with cell index as key and its
        vertex assignment list as value
        """
        vertex_assign = dict()
        for index, row in self.init_vals_input.iloc[:, 15:16].iterrows():
            row = row.to_string()[12:].replace(" ", "").replace("[", "").replace("]", "").split(",")
            vertex_assign["c{0}".format(index)] = row
        return vertex_assign

    def get_neighbors_assignment(self) -> dict:
        """
        Returns neighbors dictionary with cell index as key and its neighbors
        list as value
        """
        neighbors = dict()
        for index, row in self.init_vals_input.iloc[:, 16:].iterrows():
            row = row.to_string()[13:].replace(" ", "").replace("[", "").replace("]", "").split(",")
            neighbors["c{0}".format(index)] = row
        return neighbors

    def group_vertices(self, vertices: dict, vertex_assignment: dict) -> dict:
        """
        Returns grouping dictionary with cell index as key and its 4 vertices
        list (with Vertex object) as value
        """
        grouping = dict()
        for cell in vertex_assignment:
            vertex_list = []
            for vertex in vertex_assignment[cell]:
                if vertex in vertices:
                    vertex_list.append(vertices[vertex])
            grouping[cell] = vertex_list
        return grouping

    def create_cells(self) -> dict:
        """
        Returns newly made cells dictionary with cell index as key and its
        corresponding GrowingCell object as value
        """
        vertices = self.get_vertex()
        vertex_assignment = self.get_vertex_assignment()

        vertex_grouping = self.group_vertices(vertices, vertex_assignment)
        init_vals = self.get_init_vals()

        # generate new cells
        new_cells = dict()
        for cell in vertex_grouping:
            new_cells[cell] = GrowingCell(
                self.sim, vertex_grouping[cell], init_vals[cell], self.sim.get_next_cell_id()
            )
        return new_cells

    def get_neighbors(self, new_cells: dict) -> dict:
        """
        Returns neighbors dictionary with cell index as key and its
        correspodning neighbors list (with GrowingCell objects) as value
        """
        neighbors_assignment = self.get_neighbors_assignment()
        neighbors = dict()
        for cell in neighbors_assignment:
            for index in range(len(neighbors_assignment[cell])):
                if cell not in neighbors:
                    neighbors[cell] = [new_cells[neighbors_assignment[cell][index]]]
                else:
                    neighbors[cell].append(new_cells[neighbors_assignment[cell][index]])
        return neighbors

    def update_neighbors(self, neighbors: dict, new_cells: dict) -> None:
        """
        For each cell, add its corresponding neighbors
        """
        for cell in neighbors:
            for neighbor in neighbors[cell]:
                new_cells[cell].add_neighbor(neighbor)
