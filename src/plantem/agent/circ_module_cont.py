import numpy as np
from scipy.integrate import odeint
from src.plantem.loc.quad_perimeter.quad_perimeter import get_len_perimeter_in_common
from src.plantem.sim.util.math_helpers import round_to_sf


class BaseCirculateModuleCont:
    """
    Base class for the circulation module controller.

    Attributes:
        auxin (float): The auxin concentration in the cell.
        arr (float): The ARR concentration in the cell.
        al (float): The AUX/LAX expression in the cell.
        pin (float): The unlocalized PIN expression in the cell.
        pina (float): The PIN localized in the apical direction.
        pinb (float): The PIN localized in the basal direction.
        pinl (float): The PIN localized in the lateral direction.
        pinm (float): The PIN localized in the medial direction.
        cell (Cell): The cell associated with the circulation module.
        left (str): Whether the cell's left membrane is lateral or medial.
        right (str): Whether the cell's right membrane is lateral or medial.
        weighta (float): The proportion of localized PIN in the apical direction.
        weightb (float): The proportion of localized PIN in the basal direction.
        weightl (float): The proportion of localized PIN in the lateral direction.
        weightm (float): The proportion of localized PIN in the medial direction.
        auxin_w (float): The weight of auxin synthesis.
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
    auxin_w = 0

    def __init__(self, cell, init_vals: dict):
        """
        Initialize the BaseCirculateModuleCont object.

        Args:
            cell (Cell): The cell associated with the circulation module.
            init_vals (dict): The initial values for the attributes.
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

        self.auxin_w = init_vals.get("auxin_w")

        self.arr_hist = init_vals.get("arr_hist")

        # set medial to either "left" or "right" and lateral to the opposite
        # based on where self.cell.QuadPerimeter.get_midpointx() is in relation
        # to self.cell.sim.root_midpointx
        self.left = self.cell.get_quad_perimeter().get_left_lateral_or_medial(
            self.cell.get_sim().get_root_midpointx()
        )
        self.right = self.cell.get_quad_perimeter().get_right_lateral_or_medial(
            self.cell.get_sim().get_root_midpointx()
        )

        self.pin_weights = self.initialize_pin_weights()

    def initialize_pin_weights(self):
        """
        Initialize the pin weights for each membrane
        given input-file specified initial PIN distribution
        """
        pin_weights_dict = {}
        pina = self.get_apical_pin()
        pinb = self.get_basal_pin()
        pinl = self.get_lateral_pin()
        pinm = self.get_medial_pin()
        pin_vals = [pina, pinb, pinl, pinm]
        pin_sum = pina + pinb + pinl + pinm
        for (val, direction) in zip(pin_vals, ["a", "b", "l", "m"]):
            pin_weights_dict[direction] = val / pin_sum
        return pin_weights_dict

    def f(self, y, t) -> list:
        """
        Setup the model differential equations.

        Args:
            y (list): The current values of the variables.
            t (float): The current time.

        Returns:
            list: The derivative equations of the variables.
        """

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
        f0 = self.calculate_auxin(auxini)
        # arr
        f1 = self.calculate_arr(arri)
        # al
        f2 = self.calculate_al(auxini, ali)
        # pin
        f3 = self.calculate_pin(auxini, arri)
        # neighbor pin
        f4 = self.calculate_membrane_pin(pini, pinai, "a", self.pin_weights.get("a"))
        f5 = self.calculate_membrane_pin(pini, pinbi, "b", self.pin_weights.get("b"))
        f6 = self.calculate_membrane_pin(pini, pinli, "l", self.pin_weights.get("l"))
        f7 = self.calculate_membrane_pin(pini, pinmi, "m", self.pin_weights.get("m"))

        return [f0, f1, f2, f3, f4, f5, f6, f7]

    def solve_equations(self):
        """
        Solve the differential equations.

        Returns:
            ndarray: The solution of the differential equations.
        """
        y0 = [
            self.auxin,
            self.arr,
            self.al,
            self.pin,
            self.pina,
            self.pinb,
            self.pinl,
            self.pinm,
        ]
        t = np.array([0, 1])
        soln = odeint(self.f, y0, t)
        return soln

    def update(self) -> None:
        """
        Update the circulation contents of the circulator.
        """
        self.pin_weights = self.cell.get_pin_weights()
        assert round_to_sf(sum(self.pin_weights.values()), 2) == 1.0
        soln = self.solve_equations()
        self.update_auxin(soln)
        self.update_circ_contents(soln)

    def calculate_auxin(self, auxini: float) -> float:
        """
        Calculate the auxin synthesis and degradation of the current cell.

        Args:
            auxini (float): The initial (current) auxin concentration of the
                            current cell in au/um^2.

        Returns:
            float: The calculated auxin concentration.
        """
        auxin = (self.ks * self.auxin_w) - (self.kd * auxini)
        return auxin

    def calculate_arr(self, arri: float) -> float:
        """
        Calculate the ARR concentration of the current cell.

        Args:
            arri (float): The initial (current) ARR concentration in au/um^2.

        Returns:
            float: The calculated ARR concentration.
        """
        arr = (self.ks * (self.k_arr_arr / (self.arr_hist[0] + self.k_arr_arr))) - (self.kd * arri)
        return arr

    def calculate_al(self, auxini: float, ali: float) -> float:
        """
        Calculate the AUX/LAX expression of the current cell.

        Args:
            auxini (float): The initial (current) auxin concentration of the
                            current cell in au/um^2.
            ali (float): The initial (current) AUX/LAX expression in au/um^2.

        Returns:
            float: The calculated AUX/LAX expression.
        """
        al = self.ks * (auxini / (auxini + self.k_auxin_auxlax)) - self.kd * ali
        return al

    def calculate_pin(self, auxini: float, arri: float) -> float:
        """
        Calculate the PIN expression of the current cell.

        Args:
            auxini (float): The initial (current) auxin concentration of the
                            current cell in au/um^2.
            arri (float): The initial (current) ARR expression in au/um^2.

        Returns:
            float: The calculated PIN expression.
        """
        pin = (
            self.ks
            * (self.k_arr_pin / (arri + self.k_arr_pin))
            * (auxini / (auxini + self.k_auxin_pin))
            - self.kd * self.pin
        )
        return pin

    def calculate_membrane_pin(
        self, pini: float, pindi: float, direction: str, pin_weight: float
    ) -> float:
        """
        Calculate the PIN expression on one membrane.

        Args:
            pini (float): The current cell's unlocalized PIN expression.
            pindi (float): The current cell's localized PIN expression
                           in the specified direction.
            direction (str): The direction of the membrane.
            pin_weight (float): The proportion of membrane localized pin
                                in this membrane

        Returns:
            float: The calculated PIN expression on the membrane.
        """
        weight = pin_weight
        memfrac = self.cell.get_quad_perimeter().get_memfrac(direction, self.left)
        membrane_pin = pin_weight * pini - (self.kd * pindi)
        return membrane_pin

    def calculate_neighbor_memfrac(self, neighbor) -> float:
        """
        Calculate the fraction of total cell membrane that is shared
        with a specified neighbor.

        Args:
            neighbor: The neighbor cell.

        Returns:
            float: The fraction of total cell membrane shared with the neighbor.
        """
        cell_perimeter = self.cell.quad_perimeter.get_perimeter_len()
        try:
            common_perimeter = get_len_perimeter_in_common(self.cell, neighbor)
        except Exception as e:
            print(
                "cell",
                self.cell.get_c_id(),
                " does not neighbor cell",
                neighbor.get_c_id(),
            )
            raise e
        memfrac = common_perimeter / cell_perimeter
        return round_to_sf(memfrac, 6)

    def get_aux_exchange_across_membrane(self, al: float, pindi: float, neighbors: list) -> dict:
        """
        Calculate the amount of auxin that will be transported across each membrane.

        Args:
            al (float): The AUX/LAX concentration of the current cell.
            pindi (float): The localized PIN expression in the specified direction
                           of the current cell.
            neighbors (list): The list of neighbor cells.

        Returns:
            dict: A dictionary containing the amount of auxin transported across each membrane.
                  Keys are neighbor cells, values are the amount of auxin transported.
        """
        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_neighbor_memfrac(neighbor)
            neighbor_aux = neighbor.get_circ_mod().get_auxin()
            # added memfrac to export al term
            # TODO: change memfrac below multiplied by neighbor_aux to be neighbor memfrac
            auxin_influx = (neighbor_aux * (memfrac)) * (al * memfrac) * self.k_al
            # added memfrac to export term
            # TODO: Make pin_activity a sigmoidal variable that ranges from 0 to 1
            pin_activity = ((pindi * memfrac) / (pindi * memfrac + self.k_pin)) * self.k_pin
            accessible_pin = self.auxin * memfrac
            auxin_efflux = accessible_pin * pin_activity
            if (
                auxin_influx == float("inf")
                or auxin_influx == float("-inf")
                or auxin_efflux == float("inf")
                or auxin_efflux == float("-inf")
            ):
                print(f"cell {self.cell.get_c_id()} neighbor {neighbor.get_c_id()}")
                print(f"neighbor's auxin {auxin_influx}, self aux out {auxin_efflux}")
            neighbor_aux_exchange = auxin_influx - auxin_efflux
            neighbor_dict[neighbor] = round_to_sf(neighbor_aux_exchange, 5)
        return neighbor_dict

    def calculate_delta_auxin(self, syn_deg_auxin: float, neighbors_auxin: list) -> float:
        """
        Calculate the total amount of change in auxin for the current cell.

        Args:
            syn_deg_auxin (float): The amount of auxin synthesized and degraded
                                   in the current cell.
            neighbors_auxin (list): The list of dictionaries containing the amount of
                                    auxin transported across each membrane for each
                                    neighbor cell.

        Returns:
            float: The total amount of change in auxin for the current cell.
        """
        total_auxin = syn_deg_auxin
        for neighbors in neighbors_auxin:
            auxin = sum(neighbors.values())
            if (
                auxin == float("inf")
                or total_auxin == float("inf")
                or auxin == float("-inf")
                or total_auxin == float("-inf")
            ):
                print(f"cell {self.cell.get_c_id()} auxin {auxin}, total auxin {total_auxin}")
            else:
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

        Args:
            soln (ndarray): The solution of the differential equations.
        """
        self.arr = round_to_sf(soln[1, 1], 5)
        self.al = round_to_sf(soln[1, 2], 5)
        self.pin = round_to_sf(soln[1, 3], 5)
        self.pina = round_to_sf(soln[1, 4], 5)
        self.pinb = round_to_sf(soln[1, 5], 5)
        self.pinl = round_to_sf(soln[1, 6], 5)
        self.pinm = round_to_sf(soln[1, 7], 5)
        self.update_arr_hist()

    def update_neighbor_auxin(self, neighbors_auxin: list) -> None:
        """
        Update the change in auxin of neighbor cells in the circulator

        Args:
            neighbors_auxin (list): The list of dictionaries containing the amount of auxin
                                    transported across each membrane for each neighbor cell.
        """
        for each_dirct in neighbors_auxin:
            for neighbor in each_dirct:
                self.cell.get_sim().get_circulator().add_delta(neighbor, -each_dirct[neighbor])

    def get_neighbors(self) -> tuple:
        """
        Get the neighbors of the current cell.

        Returns:
            tuple: A tuple containing the list of neighbors for each membrane.
        """
        neighborsa = self.cell.get_a_neighbors()
        neighborsb = self.cell.get_b_neighbors()
        neighborsl = self.cell.get_l_neighbors()
        neighborsm = self.cell.get_m_neighbors()
        return neighborsa, neighborsb, neighborsl, neighborsm

    def update_auxin(self, soln) -> None:
        """
        Update the auxin of the current cell and its neighbors.

        Args:
            soln (ndarray): The solution of the differential equations.
        """
        curr_cell = self.cell

        neighborsa, neighborsb, neighborsl, neighborsm = self.get_neighbors()

        auxina_exchange = self.get_aux_exchange_across_membrane(self.al, self.pina, neighborsa)
        auxinb_exchange = self.get_aux_exchange_across_membrane(self.al, self.pinb, neighborsb)
        auxinl_exchange = self.get_aux_exchange_across_membrane(self.al, self.pinl, neighborsl)
        auxinm_exchange = self.get_aux_exchange_across_membrane(self.al, self.pinm, neighborsm)
        neighbors_auxin_exchange = [
            auxina_exchange,
            auxinb_exchange,
            auxinl_exchange,
            auxinm_exchange,
        ]

        auxin_synthesized_and_degraded_this_timestep = soln[1, 0] - self.auxin

        total_aux_exchange = (
            sum(auxina_exchange.values())
            + sum(auxinb_exchange.values())
            + sum(auxinl_exchange.values())
            + sum(auxinm_exchange.values())
        )

        if (soln[1, 0] + total_aux_exchange) < 0:
            print("-------------------")
            print(f"cell {self.cell.get_c_id()} auxin {soln[1, 0]}")
            print(f"total aux exchange {total_aux_exchange}")
            print("-------------------")
            raise ValueError("Negative auxin")

        delta_auxin = self.calculate_delta_auxin(
            auxin_synthesized_and_degraded_this_timestep, neighbors_auxin_exchange
        )

        # update current cell
        curr_cell.get_sim().get_circulator().add_delta(curr_cell, round_to_sf(delta_auxin, 5))

        # update neighbor cell
        self.update_neighbor_auxin(neighbors_auxin_exchange)

    # getter functions
    def get_auxin(self) -> float:
        """
        Get the auxin concentration in the cell.

        Returns:
            float: The auxin concentration in the cell.
        """
        return self.auxin

    def get_arr(self) -> float:
        """
        Get the ARR concentration in the cell.

        Returns:
            float: The ARR concentration in the cell.
        """
        return self.arr

    def get_al(self) -> float:
        """
        Get the AUX/LAX expression in the cell.

        Returns:
            float: The AUX/LAX expression in the cell.
        """
        return self.al

    def get_arr_hist(self) -> list:
        """
        Get the ARR history list.

        Returns:
            list: The ARR history list.
        """
        return self.arr_hist

    def get_auxin_w(self) -> float:
        """
        Get the weight of auxin synthesis.

        Returns:
            float: The weight of auxin synthesis.
        """
        return self.auxin_w

    def get_pin(self) -> float:
        """
        Get the unlocalized PIN expression in the cell.

        Returns:
            float: The unlocalized PIN expression in the cell.
        """
        return self.pin

    def get_apical_pin(self) -> float:
        """
        Get the PIN localized in the apical direction.

        Returns:
            float: The PIN localized in the apical direction.
        """
        return self.pina

    def get_basal_pin(self) -> float:
        """
        Get the PIN localized in the basal direction.

        Returns:
            float: The PIN localized in the basal direction.
        """
        return self.pinb

    def get_lateral_pin(self) -> float:
        """
        Get the PIN localized in the lateral direction.

        Returns:
            float: The PIN localized in the lateral direction.
        """
        return self.pinl

    def get_medial_pin(self) -> float:
        """
        Get the PIN localized in the medial direction.

        Returns:
            float: The PIN localized in the medial direction.
        """
        return self.pinm

    def get_left_pin(self) -> float:
        """
        Get the PIN localized in the left direction.

        Returns:
            float: The PIN localized in the left direction.
        """
        if self.left == "medial":
            return self.pinm
        return self.pinl

    def get_right_pin(self) -> float:
        """
        Get the PIN localized in the right direction.

        Returns:
            float: The PIN localized in the right direction.
        """
        if self.right == "medial":
            return self.pinm
        return self.pinl

    def get_state(self) -> dict:
        """
        Get the state of the circulate module.

        Returns:
            dict: All circ mod attributes and current values.
        """
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
            "auxin_w": self.auxin_w,
            "arr_hist": self.arr_hist,
        }
        return state

    def set_auxin(self, new_aux: float) -> None:
        """
        Set the auxin concentration in the cell.

        Args:
            new_aux (float): The new auxin concentration in the cell.
        """
        self.auxin = new_aux
