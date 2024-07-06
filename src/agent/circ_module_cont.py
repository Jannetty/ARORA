import numpy as np
from typing import Any, Dict, List, Optional, TYPE_CHECKING, cast
from scipy.integrate import odeint
from src.sim.util.math_helpers import round_to_sf
from src.agent.circ_module import CirculateModule

if TYPE_CHECKING:
    from src.agent.cell import Cell


class BaseCirculateModuleCont(CirculateModule):
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

    ks: float
    kd: float

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
            Indicates whether the cell is currently growing. Not saved here, used in Cell constructor.
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
        super().__init__(cell, init_vals)

        def get_float(key: str) -> float:
            value = init_vals.get(key)
            if value is None:
                raise ValueError(f"Missing value for key: {key}")
            return float(value)

        self.ks = get_float("k_s")
        self.kd = get_float("k_d")

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

    def calculate_auxlax(self, auxini: float, ali: float) -> float:
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
            "al": self.auxlax,
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
