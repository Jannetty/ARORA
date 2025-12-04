from typing import Protocol, Dict, List, Any, cast
from abc import ABC, abstractmethod
import numpy as np
from typing import TYPE_CHECKING
from scipy.integrate import odeint
from src.sim.util.math_helpers import round_to_sf
from src.arora_enums import PinLocalizationRulesetEnum
from src.loc.quad_perimeter.quad_perimeter import get_len_perimeter_in_common

if TYPE_CHECKING:
    from src.agent.cell import Cell


class CirculateModule(ABC):

    auxin: float
    arr: float
    auxlax: float
    pin: float
    pina: float
    pinb: float
    pinl: float
    pinm: float
    cell: "Cell"
    left: str
    right: str
    pin_weights: Dict[str, float]
    k_arr_arr: float
    k_auxin_auxlax: float
    k_auxin_pin: float
    k_arr_pin: float
    k_al: float
    k_pin: float
    auxin_w: float
    arr_hist: List[float]
    output_list: List[str] = []

    @abstractmethod
    def __init__(self, cell: "Cell", init_vals: Dict[str, Any]) -> None:

        self.cell = cell

        def get_float(key: str) -> float:
            value = init_vals.get(key)
            if value is None:
                raise ValueError(f"Missing value for key: {key}")
            return float(value)

        def get_float_list(key: str) -> List[float]:
            value = init_vals.get(key)
            if value is None:
                raise ValueError(f"Missing value for key: {key}")
            if not isinstance(value, list):
                raise ValueError(f"Expected a list for key: {key}")
            return [float(v) for v in value]

        self.auxin = get_float("auxin")
        self.output_list.append("auxin")
        self.arr = get_float("arr")
        self.output_list.append("arr")
        self.auxlax = get_float("al")
        self.output_list.append("al")
        self.pin = get_float("pin")
        self.output_list.append("pin")
        self.pina = get_float("pina")
        self.output_list.append("pina")
        self.pinb = get_float("pinb")
        self.output_list.append("pinb")
        self.pinl = get_float("pinl")
        self.output_list.append("pinl")
        self.pinm = get_float("pinm")
        self.output_list.append("pinm")
        self.k_arr_arr = get_float("k1")
        self.output_list.append("k1")
        self.k_auxin_auxlax = get_float("k2")
        self.output_list.append("k2")
        self.k_auxin_pin = get_float("k3")
        self.output_list.append("k3")
        self.k_arr_pin = get_float("k4")
        self.output_list.append("k4")
        self.k_al = get_float("k5")
        self.output_list.append("k5")
        self.k_pin = get_float("k6")
        self.output_list.append("k6")
        self.auxin_w = get_float("auxin_w")
        self.output_list.append("auxin_w")
        self.arr_hist = get_float_list("arr_hist")
        self.output_list.append("arr_hist")
        self.left = self.cell.get_quad_perimeter().get_left_lateral_or_medial(
            self.cell.get_sim().get_root_midpointx()
        )
        self.right = self.cell.get_quad_perimeter().get_right_lateral_or_medial(
            self.cell.get_sim().get_root_midpointx()
        )
        self.pin_weights = self.initialize_pin_weights()

    def initialize_pin_weights(self) -> Dict[str, float]:
        """
        Initialize PIN weights for each membrane based on initial PIN distribution.

        Returns
        -------
        dict[str, float]
            A dictionary mapping membrane identifiers ('a' for apical, 'b' for basal,
            'l' for lateral, 'm' for medial) to their respective initial PIN weights.
        """
        pin_weights_dict = {}
        pin_vals = [
            self.get_apical_pin(),
            self.get_basal_pin(),
            self.get_lateral_pin(),
            self.get_medial_pin(),
        ]
        pin_sum = sum(pin_vals)
        if pin_sum == 0:
            return {"a": 0, "b": 0, "l": 0, "m": 0}
        else:
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
        f2 = self.calculate_auxlax(auxini, ali)
        # pin
        f3 = self.calculate_pin(auxini, arri)
        # neighbor pin
        f4 = self.calculate_membrane_pin(pini, pinai, "a", cast(float, self.pin_weights.get("a")))
        f5 = self.calculate_membrane_pin(pini, pinbi, "b", cast(float, self.pin_weights.get("b")))
        f6 = self.calculate_membrane_pin(pini, pinli, "l", cast(float, self.pin_weights.get("l")))
        f7 = self.calculate_membrane_pin(pini, pinmi, "m", cast(float, self.pin_weights.get("m")))

        return [f0, f1, f2, f3, f4, f5, f6, f7]

    def solve_equations(self, dt_hours: float) -> np.ndarray:
        """
        Advance the ODEs by dt_hours of biological time.

        Parameters
        ----------
        dt_hours : float
            Biological time elapsed this simulation tick (in hours).

        Returns
        -------
        ndarray
            Solution of the ODEs evaluated at t = 0 and t = dt_hours.
            The last row (soln[-1]) is the state at t = dt_hours.
        """
        y0 = [
            self.get_auxin(),
            self.get_arr(),
            self.get_auxlax(),
            self.get_pin(),
            self.get_apical_pin(),
            self.get_basal_pin(),
            self.get_lateral_pin(),
            self.get_medial_pin(),
        ]

        t = np.array([0.0, dt_hours], dtype=float)
        soln = odeint(self.f, y0, t)
        return soln

    def update(self) -> None:
        """
        Update circulation contents based on current PIN weights and differential equations.
        """
        # Retrieve current PIN weights from the cell
        self.pin_weights = self.cell.get_pin_weights()
        assert round_to_sf(sum(self.pin_weights.values()), 2) == 1.0, "PIN weights sum to 1.0"

        # How much biological time does one simulation tick represent?
        dt_hours = self.cell.get_sim().get_timestep_hours()

        # Solve the ODEs over this biological time window
        soln = self.solve_equations(dt_hours=dt_hours)

        # Update model states based on the solution at t = dt_hours
        self.update_auxin(soln)
        self.update_circ_contents(soln)

    @abstractmethod
    def calculate_auxin(self, auxin: float) -> float:
        pass

    @abstractmethod
    def calculate_arr(self, arr: float) -> float:
        pass

    @abstractmethod
    def calculate_auxlax(self, auxin: float, auxlax: float) -> float:
        pass

    @abstractmethod
    def calculate_pin(self, auxin: float, arr: float) -> float:
        pass

    @abstractmethod
    def calculate_membrane_pin(
        self, pin: float, membrane_pin: float, direction: str, weight: float
    ) -> float:
        pass

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
        self, al: float, pindi: float, neighbors: list, dt_hours: float
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

            # Per-hour rates:
            influx_rate = neighbor_aux * al * memfrac * self.k_al
            pin_activity = pindi * self.k_pin
            accessible_auxin = self.auxin * memfrac
            efflux_rate = accessible_auxin * pin_activity

            # Integrate over dt_hours
            auxin_influx = influx_rate * dt_hours
            auxin_efflux = efflux_rate * dt_hours

            if any(x in (float("inf"), float("-inf")) for x in (auxin_influx, auxin_efflux)):
                print(f"cell {self.cell.get_c_id()} neighbor {neighbor.get_c_id()}")
                print(f"neighbor's auxin {auxin_influx}, self aux out {auxin_efflux}")
                raise ValueError("Negative auxin")

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

    # TODO: (maybe) Make this abstract and implement in each circ mod
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
        last = soln[-1]
        self.arr    = round_to_sf(last[1], 5)
        self.auxlax = round_to_sf(last[2], 5)
        self.pin    = round_to_sf(last[3], 5)
        self.pina   = round_to_sf(last[4], 5)
        self.pinb   = round_to_sf(last[5], 5)
        self.pinl   = round_to_sf(last[6], 5)
        self.pinm   = round_to_sf(last[7], 5)
        self.update_arr_hist()

        rules = self.cell.get_sim().get_pin_loc_rules()
        if rules == PinLocalizationRulesetEnum.IMPOSED:
            # For imposed, overwrite pina/pinb/pinl/pinm with the spatial pattern,
            # but DO NOT touch self.pin_weights (those already came from cell)
            pins_frac = self.cell.get_pin_weights()  # already normalized
            self.pina = pins_frac["a"]
            self.pinb = pins_frac["b"]
            self.pinl = pins_frac["l"]
            self.pinm = pins_frac["m"]
            self.auxlax = 1

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
        dt_hours = self.cell.get_sim().get_timestep_hours()

        # Retrieve neighbors for auxin exchange
        neighborsa, neighborsb, neighborsl, neighborsm = self.get_neighbors()

        reg = self.get_pin_reg_factor()

        # Calculate auxin exchange across membranes
        auxina_exchange = self.get_aux_exchange_across_membrane(
            self.auxlax,
            reg * self.cell.get_pin_weights()["a"],
            neighborsa,
            dt_hours
        )
        auxinb_exchange = self.get_aux_exchange_across_membrane(
            self.auxlax,
            reg * self.cell.get_pin_weights()["b"],
            neighborsb,
            dt_hours
        )
        auxinl_exchange = self.get_aux_exchange_across_membrane(
            self.auxlax,
            reg * self.cell.get_pin_weights()["l"],
            neighborsl,
            dt_hours
        )
        auxinm_exchange = self.get_aux_exchange_across_membrane(
            self.auxlax,
            reg * self.cell.get_pin_weights()["m"],
            neighborsm,
            dt_hours
        )
        neighbors_auxin_exchange = [
            auxina_exchange,
            auxinb_exchange,
            auxinl_exchange,
            auxinm_exchange,
        ]

        # Compute net auxin synthesized and degraded at this time step
        # Net auxin change over dt_hours from synthesis/degradation
        aux_new = soln[-1, 0]
        auxin_synthesized_and_degraded_this_timestep = aux_new - self.auxin

        delta_auxin = self.calculate_delta_auxin(
            auxin_synthesized_and_degraded_this_timestep, neighbors_auxin_exchange
        )

        # Update current cell auxin
        curr_cell.get_sim().get_circulator().add_delta(curr_cell, round_to_sf(delta_auxin, 5))

        # Update auxin levels in neighbor cells
        self.update_neighbor_auxin(neighbors_auxin_exchange)

        # delta_from_syn_deg = aux_new - self.auxin
        # delta_from_neighbors = delta_from_neighbors = sum(sum(d.values()) for d in neighbors_auxin_exchange)
        # print(self.cell.c_id,
        #     "aux:", self.auxin,
        #     "Δ_syn_deg:", delta_from_syn_deg,
        #     "Δ_neighbors:", delta_from_neighbors)


    def get_directional_pattern(self, direction: str) -> float:
        return self.cell.get_pin_weights()[direction]  # "a", "b", "l", "m"

    def get_pin_reg_factor(self) -> float:
        """
        Compute a regulatory factor for PIN-mediated auxin efflux based on
        the current auxin and ARR levels.

        - Auxin ACTIVATES export (increasing factor with auxin, saturating).
        - ARR INHIBITS export (decreasing factor with ARR, saturating).

        The returned value is in [0, 1] and is dimensionless.
        """
        # Guard against negatives / NaNs
        aux = max(float(self.auxin), 0.0)
        arr = max(float(self.arr), 0.0)

        # TODO: Restructure the circulation modules so that this is how PIN is regulated!!!
        # Simple “Hill-like” saturating activation by auxin:
        # aux_term ~ 0 when aux ~ 0, aux_term -> 1 as aux grows large
        aux_term = aux / (aux + 1.0)

        # Simple saturating inhibition by ARR:
        # arr_term ~ 1 when arr ~ 0, arr_term -> 0 as arr grows large
        arr_term = 1.0 / (1.0 + arr)

        reg = aux_term * arr_term

        # Floating point protection
        if reg < 0.0:
            reg = 0.0
        elif reg > 1.0:
            reg = 1.0

        return reg

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

    def get_auxlax(self) -> float:
        """
        Get the AUX/LAX expression in the cell.

        Returns
        -------
        float
            The AUX/LAX expression in the cell.
        """
        return self.auxlax

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

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        pass

    def set_auxin(self, new_aux: float) -> None:
        """
        Set the auxin concentration in the cell.

        Parameters
        ----------
        new_aux: float
            The new auxin concentration in the cell.
        """
        self.auxin = new_aux

    def get_pin_weights(self) -> dict[str, float]:
        """
        Get the weights of PIN localized in each membrane direction. Pin weights sum to 1.

        Returns
        -------
        dict[str, float]
            A dictionary mapping membrane identifiers ('a' for apical, 'b' for basal,
            'l' for lateral, 'm' for medial) to their respective PIN weights.
        """
        return self.pin_weights

    def update_left_right(self) -> None:
        """
        Update the left and right attributes of the current cell.

        This method updates the left and right attributes of the current cell based on the
        current midpoint of the cell's perimeter relative to the root midpoint.
        """
        self.left = self.cell.get_quad_perimeter().get_left_lateral_or_medial(
            self.cell.get_sim().get_root_midpointx()
        )
        self.right = self.cell.get_quad_perimeter().get_right_lateral_or_medial(
            self.cell.get_sim().get_root_midpointx()
        )
