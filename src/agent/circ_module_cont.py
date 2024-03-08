import numpy as np
from typing import TYPE_CHECKING, cast, Any
from scipy.integrate import odeint
from src.loc.quad_perimeter.quad_perimeter import get_len_perimeter_in_common
from src.sim.util.math_helpers import round_to_sf

if TYPE_CHECKING:
    from src.agent.cell import Cell


class BaseCirculateModuleCont:
    """
    Base class for the circulation module controller.

    This class defines the core attributes and methods required for simulating
    the circulation of auxin between cells, focusing on regulatory interactions
    pf auxin and ARR, as well as the expression and localization of PIN proteins.

    Attributes
    ----------
    auxin : float
        The concentration of auxin in the cell.
    arr : float
        The concentration of ARR in the cell.
    arr_hist : list[float]
        History of ARR concentrations in the cell for the last `len(arr_hist)` time points.
    al : float
        The expression level of AUX/LAX in the cell.
    pin : float
        The total unlocalized PIN expression in the cell.
    pina : float
        The PIN protein localized in the apical direction.
    pinb : float
        The PIN protein localized in the basal direction.
    pinl : float
        The PIN protein localized in the lateral direction.
    pinm : float
        The PIN protein localized in the medial direction.
    cell : Cell
        The cell instance associated with this circulation module.
    left : str
        Indicates if the cell's left membrane is lateral ('l') or medial ('m').
    right : str
        Indicates if the cell's right membrane is lateral ('l') or medial ('m').
    pin_weights : dict[str, float]
        Weights of the PIN protein localized in each direction ('a', 'b', 'l', 'm') as keys and their respective weights as values.
    k_arr_arr : float
        Concentration of ARR at which the rate of ARR synthesis is half its maximum. ARR negatively regulates its own synthesis.
    k_auxin_auxlax : float
        Concentration of auxin at which the rate of AUX/LAX synthesis is half its maximum. Auxin positively regulates AUX/LAX synthesis.
    k_auxin_pin : float
        Concentration of auxin at which the rate of PIN synthesis is half its maximum. Auxin positively regulates PIN synthesis.
    k_arr_pin : float
        Concentration of ARR at which the rate of PIN synthesis is half its maximum. ARR negatively regulates PIN synthesis.
    k_al : float
        Rate of auxin import through AUX/LAX proteins.
    k_pin : float
        Rate of auxin export through PIN proteins.
    ks : float
        Rate of synthesis of the species.
    kd : float
        Rate of degradation of the species.
    auxin_w : float
        Weight of auxin in the synthesis process.
    """

    auxin: float
    arr: float
    al: float
    pin: float
    pina: float
    pinb: float
    pinl: float
    pinm: float
    cell: "Cell"
    left: str
    right: str
    pin_weights: dict[str, float]
    k_arr_arr: float
    k_auxin_auxlax: float
    k_auxin_pin: float
    k_arr_pin: float
    k_al: float
    k_pin: float
    ks: float
    kd: float
    auxin_w: float
    arr_hist: list[float]

    def __init__(self, cell: "Cell", init_vals: dict[str, Any]):
        """
        Initialize the BaseCirculateModuleCont object by setting up initial values for various cellular attributes.

        Parameters
        ----------
        cell : Cell
            The cell associated with the circulation module. This parameter expects an instance of a Cell class.
        init_vals : dict[str, Any]
            A dictionary containing the initial values for the object's attributes. Expected keys include "auxin",
            "arr", "al", "pin", "pina", "pinb", "pinl", "pinm", "growing", "k1" through "k6", "k_s", "k_d", and "auxin_w".
            Each key's value should be of the appropriate type (float for numerical values, bool for "growing", and list[float] for "arr_hist").

        Attributes
        ----------
        cell : Cell
            The cell associated with this module.
        auxin : float
            Initial concentration of auxin in the cell.
        arr : float
            Initial concentration of ARR in the cell.
        al : float
            Initial level of AUX/LAX expression in the cell.
        pin : float
            Initial level of unlocalized PIN expression in the cell.
        pina, pinb, pinl, pinm : float
            Initial levels of PIN localized in the apical, basal, lateral, and medial directions, respectively.
        growing : bool
            Indicates whether the cell is currently growing.
        k_arr_arr, k_auxin_auxlax, k_auxin_pin, k_arr_pin, k_al, k_pin : float
            Parameters for various rate calculations within the cell, relating to ARR, auxin, and PIN dynamics.
        ks : float
            Rate of synthesis of the species.
        kd : float
            Rate of degradation of the species.
        auxin_w : float
            Weight of auxin synthesis.
        arr_hist : list[float]
            History of ARR concentrations in the cell.
        left, right : str
            Indicators of whether the cell's left or right membrane is lateral or medial, respectively.
        pin_weights : dict
            Weights of PIN localized in each membrane direction.

        Notes
        -----
        The 'init_vals' dictionary must contain keys corresponding to all attributes that need to be initialized. Missing keys may result in an AttributeError.
        """

        self.cell = cell

        self.init_auxin = cast(float, init_vals.get("auxin"))
        self.auxin = self.init_auxin

        self.init_arr = cast(float, init_vals.get("arr"))
        self.arr = self.init_arr

        self.init_al = cast(float, init_vals.get("al"))
        self.al = self.init_al

        self.init_pin = cast(float, init_vals.get("pin"))
        self.pin = self.init_pin

        self.init_pina = cast(float, init_vals.get("pina"))
        self.pina = self.init_pina

        self.init_pinb = cast(float, init_vals.get("pinb"))
        self.pinb = self.init_pinb

        self.init_pinl = cast(float, init_vals.get("pinl"))
        self.pinl = self.init_pinl

        self.init_pinm = cast(float, init_vals.get("pinm"))
        self.pinm = self.init_pinm

        self.growing = cast(bool, init_vals.get("growing"))

        self.k_arr_arr = cast(float, init_vals.get("k1"))
        self.k_auxin_auxlax = cast(float, init_vals.get("k2"))
        self.k_auxin_pin = cast(float, init_vals.get("k3"))
        self.k_arr_pin = cast(float, init_vals.get("k4"))
        self.k_al = cast(float, init_vals.get("k5"))
        self.k_pin = cast(float, init_vals.get("k6"))

        self.ks = cast(float, init_vals.get("k_s"))
        self.kd = cast(float, init_vals.get("k_d"))

        self.auxin_w = cast(float, init_vals.get("auxin_w"))

        self.arr_hist = cast(list[float], init_vals.get("arr_hist"))

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

    def initialize_pin_weights(self) -> dict[str, float]:
        """
        Initialize PIN weights for each membrane based on initial PIN distribution.

        Returns
        -------
        dict[str, float]
            A dictionary mapping membrane identifiers ('a' for apical, 'b' for basal,
            'l' for lateral, 'm' for medial) to their respective initial PIN weights.
        """
        pin_weights_dict = {}
        pina = self.get_apical_pin()
        pinb = self.get_basal_pin()
        pinl = self.get_lateral_pin()
        pinm = self.get_medial_pin()
        pin_vals = [pina, pinb, pinl, pinm]
        pin_sum = pina + pinb + pinl + pinm
        for val, direction in zip(pin_vals, ["a", "b", "l", "m"]):
            pin_weights_dict[direction] = val / pin_sum
        return pin_weights_dict

    def f(self, y: list[float], t: float) -> list[float]:
        """
        Define the model's differential equations.

        Parameters
        ----------
        y : list[float]
            The current values of the model variables, ordered as [auxin, ARR, AUX/LAX,
            unlocalized PIN, apical PIN, basal PIN, lateral PIN, medial PIN].
        t : float
            The current simulation time.

        Returns
        -------
        list[float]
            The derivatives of the model variables, representing the rate of change
            of each variable at time `t`.
        """

        # Variable unpacking for clarity
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
        f4 = self.calculate_membrane_pin(pini, pinai, "a", cast(float, self.pin_weights.get("a")))
        f5 = self.calculate_membrane_pin(pini, pinbi, "b", cast(float, self.pin_weights.get("b")))
        f6 = self.calculate_membrane_pin(pini, pinli, "l", cast(float, self.pin_weights.get("l")))
        f7 = self.calculate_membrane_pin(pini, pinmi, "m", cast(float, self.pin_weights.get("m")))

        return [f0, f1, f2, f3, f4, f5, f6, f7]

    def solve_equations(self) -> np.ndarray:
        """
        Solve the model's differential equations over a given time span.

        Returns
        -------
        ndarray
            An array containing the solution of the differential equations at each
            time step. Each row corresponds to a time step, and each column corresponds
            to one of the model variables.
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
        Update the model's circulation contents based on current PIN weights and differential equations.

        This method performs a series of updates to the model's state, including:
        - Retrieving current PIN weights from the associated cell.
        - Solving the model's differential equations over a time step.
        - Updating auxin levels and other circulation-related contents based on the solutions obtained.

        Ensures that the sum of PIN weights is 1.0 before proceeding with the updates.
        """
        # Retrieve current PIN weights
        self.pin_weights = self.cell.get_pin_weights()
        assert round_to_sf(sum(self.pin_weights.values()), 2) == 1.0, "PIN weights sum to 1.0"

        # Solve the differential equations for the current state
        soln = self.solve_equations()

        # Update model states based on the solutions
        self.update_auxin(soln)
        self.update_circ_contents(soln)

    def calculate_auxin(self, auxini: float) -> float:
        """
        Calculate the auxin synthesis and degradation of the current cell.

        Parameters
        ----------
        auxini : float
            The initial (current) auxin concentration of the current cell in au/um^2.

        Returns
        -------
        float
            The calculated auxin concentration after accounting for synthesis and
            degradation.
        """
        auxin = (self.ks * self.auxin_w) - (self.kd * auxini)
        return auxin

    def calculate_arr(self, arri: float) -> float:
        """
        Calculate the ARR concentration of the current cell based on initial
        concentration and historical data.

        Parameters
        ----------
        arri : float
            The initial (current) ARR concentration in au/um^2.

        Returns
        -------
        float
            The calculated ARR concentration after accounting for synthesis and
            degradation dynamics.
        """
        arr = (self.ks * (self.k_arr_arr / (self.arr_hist[0] + self.k_arr_arr))) - (self.kd * arri)
        return arr

    def calculate_al(self, auxini: float, ali: float) -> float:
        """
        Calculate the AUX/LAX expression of the current cell based on initial
        auxin concentration and AUX/LAX expression.

        Parameters
        ----------
        auxini : float
            The initial (current) auxin concentration of the current cell in
            au/um^2.
        ali : float
            The initial (current) AUX/LAX expression in au/um^2.

        Returns
        -------
        float
            The calculated AUX/LAX expression after synthesis and degradation.
        """
        al = self.ks * (auxini / (auxini + self.k_auxin_auxlax)) - self.kd * ali
        return al

    def calculate_pin(self, auxini: float, arri: float) -> float:
        """
        Calculate the PIN expression of the current cell based on initial auxin
        and ARR concentrations.

        Parameters
        ----------
        auxini : float
            The initial (current) auxin concentration of the current cell in
            au/um^2.
        arri : float
            The initial (current) ARR expression in au/um^2.

        Returns
        -------
        float
            The calculated PIN expression considering both synthesis and
            degradation factors.
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
        Calculate the PIN expression on one membrane based on the current cell's
        unlocalized and localized PIN expressions, the membrane direction, and
        the proportion of membrane-localized PIN in this membrane.

        Parameters
        ----------
        pini : float
            The current cell's unlocalized PIN expression.
        pindi : float
            The current cell's localized PIN expression in the specified direction.
        direction : str
            The direction of the membrane.
        pin_weight : float
            The proportion of membrane-localized PIN in this membrane.

        Returns
        -------
        float
            The calculated PIN expression on the membrane, taking into account
            localization and degradation.
        """
        weight = pin_weight
        memfrac = self.cell.get_quad_perimeter().get_memfrac(direction, self.left)
        membrane_pin = pin_weight * pini - (self.kd * pindi)
        return membrane_pin

    def calculate_neighbor_memfrac(self, neighbor: "Cell") -> float:
        """
        Calculate the fraction of the total cell membrane that is shared with a
        specified neighbor cell.

        Parameters
        ----------
        neighbor : Cell
            The neighbor cell.

        Returns
        -------
        float
            The fraction of the total cell membrane shared with the neighbor,
            rounded to six significant figures.
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

    def get_aux_exchange_across_membrane(
        self, al: float, pindi: float, neighbors: list
    ) -> dict["Cell", float]:
        """
        Calculate the amount of auxin that will be transported across each
        membrane to or from neighboring cells. This calculation takes into
        account the AUX/LAX concentration, localized PIN expression, and the
        fraction of membrane shared with each neighbor.

        Parameters
        ----------
        al : float
            The AUX/LAX concentration of the current cell.
        pindi : float
            The localized PIN expression in the specified direction of the current cell.
        neighbors : list
            The list of neighbor cells.

        Returns
        -------
        dict[Cell, float]
            A dictionary containing the amount of auxin transported across each
            membrane. Keys are neighbor cells, and values are the amounts of
            auxin transported.
        """
        neighbor_dict = {}
        for neighbor in neighbors:
            memfrac = self.calculate_neighbor_memfrac(neighbor)
            neighbor_memfrac = neighbor.get_circ_mod().calculate_neighbor_memfrac(self.cell)
            neighbor_aux = neighbor.get_circ_mod().get_auxin()
            auxin_influx = (neighbor_aux * (neighbor_memfrac)) * (al * memfrac) * self.k_al
            pin_activity = pindi * self.k_pin
            # pin_activity = ((pindi * memfrac) / (pindi * memfrac + self.k_pin)) * self.k_pin
            accessible_auxin = self.auxin * memfrac
            # print(f"accessible auxin {accessible_auxin}")
            auxin_efflux = accessible_auxin * pin_activity
            # print(f"auxin efflux {auxin_efflux}")
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
        Calculate the total amount of change in auxin concentration for the current
        cell, considering both synthesized/degraded auxin and auxin exchanged with
        neighbors.

        Parameters
        ----------
        syn_deg_auxin : float
            The amount of auxin synthesized and degraded in the current cell.
        neighbors_auxin : list
            The list of dictionaries containing the amount of auxin transported
            across each membrane for each neighbor cell.

        Returns
        -------
        float
            The total amount of change in auxin concentration for the current cell.
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
        Update the history of ARR concentrations in the cell. This method shifts
        each element in the ARR history list one position to the left and updates
        the last element with the current ARR concentration, effectively recording
        the most recent state of ARR concentration.
        """
        for i, elem in enumerate(self.arr_hist):
            if i != 0:
                self.arr_hist[i - 1] = elem
            if i == (len(self.arr_hist) - 1):
                self.arr_hist[i] = self.arr

    def update_circ_contents(self, soln: np.ndarray) -> None:
        """
        Update the circulation contents of the cell, except for auxin, based on the
        solution of the differential equations. This includes updating the concentrations
        of ARR, AUX/LAX, unlocalized PIN and membrane bound PINs.

        Parameters
        ----------
        soln : ndarray
            The solution of the differential equations, where each row represents a
            different time point and columns represent the concentrations of different
            substances at that time point.
        """
        self.arr = round_to_sf(soln[1, 1], 5)
        self.al = round_to_sf(soln[1, 2], 5)
        self.pin = round_to_sf(soln[1, 3], 5) - self.pin
        self.pina = round_to_sf(soln[1, 4], 5)
        self.pinb = round_to_sf(soln[1, 5], 5)
        self.pinl = round_to_sf(soln[1, 6], 5)
        self.pinm = round_to_sf(soln[1, 7], 5)
        self.update_arr_hist()

    def update_neighbor_auxin(self, neighbors_auxin: list[dict]) -> None:
        """
        Update the change in auxin concentrations for neighbor cells in the circulator.
        This method processes each directional exchange of auxin with neighbors and
        applies the changes to the respective neighbor cells.

        Parameters
        ----------
        neighbors_auxin : list[dict]
            The list of dictionaries containing the amount of auxin transported across
            each membrane for each neighbor cell. Each dictionary corresponds to auxin
            exchanges in one direction.
        """
        for each_dirct in neighbors_auxin:
            for neighbor in each_dirct:
                self.cell.get_sim().get_circulator().add_delta(neighbor, -each_dirct[neighbor])

    def get_neighbors(self) -> tuple:
        """
        Get the neighbors of the current cell.

        Returns
        -------
        tuple:
            A tuple containing the list of neighbors for each membrane.
        """
        neighborsa = self.cell.get_a_neighbors()
        neighborsb = self.cell.get_b_neighbors()
        neighborsl = self.cell.get_l_neighbors()
        neighborsm = self.cell.get_m_neighbors()
        return neighborsa, neighborsb, neighborsl, neighborsm

    def update_auxin(self, soln: np.ndarray) -> None:
        """
        Update auxin levels for the current cell and its neighbors based on differential equation solutions.

        This function calculates the exchange of auxin between the current cell and its neighbors based on
        the auxin transport mechanisms modeled by the differential equations. It updates the auxin levels
        by considering auxin synthesis, degradation, and exchange with neighbors.

        Parameters
        ----------
        soln : np.ndarray
            The solution to the differential equations, providing the dynamic state of the system
            including auxin levels at the current time step.

        Raises
        ------
        ValueError
            If the update results in negative auxin levels, indicating an issue with the model's
            parameters or the numerical solution.
        """
        curr_cell = self.cell

        # Retrieve neighbors for auxin exchange
        neighborsa, neighborsb, neighborsl, neighborsm = self.get_neighbors()

        # Calculate auxin exchange across membranes
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

        # Compute net auxin synthesized and degraded at this time step
        auxin_synthesized_and_degraded_this_timestep = soln[1, 0] - self.auxin

        delta_auxin = self.calculate_delta_auxin(
            auxin_synthesized_and_degraded_this_timestep, neighbors_auxin_exchange
        )

        # Update current cell auxin
        curr_cell.get_sim().get_circulator().add_delta(curr_cell, round_to_sf(delta_auxin, 5))

        # Update auxin levels in neighbor cells
        self.update_neighbor_auxin(neighbors_auxin_exchange)

    # getter functions
    def get_auxin(self) -> float:
        """
        Get the auxin concentration in the cell.

        Returns
        -------
        float
            The auxin concentration in the cell.
        """
        return self.auxin

    def get_arr(self) -> float:
        """
        Get the ARR concentration in the cell.

        Returns
        -------
        float
            The ARR concentration in the cell.
        """
        return self.arr

    def get_al(self) -> float:
        """
        Get the AUX/LAX expression in the cell.

        Returns
        -------
        float
            The AUX/LAX expression in the cell.
        """
        return self.al

    def get_arr_hist(self) -> list[float]:
        """
        Get the ARR history list.

        Returns
        -------
        list
            The ARR history list.
        """
        return self.arr_hist

    def get_auxin_w(self) -> float:
        """
        Get the weight of auxin synthesis.

        Returns
        -------
        float
            The weight of auxin synthesis.
        """
        return self.auxin_w

    def get_pin(self) -> float:
        """
        Get the unlocalized PIN expression in the cell.

        Returns
        -------
        float
            The unlocalized PIN expression in the cell.
        """
        return self.pin

    def get_apical_pin(self) -> float:
        """
        Get the PIN localized in the apical direction.

        Returns
        -------
        float
            The PIN localized in the apical direction.
        """
        return self.pina

    def get_basal_pin(self) -> float:
        """
        Get the PIN localized in the basal direction.

        Returns
        -------
        float
            The PIN localized in the basal direction.
        """
        return self.pinb

    def get_lateral_pin(self) -> float:
        """
        Get the PIN localized in the lateral direction.

        Returns
        -------
        float
            The PIN localized in the lateral direction.
        """
        return self.pinl

    def get_medial_pin(self) -> float:
        """
        Get the PIN localized in the medial direction.

        Returns
        -------
        float
            The PIN localized in the medial direction.
        """
        return self.pinm

    def get_left_pin(self) -> float:
        """
        Get the PIN localized in the left direction.

        Returns
        -------
        float
            The PIN localized in the left direction.
        """
        if self.left == "medial":
            return self.pinm
        return self.pinl

    def get_right_pin(self) -> float:
        """
        Get the PIN localized in the right direction.

        Returns
        -------
        float
            The PIN localized in the right direction.
        """
        if self.right == "medial":
            return self.pinm
        return self.pinl

    def get_state(self) -> dict[str, Any]:
        """
        Retrieve the current state of the circulate module.

        This method compiles the current state of the circulate module, encapsulating
        all relevant attributes and their values into a dictionary. This includes
        concentrations of various species, kinetic parameters, and historical data
        related to the module's operation.

        Returns
        -------
        dict[str, Any]
            A dictionary containing key-value pairs of attribute names and their
            current values. Includes concentrations (auxin, ARR, etc.), kinetic
            parameters (`k1` to `k6`, `k_s`, `k_d`), auxin weight, and the history
            of ARR concentrations.
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
            "circ_mod": "cont",
        }
        return state

    def set_auxin(self, new_aux: float) -> None:
        """
        Set the auxin concentration in the cell.

        Parameters
        ----------
        new_aux: float
            The new auxin concentration in the cell.
        """
        self.auxin = new_aux
