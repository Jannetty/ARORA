from scipy.integrate import odeint
from src.plantem.loc.quad_perimeter.quad_perimeter import get_len_perimeter_in_common
import numpy as np


class BaseCirculateModuleCont:
    """
    Continuous circulation module to calculate and update circulation contents
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

        self.ks = init_vals.get("k_s")
        self.kd = init_vals.get("k_d")

        self.arr_hist = init_vals.get("arr_hist")

        # set medial to either "left" or "right" and lateral to the opposite
        # based on where self.cell.QuadPerimeter.get_midpointx() is in relation
        # to self.cell.sim.root_midpointx
        self.left, self.right = self.determine_left_right()

    def f(self, y, t) -> list:
        """
        Setup the model functions
        """
        area = self.cell.get_quad_perimeter().get_area()

        # setup species
        auxini = y[0]
        arri = y[1]
        ali = y[2]
        pini = y[3]
        pinai = y[4]
        pinbi = y[5]
        pinli = y[6]
        pinmi = y[7]

        # the model equations
        # auxin
        f0 = self.calculate_auxin(auxini, area)
        # arr
        f1 = self.calculate_arr(arri, area)
        # al
        f2 = self.calculate_al(auxini, ali, area)
        # pin
        f3 = self.calculate_pin(auxini, arri)
        # neighbor pin
        f4 = self.calculate_neighbor_pin(pini, pinai, area)
        f5 = self.calculate_neighbor_pin(pini, pinbi, area)
        f6 = self.calculate_neighbor_pin(pini, pinli, area)
        f7 = self.calculate_neighbor_pin(pini, pinmi, area)

        return [f0, f1, f2, f3, f4, f5, f6, f7]

    def solve_equations(self):
        """
        Solve the differential euqations
        """
        y0 = [self.auxin, self.arr, self.al, self.pin, self.pina, self.pinb, self.pinl, self.pinm]
        t = np.array([0, 1])
        soln = odeint(self.f, y0, t)
        return soln

    def update(self) -> None:
        """
        Update the circulation contents to the circulator
        """
        soln = self.get_solution()
        self.update_circ_contents(soln)
        self.update_auxin(soln)
        print(f"auxin = {self.auxin}")

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

    def calculate_auxin(self, auxini: float, area: float) -> float:
        """
        Calcualte the auxin expression of current cell
        """
        auxin = self.ks - self.kd * auxini * (1 / area)
        return auxin

    def calculate_arr(self, arri: float, area: float) -> float:
        """
        Calculate the ARR expression of current cell
        """
        arr = self.ks * 1 / (self.arr_hist[0] / self.k_arr_arr + 1) - self.kd * arri * (1 / area)
        return arr

    def calculate_al(self, auxini: float, ali: float, area: float) -> float:
        """
        Calculate the AUX/LAX expression of current cell
        """
        al = self.ks * (auxini / (auxini + self.k_auxin_auxlax)) - self.kd * ali * (1 / area)
        return al

    def calculate_pin(self, auxini: float, arri: float) -> float:
        """
        Calculate the PIN expression of current cell
        """
        pin = self.ks * (1 / (arri / self.k_arr_pin + 1)) * (auxini / (auxini + self.k_auxin_pin))
        return pin

    def calculate_neighbor_pin(self, pini: float, pindi: float, area: float) -> float:
        """
        Calculate the PIN expression of neighbor cells
        """
        neighbor_pin = 0.25 * pini - self.kd * pindi * (1 / area)
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
        self, ali: float, pindi: float, neighbors: list, direction: str, area: float
    ) -> dict:
        """
        Calculate the auxin expression of neighbor cells in a defined direction
        """
        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_memfrac(neighbor, direction)
            neighbor_aux = self.ks * memfrac * ali - self.kd * pindi * (1 / area)
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

    def get_solution(self):
        soln = self.solve_equations()
        return soln

    def update_arr_hist(self) -> None:
        """
        Update the ARR history list
        """
        for i, elem in enumerate(self.arr_hist):
            if i != 0:
                self.arr_hist[i - 1] = elem
            if i == (len(self.arr_hist) - 1):
                self.arr_hist[i] = self.arr

    def update_circ_contents(self, soln) -> None:
        """
        Update the circulation contents except auxin
        """
        self.arr = soln[1, 1]
        self.al = soln[1, 2]
        self.pin = soln[1, 3]
        self.pina = soln[1, 4]
        self.pinb = soln[1, 5]
        self.pinl = soln[1, 6]
        self.pinm = soln[1, 7]
        self.update_arr_hist()

    def update_neighbor_auxin(self, sim_circ: dict, neighbors_auxin: list) -> None:
        """
        Update the change in auxin of neighbor cells in the circulator
        """
        for each_dirct in neighbors_auxin:
            for neighbor in each_dirct:
                sim_circ.add_delta(neighbor, -each_dirct[neighbor])

    def get_neighbors(self) -> tuple:
        neighborsa = self.cell.get_a_neighbors()
        neighborsb = self.cell.get_b_neighbors()
        neighborsl = self.cell.get_l_neighbors()
        neighborsm = self.cell.get_m_neighbors()
        return neighborsa, neighborsb, neighborsl, neighborsm

    def update_auxin(self, soln) -> None:
        curr_cell = self.cell
        sim_circ = curr_cell.get_sim().get_circulator()

        neighborsa, neighborsb, neighborsl, neighborsm = self.get_neighbors()
        area = self.cell.quad_perimeter.get_area()

        auxina = self.get_neighbor_auxin(self.al, self.pina, neighborsa, "a", area)
        auxinb = self.get_neighbor_auxin(self.al, self.pinb, neighborsb, "b", area)
        auxinl = self.get_neighbor_auxin(self.al, self.pinl, neighborsl, "l", area)
        auxinm = self.get_neighbor_auxin(self.al, self.pinm, neighborsm, "m", area)
        neighbors_auxin = [auxina, auxinb, auxinl, auxinm]

        syn_deg_auxin = soln[1, 0] - self.auxin
        delta_auxin = self.calculate_delta_auxin(syn_deg_auxin, neighbors_auxin)

        # update current cell
        sim_circ.add_delta(curr_cell, delta_auxin)
        # print(sim_circ.delta_auxins)

        # update neighbor cell
        self.update_neighbor_auxin(sim_circ, neighbors_auxin)

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
            "k_arr_arr": self.k_arr_arr,
            "k_auxin_auxlax": self.k_auxin_auxlax,
            "k_auxin_pin": self.k_auxin_pin,
            "k_arr_pin": self.k_arr_pin,
            "ks": self.ks,
            "kd": self.kd,
            "arr_hist": self.arr_hist,
        }
        return state

    def get_state_half(self) -> dict:
        state_half = {
            "auxin": self.auxin / 2,
            "arr": self.arr / 2,
            "al": self.al / 2,
            "pin": self.pin / 2,
            "pina": self.pina / 2,
            "pinb": self.pinb / 2,
            "pinl": self.pinl / 2,
            "pinm": self.pinm / 2,
            "k_arr_arr": self.k_arr_arr,
            "k_auxin_auxlax": self.k_auxin_auxlax,
            "k_auxin_pin": self.k_auxin_pin,
            "k_arr_pin": self.k_arr_pin,
            "ks": self.ks,
            "kd": self.kd,
            "arr_hist": self.arr_hist,
        }
        return state_half
