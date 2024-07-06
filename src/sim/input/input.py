from typing import TYPE_CHECKING
import pandas as pd
import numpy as np
import json
from src.loc.vertex.vertex import Vertex
from src.agent.cell import Cell

if TYPE_CHECKING:
    from src.sim.simulation.sim import GrowingSim


class Input:
    """
    Processes input initialization values and vertex information for a simulation.

    This class handles reading and processing initial values and vertex information from
    input files, creating cells based on this information, and updating the simulation
    accordingly.

    Attributes
    ----------
    init_vals_input : DataFrame
        A pandas DataFrame containing the initial cell parameter values.
    vertex_input : DataFrame
        A pandas DataFrame containing the initial locations for vertices.
    initial_v_miny : float
        The minimum y-coordinate among all vertices, used to identify the root tip.
    sim : GrowingSim
        The simulation instance this Input class is associated with.

    Parameters
    ----------
    init_vals_file : str
        The file path to the CSV containing initial cell parameter values.
    vertex_file : str
        The file path to the CSV containing initial locations for vertices.
    sim : GrowingSim
        The simulation instance to which this Input class belongs.
    """

    int_params: list = ["k1", "k2", "k4"]
    float_params: list = ["k3", "k5", "k6", "k_s", "k_d"]

    def __init__(self, init_vals_file: str, vertex_file: str, sim: "GrowingSim"):
        """
        Initializes the Input class by loading initial values and vertex information from JSON files.

        Parameters
        ----------
        init_vals_file : str
            The file path to the JSON containing initial cell parameter values.
        vertex_file : str
            The file path to the JSON containing initial locations for vertices.
        sim : GrowingSim
            The simulation instance to which this Input class belongs.
        """
        self.init_vals_input = self.load_json(init_vals_file)
        for col in self.int_params:
            self.init_vals_input[col] = self.init_vals_input[col].astype("int")
        for col in self.float_params:
            self.init_vals_input[col] = self.init_vals_input[col].astype("float")
        self.vertex_input = self.load_json(vertex_file)
        self.initial_v_miny = float(min(self.vertex_input["y"]))
        self.sim = sim

    def load_json(self, file_path: str) -> pd.DataFrame:
        with open(file_path, "r") as file:
            data = json.load(file)
        return pd.DataFrame(data)

    def get_initial_v_miny(self) -> float:
        """
        Retrieves the minimum y-coordinate of all initial vertices

        Returns
        -------
        float
            The minimum y-coordinate among all vertices in the simulation
            after initialization.
        """
        return self.initial_v_miny

    def make_cells_from_input_files(self) -> None:
        """
        Creates new cells based on input files and updates their neighbors in the simulation.

        This method reads cell and vertex information from input files, creates new Cell instances,
        assigns neighbors to these cells, and updates the simulation's cell list.
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
    def get_vertices_from_input_file(self) -> dict[str, "Vertex"]:
        """
        Extracts vertices from the input file and returns them as a dictionary.

        Returns
        -------
        dict[str, Vertex]
            A dictionary where keys are vertex identifiers (ints as strings) and values are Vertex objects.
        """
        vertex_dict = {}
        for index, row in self.vertex_input.iterrows():
            vertex_dict[index] = row.to_dict()
        # update the vertex_dict to store vertcies in Vertex format
        new_vertex_dict = {}
        for v_num, vertex in vertex_dict.items():
            x = int(vertex["x"])
            y = int(vertex["y"])
            new_vertex_dict[v_num] = Vertex(x, y, int(v_num))
        return new_vertex_dict

    def replace_default_to_gparam(self, gparam_series: pd.Series) -> None:
        """
        Updates default initialization values with specific values from a given pandas Series.

        Parameters
        ----------
        gparam_series : pandas.Series
            A pandas Series containing specific parameters to update in the default initialization values.
        """
        for index_df, row in self.init_vals_input.iterrows():
            for index_s, value in gparam_series.items():
                if index_s in ["k1", "k2", "k3", "k4"]:
                    # print(f"index_s: {index_s}, value: {value}, value type: {type(value)}, value as int: {int(value)}")
                    # print(f"current self.init_vals_input.at[index_df, index_s] = {self.init_vals_input.at[index_df, index_s]}, type: {type(self.init_vals_input.at[index_df, index_s])}")
                    self.init_vals_input.at[index_df, index_s] = int(value)
                if index_s in ["k5", "k6", "k_s", "k_d"]:
                    # print(f"index_s: {index_s}, value: {value}, value type: {type(value)}, value as float: {float(value)}")
                    # print(f"current self.init_vals_input.at[index_df, index_s] = {self.init_vals_input.at[index_df, index_s]}, type: {type(self.init_vals_input.at[index_df, index_s])}")
                    self.init_vals_input.at[index_df, index_s] = float(value)
                if index_s == "tau":
                    self.init_vals_input.at[index_df, "arr_hist"] = [row["arr"]] * int(value)

    def get_init_vals(self) -> dict:
        """
        Extracts initial values for cells from the input JSON and returns them as a dictionary.

        Returns
        -------
        dict
            A dictionary with cell indices as keys and dictionaries of their initial values as values.
        """
        init_vals_dict = {}
        init_vals_data = self.init_vals_input

        # Dynamically get the field names from the JSON data
        init_vals_names = init_vals_data.columns.tolist()

        for index, row in init_vals_data.iterrows():
            cell_num = f"c{index}"
            cell_dict = {}
            for key in init_vals_names:
                cell_dict[key] = init_vals_data.loc[index, key]
            init_vals_dict[cell_num] = cell_dict

            for val in init_vals_dict[cell_num]:
                if val in ["arr_hist", "vertices"]:
                    if isinstance(init_vals_dict[cell_num][val], str):
                        init_vals_dict[cell_num][val] = eval(init_vals_dict[cell_num][val])
                    elif isinstance(init_vals_dict[cell_num][val], list):
                        init_vals_dict[cell_num][val] = init_vals_dict[cell_num][val]
                if val == "neighbors":
                    if isinstance(init_vals_dict[cell_num][val], str):
                        init_vals_dict[cell_num][val] = eval(init_vals_dict[cell_num][val])
                    init_vals_dict[cell_num][val] = [
                        neighbor.strip() for neighbor in init_vals_dict[cell_num][val]
                    ]

            # Setting arr_hist
            init_vals_dict[cell_num]["arr_hist"] = [init_vals_dict[cell_num]["arr"]] * len(
                init_vals_dict[cell_num]["arr_hist"]
            )

        self.set_arr_hist(init_vals_dict)
        return init_vals_dict

    def set_arr_hist(self, init_vals_dict: dict) -> None:
        """
        Updates the arr_hist parameter in the initialization values dictionary.

        Parameters
        ----------
        init_vals_dict : dict
            The dictionary of initial values for each cell, where arr_hist needs to be updated.
        """
        for cell, dict in init_vals_dict.items():
            hist = dict["arr_hist"]
            init_vals_dict[cell]["arr_hist"] = hist

    def get_vertex_assignment(self) -> dict:
        """
        Extracts initial vertex assignments for each cell and returns them as a dictionary.

        Returns
        -------
        dict
            A dictionary with cell indices as keys and lists of assigned vertex identifiers as values.
        """
        vertex_assign = {}
        for index, row in self.init_vals_input.iterrows():
            vertex_assign[f"c{index}"] = self.init_vals_input.iloc[index]["vertices"]
        return vertex_assign

    def get_neighbors_assignment(self) -> dict:
        """
        Extracts initial neighbor assignments for each cell and returns them as a dictionary.

        Returns
        -------
        dict
            A dictionary with cell indices as keys and lists of neighbor cell indices as values.
        """
        neighbors = {}
        for index, row in self.init_vals_input.iterrows():
            neighbors[f"c{index}"] = self.init_vals_input.iloc[index]["neighbors"]
        return neighbors

    def group_vertices(self, vertices: dict, vertex_assignment: dict) -> dict:
        """
        Groups vertices by cell index based on vertex assignments.

        This method organizes vertices into groups associated with each cell as
        described in init_vals_input df

        Parameters
        ----------
        vertices : dict
            A dictionary where keys are vertex identifiers and values are Vertex objects.
        vertex_assignment : dict
            A dictionary with cell indices as keys and lists of assigned vertex identifiers as values.

        Returns
        -------
        dict
            A dictionary with cell indices as keys and lists of Vertex objects (four per cell) as values.
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
        Creates new cells based on vertex groupings and initial values.

        This method generates new Cell objects for each cell index, using grouped vertices and
        initial parameter values defined in input files.

        Returns
        -------
        dict
            A dictionary with int cell indices as keys and the corresponding newly created Cell objects as values.
        """
        all_vs = self.get_vertices_from_input_file()
        vertex_assignment = self.get_vertex_assignment()

        vertex_grouping = self.group_vertices(all_vs, vertex_assignment)
        init_vals = self.get_init_vals()

        # generate new cells
        new_cells = {}
        for cell_num, cell_vs in vertex_grouping.items():
            new_cells[cell_num] = Cell(
                self.sim,
                [v for v in cell_vs],
                init_vals[cell_num],
                self.sim.get_next_cell_id(),
            )
        return new_cells

    def get_neighbors(self, new_cells: dict) -> dict:
        """
        Generates a neighbors dictionary for each new cell based on input files.

        Parameters
        ----------
        new_cells : dict
            A dictionary with cell indices as keys and Cell objects as values, representing newly created cells.

        Returns
        -------
        dict
            A dictionary with cell indices as keys and lists of neighboring Cell objects as values.
        """
        neighbors_assignment = self.get_neighbors_assignment()
        neighbors = {}
        for cell_num, neighb in neighbors_assignment.items():
            for each in neighb:
                if cell_num not in neighbors:
                    neighbors[cell_num] = [new_cells[each]]
                else:
                    neighbors[cell_num].append(new_cells[each])
        return neighbors

    def update_neighbors(self, neighbors: dict, new_cells: dict) -> None:
        """
        Updates each new cell's neighbors list with the appropriate neighboring cells.

        Parameters
        ----------
        neighbors : dict
            A dictionary with cell indices as keys and lists of neighboring Cell objects as values.
        new_cells : dict
            A dictionary with cell indices as keys and newly created Cell objects as values.
        """
        for cell in neighbors:
            for neighbor in neighbors[cell]:
                new_cells[cell].add_neighbor(neighbor)
