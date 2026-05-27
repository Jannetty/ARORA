from typing import Any, TYPE_CHECKING
from src.agent.circ_module_imposed_pin_arr_activity import (
    CirculateModuleImposedPinArrActivity,
)

if TYPE_CHECKING:
    from src.agent.cell import Cell


class CirculateModuleImposedPinNoArr(CirculateModuleImposedPinArrActivity):
    """
    VDB-aligned circulation module: imposed PIN localisation, no ARR feedback.

    ARR is structurally absent. dARR/dt ≡ 0 and PIN transport is always
    unrestricted (reg = 1.0). Oscillations, if they arise, must come purely
    from the auxin reflux loop and growth-driven cell-size alternations —
    the mechanism described in van den Berg et al. 2021.

    Inherits all initialisation and auxin/transport logic from
    CirculateModuleImposedPinArrActivity. Only calculate_arr,
    get_pin_reg_factor, and get_state are overridden.
    """

    def __init__(self, cell: "Cell", init_vals: dict[str, Any]):
        super().__init__(cell, init_vals)

    def calculate_arr(self, arri: float) -> float:
        # ARR structurally absent; arr stays at its initial value of 0.0.
        return 0.0

    def get_pin_reg_factor(self) -> float:
        # No ARR → no PIN inhibition → unrestricted transport.
        return 1.0

    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        state["circ_mod"] = "imposed_pin_no_arr"
        return state
