from typing import TYPE_CHECKING, Any
from src.agent.circ_module import CirculateModule
import pandas as pd

if TYPE_CHECKING:
    from src.agent.cell import Cell


class AbsLocCirculateModule(CirculateModule):
    """
    Circulation module that check's a cell's centroid and assigns PIN distribution based on its
    x location and y distance from the root tip.
    """

    pin_refs: pd.DataFrame

    def __init__(self, cell: "Cell", init_vals: dict[str, Any]):
        super().__init__(cell, init_vals)
        self.pin_refs = pd.read_csv("src/agent/pin_refs.csv")
        self.pin_refs["centroid"] = self.pin_refs["centroid"].apply(eval)

    def calculate_auxin(self, auxini: float) -> float:
        auxin = (self.ks * self.auxin_w) - (self.kd * auxini)
        return auxin

    def calculate_arr(self, arri: float) -> float:
        arr = (self.ks * (self.k_arr_arr / (self.arr_hist[0] + self.k_arr_arr))) - (self.kd * arri)
        return arr

    def calculate_auxlax(self, auxlax: float) -> float:
        pass

    def calculate_pin(self, pin: float) -> float:
        pass

    def calculate_membrane_pin(self, pin: float, direction: str, weight: float) -> float:
        pass

    def get_state(self) -> dict[str, Any]:
        pass
