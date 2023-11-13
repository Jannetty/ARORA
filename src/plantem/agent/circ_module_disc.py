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

        self.k_arr_arr = init_vals.get("k1")
        self.k_auxin_auxlax = init_vals.get("k2")
        self.k_auxin_pin = init_vals.get("k3")
        self.k_arr_pin = init_vals.get("k4")
        self.k_al = init_vals.get("k5")
        self.k_pin = init_vals.get("k6")

        self.ks = init_vals.get("k_s")
        self.kd = init_vals.get("k_d")

        self.arr_hist = init_vals.get("arr_hist")

        # set medial to either "left" or "right" and lateral to the opposite
        # based on where self.cell.QuadPerimeter.get_midpointx() is in relation
        # to self.cell.sim.root_midpointx
        self.left, self.right = self.determine_left_right()
        self.timestep = 1

    def update(self) -> None:
        """
        Update changes to the current and neighbor cells to circulator
        """
        # calculates changes in self species and neighbor auxins
        # adds changes to self and neighbors to circulator with key=cell
        # instance value = change in auxin
        # REMEMBER cells will be neighbors and selves multiple times

        curr_cell = self.cell
        sim_circ = curr_cell.get_sim().get_circulator()
        area = curr_cell.quad_perimeter.get_area()

        # base calculations
        syn_deg_auxin = self.calculate_auxin(self.timestep, area)
        self.arr = self.calculate_arr(self.timestep, area)
        self.al = self.calculate_aux_lax(self.timestep, area)
        self.pina = self.calculate_membrane_pin(self.pina, self.timestep, area)
        self.pinb = self.calculate_membrane_pin(self.pinb, self.timestep, area)
        self.pinl = self.calculate_membrane_pin(self.pinl, self.timestep, area)
        self.pinm = self.calculate_membrane_pin(self.pinm, self.timestep, area)

        # find neighbors
        neighborsa, neighborsb, neighborsl, neighborsm = self.get_neighbors()

        # change in auxin relative to current cell
        auxina = self.get_neighbor_auxin_exchange(self.pina, neighborsa, "a", self.timestep, area)
        auxinb = self.get_neighbor_auxin_exchange(self.pinb, neighborsb, "b", self.timestep, area)
        auxinl = self.get_neighbor_auxin_exchange(self.pinl, neighborsl, "l", self.timestep, area)
        auxinm = self.get_neighbor_auxin_exchange(self.pinm, neighborsm, "m", self.timestep, area)
        neighbors_auxin = [auxina, auxinb, auxinl, auxinm]

        # update current cell
        delta_auxin = self.calculate_delta_auxin(syn_deg_auxin, neighbors_auxin)
        sim_circ.add_delta(curr_cell, delta_auxin)

        # update neighbor cells
        self.update_neighbor_auxin(sim_circ, neighbors_auxin)

        # update arr_hist
        self.update_arr_hist()

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
        auxin = (self.ks - self.kd * self.auxin * (1 / area)) * timestep
        return auxin

    def calculate_arr(self, timestep: float, area: float) -> float:
        """
        Calculate the ARR expression of current cell
        """
        arr = (
            self.ks * 1 / (self.arr_hist[0] / self.k_arr_arr + 1)
            - self.kd * self.init_arr * (1 / area)
        ) * timestep
        return arr

    def calculate_aux_lax(self, timestep: float, area: float) -> float:
        """
        Calculate the AUX/LAX expression of current cell
        """
        aux_lax = (
            self.ks * (self.init_auxin / (self.init_auxin + self.k_auxin_auxlax))
            - self.kd * self.init_al * (1 / area)
        ) * timestep
        return aux_lax

    def calculate_pin(self, timestep: float, area: float) -> float:
        """
        Calculate the PIN expression of current cell
        """
        pin = (
            (
                self.ks
                * (1 / (self.init_arr / self.k_arr_pin + 1))
                * (self.init_auxin / (self.init_auxin + self.k_auxin_pin))
            )
            - self.kd * self.pin
        ) * timestep
        return pin

    def calculate_membrane_pin(self, init: float, timestep: float, area: float) -> float:
        """
        Calculate the PIN expression on one cell membrane
        """
        membrane_pin = (0.25 * self.init_pin - self.kd * init * (1 / area)) * timestep
        return membrane_pin

    def calculate_neighbor_memfrac(self, neighbor) -> float:
        """
        Calculate the fraction of total cell membrane that is in a defined direction
        """
        cell_perimeter = self.cell.quad_perimeter.get_perimeter_len()
        common_perimeter = get_len_perimeter_in_common(self.cell, neighbor)
        memfrac = common_perimeter / cell_perimeter
        return memfrac

    # TODO: Change this to make k_al and k_pin dynamic
    def get_neighbor_auxin_exchange(
        self, pin_dir: float, neighbors: list, direction: str, timestep: float, area: float
    ) -> dict:
        """
        Calculate the auxin expression of neighbor cells in a defined direction
        """
        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_neighbor_memfrac(neighbor)
            # TODO: Make k_al and k_pin  parameters from input
            k_al = 1
            k_pin = 1
            neighbor_aux = neighbor.get_circ_mod().get_auxin()
            neighbor_aux = (
                neighbor_aux * memfrac * self.al * k_al - self.auxin * pin_dir * (1 / area) * k_pin
            ) * timestep
            neighbor_dict[neighbor] = neighbor_aux
        return neighbor_dict

    def calculate_delta_auxin(self, syn_deg_auxin: float, neighbors_auxin: list) -> float:
        """
        Calculate the total amound of change in auxin for current cell
        """
        total_auxin = syn_deg_auxin
        for neighbors in neighbors_auxin:
            auxin = sum(neighbors.values())
            total_auxin += auxin
        return total_auxin

    def get_neighbors(self) -> tuple:
        neighborsa = self.cell.get_a_neighbors()
        neighborsb = self.cell.get_b_neighbors()
        neighborsl = self.cell.get_l_neighbors()
        neighborsm = self.cell.get_m_neighbors()
        return neighborsa, neighborsb, neighborsl, neighborsm

    def update_neighbor_auxin(self, sim_circ, neighbors_auxin: list) -> None:
        """
        Update the change in auxin of neighbor cells in the circulator
        """
        for each_dirct in neighbors_auxin:
            for neighbor in each_dirct:
                sim_circ.add_delta(neighbor, -each_dirct[neighbor])

    def update_arr_hist(self) -> None:
        """
        Update the ARR history list
        """
        for i, elem in enumerate(self.arr_hist):
            if i != 0:
                self.arr_hist[i - 1] = elem
            if i == (len(self.arr_hist) - 1):
                self.arr_hist[i] = self.arr

    # getter functions
    def get_auxin(self) -> float:
        return self.auxin

    def get_arr(self) -> float:
        return self.arr

    def get_al(self) -> float:
        return self.al

    def get_pin(self) -> float:
        return self.pin

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

    def get_state(self) -> dict:
        state = {
            "auxin": self.auxin,
            "arr": self.arr,
            "al": self.al,
            "pin": self.pin,
            "pina": self.pina,
            "pinb": self.pinb,
            "pinl": self.pinl,
            "pinm": self.pinm,
            "k1": self.k_arr_arr,
            "k2": self.k_auxin_auxlax,
            "k3": self.k_auxin_pin,
            "k4": self.k_arr_pin,
            "k_s": self.ks,
            "k_d": self.kd,
            "arr_hist": self.arr_hist,
        }
        return state

    # setter function
    def set_auxin(self, new_aux: float) -> None:
        self.auxin = new_aux
