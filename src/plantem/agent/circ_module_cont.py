from scipy.integrate import odeint
from src.plantem.loc.quad_perimeter.quad_perimeter import get_len_perimeter_in_common
import numpy as np


class BaseCirculateModuleCont:

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

        # set medial to either "left" or "right" and lateral to the opposite
        # based on where self.cell.QuadPerimeter.get_midpointx() is in relation
        # to self.cell.sim.root_midpointx
        self.left, self.right = self.determine_left_right()

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

    def f(self, y, t) -> list:
        area = self.cell.quad_perimeter.get_area()

        # find neighbors
        neighborsa = self.cell.get_a_neighbors()
        neighborsb = self.cell.get_b_neighbors()
        neighborsl = self.cell.get_l_neighbors()
        neighborsm = self.cell.get_m_neighbors()

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
        f3 = self.calculate_pin(auxini, arri, area)
        # neighbor pin
        f4 = self.calculate_neighbor_pin(auxini, arri, pini, pinai, area)
        f5 = self.calculate_neighbor_pin(auxini, arri, pini, pinbi, area)
        f6 = self.calculate_neighbor_pin(auxini, arri, pini, pinli, area)
        f7 = self.calculate_neighbor_pin(auxini, arri, pini, pinmi, area)
        # neighbor auxin
        f8 = self.calcualte_neighbor_auxin(ali, pinai, neighborsa, "a", area)
        f9 = self.calcualte_neighbor_auxin(ali, pinbi, neighborsb, "b", area)
        f10 = self.calcualte_neighbor_auxin(ali, pinli, neighborsl, "l", area)
        f11 = self.calcualte_neighbor_auxin(ali, pinmi, neighborsm, "m", area)

        return [f0, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11]

    def solve_equations(self):
        y0 = [self.auxin, self.arr, self.al, self.pin, self.pina, self.pinb, self.pinl, self.pinm]
        t = np.array[0, 1]
        soln = odeint(self.f, y0, t)
        return soln

    # Helper functions
    def calculate_auxin(self, auxini: float, area: float) -> float:
        """
        Calcualte the auxin expression of current cell
        """
        auxin = self.ks - self.kd * auxini * area
        return auxin

    def calculate_arr(self, arri: float, area: float) -> float:
        """
        Calculate the ARR expression of current cell
        """
        arr = self.ks * 1 / (arri / self.k_arr_arr + 1) - self.kd * arri * area
        return arr

    def calculate_al(self, auxini: float, ali: float, area: float) -> float:
        """
        Calculate the AUX/LAX expression of current cell
        """
        al = self.ks * (auxini / (auxini + self.k_auxin_auxlax)) - self.kd * ali * area
        return al

    def calculate_pin(self, auxini: float, arri: float, area: float) -> float:
        """
        Calculate the PIN expression of current cell
        """
        pin = self.ks * (1 / (arri / self.k_arr_pin + 1)) * (auxini / (auxini + self.k_auxin_pin))
        return pin

    def calculate_neighbor_pin(self, pini: float, pindi: float, area: float) -> float:
        """
        Calculate the PIN expression of neighbor cells
        """
        neighbor_pin = 0.25 * pini - self.kd * pindi * area
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

    def calcualte_neighbor_auxin(
        self, ali: float, pindi: float, neighbors: list, direction: str, area: float
    ) -> dict:
        """
        Calculate the auxin expression of neighbor cells in a defined direction
        """
        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_memfrac(neighbor, direction)
            neighbor_aux = self.ks * memfrac * ali - self.kd * pindi * area
            neighbor_dict[neighbor] = neighbor_aux
        return sum(neighbor_dict.values())
