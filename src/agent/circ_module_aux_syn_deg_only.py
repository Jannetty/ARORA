from typing import Any, TYPE_CHECKING
from src.agent.circ_module import CirculateModule

if TYPE_CHECKING:
    from src.agent.cell import Cell


class CirculateModuleAuxinSynDegOnly(CirculateModule):
    ks_aux: float
    kd_aux: float

    def __init__(self, cell: "Cell", init_vals: dict[str, Any]):
        super().__init__(cell, init_vals)

        def get_float(key: str) -> float:
            value = init_vals.get(key)
            if value is None:
                raise ValueError(f"Missing value for key: {key}")
            return float(value)

        # Get auxin synthesis and degradation rates
        self.ks_aux = get_float("ks_aux")
        self.output_list.append("ks_aux")
        self.kd_aux = get_float("kd_aux")
        self.output_list.append("kd_aux")
        # Zero out all species except auxin
        self.arr = 0
        self.auxlax = 0
        self.pin = 0
        self.pina = 0
        self.pinb = 0
        self.pinl = 0
        self.pinm = 0

    def calculate_auxin(self, auxini: float) -> float:
        auxin = (self.ks_aux * self.auxin_w) - (self.kd_aux * auxini)
        return auxin

    def calculate_arr(self, arri: float) -> float:
        return 0

    def calculate_auxlax(self, auxin: float, auxlax: float) -> float:
        return 0

    def calculate_pin(self, auxin: float, arr: float) -> float:
        return 0

    def calculate_membrane_pin(
        self, pin: float, membrane_pin: float, direction: str, weight: float
    ) -> float:
        return 0

    def get_state(self) -> dict[str, Any]:
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
            "auxin_w": self.auxin_w,
            "arr_hist": self.arr_hist,
            "circ_mod": "aux_syndegonly",
        }
        return state
