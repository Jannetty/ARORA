import csv
import pandas
import numpy as np
import pandas as pd
from src.loc.vertex.vertex import Vertex
from src.agent.cell import Cell
from typing import TYPE_CHECKING
import typing

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

    int_params: list = ["k1", "k2", "k3", "k4"]
    float_params: list = ["k5", "k6", "k_s", "k_d"]

    def __init__(self, init_vals_file: str, vertex_file: str, sim: "GrowingSim"):
        """
        Initializes the Input class by loading initial values and vertex information from CSV files.

        Parameters
        ----------
        init_vals_file : str
            The file path to the CSV containing initial cell parameter values.
        vertex_file : str
            The file path to the CSV containing initial locations for vertices.
        sim : GrowingSim
            The simulation instance to which this Input class belongs.
        """
        self.init_vals_input = pandas.read_csv(init_vals_file)
        self.make_arr_hist_to_list()
        self.make_cell_vertices_to_list()
        self.make_neighbors_to_list()
        self.make_param_to_int()
        self.vertex_file_input = pandas.read_csv(vertex_file)
        self.initial_v_miny = min(self.vertex_file_input["y"])
        self.sim = sim

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
    def get_vertices_from_input_file(self) -> dict[int, "Vertex"]:
        """
        Extracts vertices from the input file and returns them as a dictionary.

        Returns
        -------
        dict[str, Vertex]
            A dictionary where keys are vertex identifiers (ints as strings) and values are Vertex objects.
        """
        vertex_dict = {}
        for index, row in self.vertex_file_input.iterrows():
            v_id = typing.cast(int, index)
            vertex_dict[v_id] = Vertex(row["x"], row["y"], v_id)
        return vertex_dict

    def replace_default_to_gparam(self, gparam_series: pandas.Series) -> None:
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
                    self.init_vals_input.at[index_df, index_s] = int(value)
                if index_s in ["k5", "k6", "k_s", "k_d"]:
                    self.init_vals_input.at[index_df, index_s] = float(value)
                if index_s == "tau":
                    self.init_vals_input.at[index_df, "arr_hist"] = [row["arr"]] * int(value)

    def get_init_vals(self) -> dict:
        """
        Extracts initial values for cells from the input file and returns them as a dictionary.

        Returns
        -------
        dict
            A dictionary with cell indices as keys and dictionaries of their initial values as values.
        """
        init_vals_dict = {}
        init_vals_names = [
            "auxin",
            "arr",
            "al",
            "pin",
            "pina",
            "pinb",
            "pinl",
            "pinm",
            "k1",
            "k2",
            "k3",
            "k4",
            "k5",
            "k6",
            "k_s",
            "k_d",
            "auxin_w",
            "arr_hist",
            "growing",
            "circ_mod",
            "vertices",
            "neighbors",
        ]
        for index, row in self.init_vals_input[init_vals_names].iterrows():
            cell_num = f"c{index}"
            init_vals_dict[cell_num] = row.to_dict()
            for val in init_vals_dict[cell_num]:
                init_vals_dict[cell_num][val] = init_vals_dict[cell_num][val]
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
        for index in range(len(self.init_vals_input["vertices"])):
            vertex_assign[f"c{index}"] = self.init_vals_input["vertices"][index]
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
        for index in range(len(self.init_vals_input["neighbors"])):
            neighbors[f"c{index}"] = self.init_vals_input["neighbors"][index]
        return neighbors

    def group_vertices(self, vertices: dict, cell_vIDlist_mapping: dict) -> dict:
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
        for cell in cell_vIDlist_mapping:
            vertex_list = []
            for vertex in cell_vIDlist_mapping[cell]:
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
        cell_vIDlist_mapping = self.get_vertex_assignment()

        vertex_grouping = self.group_vertices(all_vs, cell_vIDlist_mapping)
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

    def make_arr_hist_to_list(self) -> None:
        """
        Change arr_hist in init_vals from string to list after reading in.
        """
        all_cells_arr_hist_lists = []
        for arr_hist_list in self.init_vals_input["arr_hist"]:
            one_cell_arr_hist_list = (
                arr_hist_list.replace(" ", "").replace("[", "").replace("]", "").split(",")
            )
            for index, arr_val in enumerate(one_cell_arr_hist_list):
                one_cell_arr_hist_list[index] = float(arr_val)
            all_cells_arr_hist_lists.append(one_cell_arr_hist_list)
        self.init_vals_input["arr_hist"] = pd.Series(all_cells_arr_hist_lists)

    def make_cell_vertices_to_list(self) -> None:
        """
        Change vertices in init_vals from string to list after reading in.
        """
        all_cells_v_lists = []
        for v_list in self.init_vals_input["vertices"]:
            one_cell_v_list = v_list.replace(" ", "").replace("[", "").replace("]", "").split(",")
            for index, v in enumerate(one_cell_v_list):
                one_cell_v_list[index] = int(v)
            all_cells_v_lists.append(one_cell_v_list)
        self.init_vals_input["vertices"] = pd.Series(all_cells_v_lists)

    def make_neighbors_to_list(self) -> None:
        """
        Change neighbors in init_vals from string to list after reading in.
        """
        all_cells_neighbors_lists = []
        for neighbor_list in self.init_vals_input["neighbors"]:
            one_cell_neighbors_list = (
                neighbor_list.replace(" ", "").replace("[", "").replace("]", "").split(",")
            )
            all_cells_neighbors_lists.append(one_cell_neighbors_list)
        self.init_vals_input["neighbors"] = pd.Series(all_cells_neighbors_lists)

    def make_param_to_int(self) -> None:
        """
        Change the integer paramters to integer type.
        """
        int_params = ["k1", "k2", "k3", "k4"]
        for param in int_params:
            for index in range(len(param)):
                self.init_vals_input.loc[index, param] = int(self.init_vals_input[param][index])
