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
    weighta = 0
    weightb = 0
    weightl = 0
    weightm = 0

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

        self.growing = init_vals.get("growing")

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
        self.left = self.cell.get_quad_perimeter().get_left_lateral_or_medial(self.cell.get_sim().get_root_midpointx())
        self.right = self.cell.get_quad_perimeter().get_right_lateral_or_medial(self.cell.get_sim().get_root_midpointx())

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
        f4 = self.calculate_membrane_pin(pini, pinai, area, 'a')
        f5 = self.calculate_membrane_pin(pini, pinbi, area, 'b')
        f6 = self.calculate_membrane_pin(pini, pinli, area, 'l')
        f7 = self.calculate_membrane_pin(pini, pinmi, area, 'm')

        return [f0, f1, f2, f3, f4, f5, f6, f7]

    def solve_equations(self):
        """
        Solve the differential euqations
        """
        y0 = [self.auxin, self.arr, self.al, self.pin, self.pina, self.pinb, self.pinl, self.pinm]
        t = np.array([0, 1])
        soln = odeint(self.f, y0, t)
        return soln

    def get_solution(self):
        soln = self.solve_equations()
        return soln

    def update(self, pin_weights: dict) -> None:
        """
        Update the circulation contents to the circulator
        """
        self.weighta = pin_weights.get("a")
        self.weightb = pin_weights.get("b")
        self.weightl = pin_weights.get("l")
        self.weightm = pin_weights.get("m")
        # if self.cell.id == 30 or self.cell.id == 31:
        #     print(f"IN UPDATE before get_solution, CELL {self.cell.id}, al = {self.al}, pinb = {self.pinb}")
        #     print(self.get_state())
        #     print(f"memfrac a = {self.cell.quad_perimeter.get_memfrac('a', self.left)}")
        #     print(f"memfrac b = {self.cell.quad_perimeter.get_memfrac('b', self.left)}")
        #     print(f"memfrac l = {self.cell.quad_perimeter.get_memfrac('l', self.left)}")
        #     print(f"memfrac m = {self.cell.quad_perimeter.get_memfrac('m', self.left)}")
        soln = self.get_solution()
        # if self.cell.id == 30 or self.cell.id == 31:
        #     print(f"IN UPDATE after get_solution, CELL {self.cell.id}, al = {soln[1][2]}, pinb = {soln[1][5]}")
        #     print(soln[1])
        self.update_auxin(soln)
        self.update_circ_contents(soln)
        # self.update_membrane_pin()


    def calculate_auxin(self, auxini: float, area: float) -> float:
        """
        Calculate the auxin expression of current cell
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
        pin = self.ks * (1 / (arri / self.k_arr_pin + 1)) * (auxini / (auxini + self.k_auxin_pin)) - self.kd * self.pin
        return pin

    def calculate_membrane_pin(self, pini: float, pindi: float, area: float, direction: str) -> float:
        """
        Calculate the PIN expression of neighbor cells
        """
        # TODO: Make get_weight a function, class of calculators that can take different values
        # TODO: have weight as parameter that is fed in
        weight = 1
        memfrac = self.cell.get_quad_perimeter().get_memfrac(direction, self.left)
        membrane_pin = memfrac * pini - self.kd * pindi * (1 / area) * weight
        return membrane_pin

    def calculate_neighbor_memfrac(self, neighbor) -> float:
        """
        Calculate the fraction of total cell membrane that is in a defined direction and shared with a specified neighbor
        """
        cell_perimeter = self.cell.quad_perimeter.get_perimeter_len()
        common_perimeter = get_len_perimeter_in_common(self.cell, neighbor)
        memfrac = common_perimeter / cell_perimeter
        return memfrac

    def get_neighbor_auxin_exchange(
        self, al: float, pindi: float, neighbors: list, area: float
    ) -> dict:
        """
        Calculate the amount of auxin that will be transported across each membrane
        """

        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_neighbor_memfrac(neighbor)
            if self.cell.id==20 or self.cell.id==25:
                if neighbor.id == 17 or neighbor.id == 18:
                    print(f"in get_neighbor_auxin_exchange, cell {self.cell.id} - neighbor {neighbor.id}")
                    print(f"cell {self.cell.get_id()} auxin = {self.auxin}")
                    print(f"cell {self.cell.get_id()} al = {al}")
                    print(f"cell {self.cell.get_id()} k_al = {self.k_al}")
                    print(f"cell {self.cell.get_id()} pindi = {pindi}")
                    print(f"cell {self.cell.get_id()} area = {area}")
                    print(f"cell {self.cell.get_id()} k_pin = {self.k_pin}")
                    print(f"cell {self.cell.get_id()} neighbor {neighbor.get_id()} memfrac = {memfrac}")
                    print(f"neighbor {neighbor.get_id()} auxin = {neighbor.get_circ_mod().get_auxin()}")
            neighbor_aux = neighbor.get_circ_mod().get_auxin()
            neighbor_aux_exchange = neighbor_aux * memfrac * al * self.k_al - self.auxin * pindi * (1 / area) * self.k_pin
            if self.cell.id==20 or self.cell.id==25:
                if neighbor.id == 17 or neighbor.id == 18:
                    print(f"cell {self.cell.get_id()} neighbor {neighbor.get_id()} aux_exchange = {neighbor_aux_exchange}")
            neighbor_dict[neighbor] = round(neighbor_aux_exchange, 5)
        return neighbor_dict

    def calculate_delta_auxin(self, syn_deg_auxin: float, neighbors_auxin: list) -> float:
        """
        Calculate the total amount of change in auxin for current cell
        """
        # if self.cell.id == 39 or self.cell.id == 42:
        #     print(f"cell {self.cell.id} neighbors_auxin = {neighbors_auxin}")
        total_auxin = syn_deg_auxin
        for neighbors in neighbors_auxin:
            auxin = sum(neighbors.values())
            total_auxin += auxin
        return total_auxin

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
        self.arr = round(soln[1, 1], 5)
        self.al = round(soln[1, 2], 5)
        self.pin = round(soln[1, 3], 5)
        self.pina = round(soln[1, 4], 5)
        self.pinb = round(soln[1, 5], 5)
        self.pinl = round(soln[1, 6], 5)
        self.pinm = round(soln[1, 7], 5)
        self.update_arr_hist()
        # if self.cell.id == 17 or self.cell.id == 18:
        #     print("in update_circ_contents")
        #     print(self.get_state())

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
        if self.cell.id == 20 or self.cell.id == 25:
            print(f"cell {self.cell.id} neighborsa = {[thiscell.id for thiscell in neighborsa]}")
            print(f"cell {self.cell.id} neighborsb = {[thiscell.id for thiscell in neighborsb]}")
            print(f"cell {self.cell.id} neighborsl = {[thiscell.id for thiscell in neighborsl]}")
            print(f"cell {self.cell.id} neighborsm = {[thiscell.id for thiscell in neighborsm]}")
        return neighborsa, neighborsb, neighborsl, neighborsm

    def update_auxin(self, soln) -> None:
        curr_cell = self.cell
        sim_circ = curr_cell.get_sim().get_circulator()

        neighborsa, neighborsb, neighborsl, neighborsm = self.get_neighbors()
        area = self.cell.quad_perimeter.get_area()

        # if self.cell.id == 13 or self.cell.id == 14:
        #     print(f"IN UPDATE AUXIN, CELL {self.cell.id}, al = {self.al}, pinb = {self.pinb}")

        auxina = self.get_neighbor_auxin_exchange(self.al, self.pina, neighborsa, area)
        # if curr_cell.id == 39 or curr_cell.id == 42:
        #     print(f"cell {curr_cell.id} auxina = {auxina}")
        auxinb = self.get_neighbor_auxin_exchange(self.al, self.pinb, neighborsb, area)
        # if curr_cell.id == 39 or curr_cell.id == 42:
        #     print(f"cell {curr_cell.id} auxinb = {auxinb}")
        auxinl = self.get_neighbor_auxin_exchange(self.al, self.pinl, neighborsl, area)
        # if curr_cell.id == 39 or curr_cell.id == 42:
        #     print(f"cell {curr_cell.id} auxinl = {auxinl}")
        auxinm = self.get_neighbor_auxin_exchange(self.al, self.pinm, neighborsm, area)
        # if curr_cell.id == 38 or curr_cell.id == 43:
        #     print(f"cell {curr_cell.id} auxinm = {auxinm}")
        #     print(f"cell {curr_cell.id} al = {self.al}")
        #     print(f"cell {curr_cell.id} pinm = {self.pinm}")
        #     print(f"cell {curr_cell.id} area = {area}")
        #     print(f"cell {curr_cell.id} neighborsm = {neighborsm}")
        neighbors_auxin = [auxina, auxinb, auxinl, auxinm]

        syn_deg_auxin = soln[1, 0] - self.auxin
        # if curr_cell.id == 39 or curr_cell.id == 42:
        #     print(f"cell {curr_cell.id} syn_deg_auxin = {syn_deg_auxin}")
        delta_auxin = self.calculate_delta_auxin(syn_deg_auxin, neighbors_auxin)
        # if curr_cell.id == 30 or curr_cell.id == 31:
        #     print(f"cell {curr_cell.id} delta_auxin = {delta_auxin}")

        # update current cell
        sim_circ.add_delta(curr_cell, round(delta_auxin,5))

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
        
    def get_arr_hist(self) -> list:
        return self.arr_hist

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
            "k5": self.k_al,
            "k6": self.k_pin,
            "k_s": self.ks,
            "k_d": self.kd,
            "arr_hist": self.arr_hist,
        }
        return state
    

    # setter function
    def set_auxin(self, new_aux: float) -> None:
        self.auxin = new_aux
