from src.plantem.loc.quad_perimeter.quad_perimeter import get_len_perimeter_in_common

# from src.plantem.agent.cell import GrowingCell


class BaseCirculateModuleDisc:
    """
    Representation of auxin circulation
    """

    auxin = None
    arr = None
    al = None
    pin = None
    pina = None
    pinb = None
    pinl = None
    pinm = None
    cell = None
    left = None
    right = None

    def __init__(self, cell, init_vals: dict):
        """
        initialize all values
        """
        self.cell = cell

        self.init_auxin = init_vals.get("auxin")
        self.auxin = self.init_auxin

        self.init_arr = init_vals.get("arr")
        self.arr = self.init_arr

        self.init_al = init_vals.get("al")
        self.al = self.init_al

        self.init_pin = init_vals.get("pin")
        self.pin = self.init_pin

        self.init_pina = init_vals.get("pina")
        self.pina = self.init_pina

        self.init_pinb = init_vals.get("pinb")
        self.pinb = self.init_pinb

        self.init_pinl = init_vals.get("pinl")
        self.pinl = self.init_pinl

        self.init_pinm = init_vals.get("pinm")
        self.pinm = self.init_pinm

        self.k_arr_arr = init_vals.get("k_arr_arr")
        self.k_auxin_auxlax = init_vals.get("k_auxin_auxlax")
        self.k_auxin_pin = init_vals.get("k_auxin_pin")
        self.k_arr_pin = init_vals.get("k_arr_pin")

        self.ks = init_vals.get("ks")
        self.kd = init_vals.get("kd")

        self.arr_hist = init_vals.get("arr_hist")

        # set medial to either "left" or "right" and lateral to the opposite
        # based on where self.cell.QuadPerimeter.get_midpointx() is in relation
        # to self.cell.sim.root_midpointx
        self.left, self.right = self.determine_left_right()
        self.timestep = 1

    def update(self):
        """
        Update changes to the current and neighbor cells to circulator

        Returns
        -------
        :
            An updated circulator
        """
        # calculates changes in self species and neighbor auxins
        # adds changes to self and neighbors to circulator with key=cell
        # instance value = change in auxin
        # REMEMBER cells will be neighbors and selves multiple times

        curr_cell = self.cell
        cell_dict = curr_cell.sim.circulator.delta_auxins
        area = curr_cell.quad_perimeter.get_area()

        # base calculations
        self.auxin = self.calculate_auxin(self.timestep, self.area)
        self.arr = self.calculate_arr(self.timestep, self.area)
        self.al = self.calculate_aux_lax(self.timestep, self.area)
        self.pina = self.calculate_neighbor_pin(self.init_pina, self.timestep, area)
        self.pinb = self.calculate_neighbor_pin(self.init_pinb, self.timestep, area)
        self.pinl = self.calculate_neighbor_pin(self.init_pinl, self.timestep, area)
        self.pinm = self.calculate_neighbor_pin(self.init_pinm, self.timestep, area)

        # find neighbors
        neighborsa = self.cell.get_a_neighbors()
        neighborsb = self.cell.get_b_neighbors()
        neighborsl = self.cell.get_l_neighbors()
        neighborsm = self.cell.get_m_neighbors()

        # change in auxin relative to current cell
        auxina = self.get_neighbor_auxin(self.init_pina, neighborsa, "a", self.timestep, area)
        auxinb = self.get_neighbor_auxin(self.init_pinb, neighborsb, "b", self.timestep, area)
        auxinl = self.get_neighbor_auxin(self.init_pinl, neighborsl, "l", self.timestep, area)
        auxinm = self.get_neighbor_auxin(self.init_pinm, neighborsm, "m", self.timestep, area)
        neighbors_auxin = [auxina, auxinb, auxinl, auxinm]

        # update current cell
        delta_auxin = self.calculate_delta_auxin(neighbors_auxin)
        cell_dict = self.update_current_cell(curr_cell, cell_dict, delta_auxin)

        # update neighbor cells
        cell_dict = self.update_neighbor_cell(cell_dict, neighbors_auxin)

        # update arr_hist
        self.update_arr_hist()

        return cell_dict

    # Helper functions
    def determine_left_right(self) -> tuple:
        cell = self.cell
        qp = cell.get_quad_perimeter()
        cell_mid = qp.get_midpointx()
        sim = cell.get_sim()
        root_mid = sim.get_root_midpointx()
        if cell_mid < root_mid:
            return ("lateral", "medial")
        elif cell_mid == root_mid:
            return ("lateral", "lateral")
        else:
            return ("medial", "lateral")

    def calculate_auxin(self, timestep: float, area: float) -> float:
        """
        Calcualte the auxin expression of current cell
        """
        auxin = (self.ks - self.kd * self.init_auxin * (1/area)) * timestep
        return auxin

    def calculate_arr(self, timestep: float, area: float) -> float:
        """
        Calculate the ARR expression of current cell
        """
        arr = (
            self.ks * 1 / (self.arr_hist[0] / self.k_arr_arr + 1) - self.kd * self.init_arr * (1/area)
        ) * timestep
        return arr

    def calculate_aux_lax(self, timestep: float, area: float) -> float:
        """
        Calculate the AUX/LAX expression of current cell
        """
        aux_lax = (
            self.ks * (self.auxin / (self.auxin + self.k_auxin_auxlax)) - self.kd *
            self.init_al * (1/area)
        ) * timestep
        return aux_lax

    def calculate_pin(self, timestep: float, area: float) -> float:
        """
        Calculate the PIN expression of current cell
        """
        pin = (
            self.ks * (1 / (self.arr / self.k_arr_pin + 1)) * (self.auxin / (self.auxin + self.k_auxin_pin))
        ) * timestep
        return pin

    def calculate_neighbor_pin(self, init: float, timestep: float, area: float) -> float:
        """
        Calculate the PIN expression of neighbor cells
        """
        neighbor_pin = (0.25 * self.pin - self.kd * init * (1/area)) * timestep
        return neighbor_pin

    def calculate_memfrac(self, neighbor, neighbor_direction: str) -> float:
        """
        Calculate the fraction of total cell membrane that is in a defined direction
        """
        cell_perimeter = self.cell.quad_perimeter.get_perimeter_len()
        common_perimeter = get_len_perimeter_in_common(
            self.cell.quad_perimeter, neighbor.quad_perimeter, neighbor_direction
        )
        memfrac = common_perimeter / cell_perimeter
        return memfrac

    def get_neighbor_auxin(
        self, init_pin: float, neighbors: list, direction: str, timestep: float, area: float
    ) -> dict:
        """
        Calculate the auxin expression of neighbor cells in a defined direction
        """
        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_memfrac(neighbor, direction)
            neighbor_aux = (self.ks * memfrac * self.al - self.kd * init_pin * (1/area)) * timestep
            neighbor_dict[neighbor] = neighbor_aux
        return neighbor_dict

    def calculate_delta_auxin(self, neighbors_auxin: list) -> float:
        """
        Calculate the total amound of change in auxin for current cell
        """
        total_auxin = self.auxin
        for neighbors in neighbors_auxin:
            auxin = sum(neighbors.values())
            total_auxin += auxin
        return total_auxin

    def update_current_cell(self, curr_cell, cell_dict: dict, delta_aux: float) -> dict:
        """
        Update the change in auxin of current cell in the circulator
        """
        if curr_cell not in cell_dict:
            cell_dict[curr_cell] = delta_aux
        else:
            cell_dict[curr_cell] += delta_aux
        return cell_dict

    def update_neighbor_cell(self, cell_dict: dict, neighbors_auxin: list) -> dict:
        """
        Update the change in auxin of neighbor cells in the circulator
        """
        for each_dirct in neighbors_auxin:
            for neighbor in each_dirct:
                if neighbor not in cell_dict:
                    cell_dict[neighbor] = -each_dirct[neighbor]
                else:
                    cell_dict[neighbor] += -each_dirct[neighbor]
        return cell_dict
    
    def update_arr_hist(self) -> None:
        """
        Update the ARR history list
        """
        for i, elem in enumerate(self.arr_hist):
            if i != 0:
                self.arr_hist[i-1] = elem
            if i == (len(self.arr_hist) - 1):
                self.arr_hist[i] = self.arr

    # getter functions
    def get_auxin(self) -> float:
        return self.auxin

    def get_arr(self) -> float:
        return self.arr

    def get_aux_lax(self) -> float:
        return self.al

    def get_apical_pin(self) -> float:
        return self.pina

    def get_basal_pin(self) -> float:
        return self.pinb

    def get_lateral_pin(self) -> float:
        return self.pinl

    def get_medial_pin(self) -> float:
        return self.pinm

    # write getters for all attributes including all pins AND left and right pin
    def get_left_pin(self) -> float:
        # write logic to determine whether to return pinm or pinl
        if self.left == "medial":
            return self.pinm
        else:
            return self.pinl

    def get_right_pin(self) -> float:
        if self.right == "medial":
            return self.pinm
        else:
            return self.pinl
