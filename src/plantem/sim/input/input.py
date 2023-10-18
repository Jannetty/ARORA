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
        for cell in new_cells.values():
            cell_list.append(cell)

        # update neighbors
        self.update_neighbors(cell_neigbors, new_cells)

    # Helper functions
    def get_vertex(self) -> dict:
        """
        Returns vertices dictionary with index and Vertex object as value
        """
        vertex_dict = {}
        for index, row in self.vertex_input.iterrows():
            vertex_dict[f"{index}"] = row.to_dict()
        # update the vertex_dict to store vertcies in Vertex format
        new_vertex_dict = {}
        for v_num, vertex in vertex_dict.items():
            x = vertex["x"]
            y = vertex["y"]
            new_vertex_dict[v_num] = Vertex(x, y)
        return new_vertex_dict
    
    def replace_default_to_gparam(self, gparam_series: pandas.Series) -> None:
        """
        update the default_init_val dataframe to fit in the value from 
        """
        for index_df, row in self.init_vals_input.iterrows():
            for index_s, value in gparam_series.items():
                if index_s != "tau":
                    self.init_vals_input.at[index_df, index_s] = value
                else:
                    self.init_vals_input.at[index_df, "arr_hist"] = [row["arr"]] * value

    # TODO: make iloc so it isn't using raw number
    # Done
    def get_init_vals(self) -> dict:
        """
        Returns inital values dictionary with cell index as key and its
        init_vals set as value
        """
        init_vals_dict = {}
        init_vals_names = ["auxin", "arr", "al", "pin", "pina", "pinb",
                           "pinl", "pinm", "k1", "k2", "k3", "k4", "k5",
                           "k6", "k_s", "k_d", "arr_hist", "growing",
                           "circ_mod", "vertices", "neighbors"]
        for index, row in self.init_vals_input[init_vals_names].iterrows():
            cell_num = f"c{index}"
            init_vals_dict[cell_num] = row.to_dict()
            for val in init_vals_dict[cell_num]:
                if val in ["arr_hist", "vertices"]:
                    init_vals_dict[cell_num][val] = eval(init_vals_dict[cell_num][val])
                if val == "neighbors":
                    init_vals_dict[cell_num][val] = init_vals_dict[cell_num][val].replace(" ", "").replace("[", "").replace("]", "").split(",")
            # update arr_hist
            init_vals_dict[cell_num]["arr_hist"] = [init_vals_dict[cell_num]["arr"]] * len(init_vals_dict[cell_num]["arr_hist"])
        self.set_arr_hist(init_vals_dict)
        return init_vals_dict

    def set_arr_hist(self, init_vals_dict: dict) -> None:
        """
        Update the arr_hist; change it from string list
        """
        for cell, dict in init_vals_dict.items():
            hist = dict["arr_hist"]
            # hist_list = hist.replace(" ", "").replace("[", "").replace("]", "").split(",")
            # new = []
            # for val in hist_list:
            #     new.append(float(val))
            init_vals_dict[cell]["arr_hist"] = hist

    # TODO: Please make this dynamic so it pulls out the vertex row by something other than its raw col number in the csv
    # Done
    def get_vertex_assignment(self) -> dict:
        """
        Returns vertex assignment dictionary with cell index as key and its
        vertex assignment list as value
        """
        vertex_assign = {}
        for index, row in self.init_vals_input[["vertices"]].iterrows():
            row = row.to_string()[12:].replace(" ", "").replace("[", "").replace("]", "").split(",")
            vertex_assign[f"c{index}"] = row
        return vertex_assign

    #TODO: replace hard coded 13
    #TODO: parse string without iterating through all elements of series (get rid of for loop so we don't give impression we are iterating through anything when we are just extracting)
    def get_neighbors_assignment(self) -> dict:
        """
        Returns neighbors dictionary with cell index as key and its neighbors
        list as value
        """
        neighbors = {}
        for index, row in self.init_vals_input[["neighbors"]].iterrows():
            for elem in row:
                print(f"elem: {elem}")
                print (type(elem))
                row = elem.replace(" ", "").replace("[", "").replace("]", "").split(",")
            if index == 296:
                print(f"row2: {row}")
            neighbors[f"c{index}"] = row
        return neighbors

    def group_vertices(self, vertices: dict, vertex_assignment: dict) -> dict:
        """
        Returns grouping dictionary with cell index as key and its 4 vertices
        list (with Vertex object) as value
        """
        grouping = {}
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
        new_cells = {}
        for cell_num, vertices in vertex_grouping.items():
            new_cells[cell_num] = GrowingCell(
                self.sim, vertices, init_vals[cell_num], self.sim.get_next_cell_id()
            )
        return new_cells

    def get_neighbors(self, new_cells: dict) -> dict:
        """
        Returns neighbors dictionary with cell index as key and its
        correspodning neighbors list (with GrowingCell objects) as value
        """
        neighbors_assignment = self.get_neighbors_assignment()
        #print(f"neighbors_assignment: {neighbors_assignment}")
        neighbors = {}
        for cell_num, neighb in neighbors_assignment.items():
            #print(f"cell_num: {cell_num}")
            #print(f"neighb: {neighb}")
            for each in neighb:
                #print(f"each: {each}")
                if cell_num not in neighbors:
                    neighbors[cell_num] = [new_cells[each]]
                else:
                    neighbors[cell_num].append(new_cells[each])
        return neighbors

    def update_neighbors(self, neighbors: dict, new_cells: dict) -> None:
        """
        For each cell, add its corresponding neighbors
        """
        for cell in neighbors:
            for neighbor in neighbors[cell]:
                new_cells[cell].add_neighbor(neighbor)
