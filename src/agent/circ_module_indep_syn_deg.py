import numpy as np
from typing import TYPE_CHECKING, cast, Any, List
from scipy.integrate import odeint
from src.sim.util.math_helpers import round_to_sf
from src.agent.circ_module import CirculateModule

if TYPE_CHECKING:
    from src.agent.cell import Cell


class CirculateModuleIndSynDeg(CirculateModule):

    ks_aux: float
    kd_aux: float
    ks_arr: float
    kd_arr: float
    ks_pinu: float  # unlocalized pin
    kd_pinu: float  # unlocalized pin
    kd_pinloc: float  # localized pin
    ks_auxlax: float
    kd_auxlax: float

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
            Indicates whether the cell is currently growing. Not used here, saved in Cell constructor.
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

        self.ks_aux = get_float("ks_aux")
        self.output_list.append("ks_aux")
        self.kd_aux = get_float("kd_aux")
        self.output_list.append("kd_aux")
        self.ks_arr = get_float("ks_arr")
        self.output_list.append("ks_arr")
        self.kd_arr = get_float("kd_arr")
        self.output_list.append("kd_arr")
        self.ks_pinu = get_float("ks_pinu")
        self.output_list.append("ks_pinu")
        self.kd_pinu = get_float("kd_pinu")
        self.output_list.append("kd_pinu")
        self.kd_pinloc = get_float("kd_pinloc")
        self.output_list.append("kd_pinloc")
        self.ks_auxlax = get_float("ks_auxlax")
        self.output_list.append("ks_auxlax")
        self.kd_auxlax = get_float("kd_auxlax")
        self.output_list.append("kd_auxlax")

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
        auxin = (self.ks_aux * self.auxin_w) - (self.kd_aux * auxini)
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
        arr = (self.ks_arr * (self.k_arr_arr / (self.arr_hist[0] + self.k_arr_arr))) - (
            self.kd_arr * arri
        )
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
        al = self.ks_auxlax * (auxini / (auxini + self.k_auxin_auxlax)) - self.kd_auxlax * ali
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
            self.ks_pinu
            * (self.k_arr_pin / (arri + self.k_arr_pin))
            * (auxini / (auxini + self.k_auxin_pin))
            - self.kd_pinu * self.pin
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
        membrane_pin = pin_weight * pini - (self.kd_pinloc * pindi)
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
            parameters (`k1` to `k6`, ks_aux, kd_aux, ks_arr, kd_arr, ks_pinu, kd_pinu, kd_pinloc, ks_auxlax, kd_auxlax`),
            auxin weight, and the history of ARR concentrations.
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
            "ks_aux": self.ks_aux,
            "kd_aux": self.kd_aux,
            "ks_arr": self.ks_arr,
            "kd_arr": self.kd_arr,
            "ks_pinu": self.ks_pinu,
            "kd_pinu": self.kd_pinu,
            "kd_pinloc": self.kd_pinloc,
            "ks_auxlax": self.ks_auxlax,
            "kd_auxlax": self.kd_auxlax,
            "auxin_w": self.auxin_w,
            "arr_hist": self.arr_hist,
            "circ_mod": "indep_syndeg",
        }
        return state
