from typing import Any, TYPE_CHECKING
from src.agent.circ_module import CirculateModule
from src.arora_enums import PinLocalizationRulesetEnum

if TYPE_CHECKING:
    from src.agent.cell import Cell


class CirculateModuleImposedPinArrActivity(CirculateModule):
    """
    Circulation module for imposed PIN localization with dynamic transport activity.

    Intended behavior:
    - PIN localization is imposed by Cell.get_pin_weights() (spatial template).
    - ARR is dynamic and modulates transport activity via get_pin_reg_factor().
    - Auxin synthesis/degradation is dynamic.
    - AUX/LAX is fixed to 1 under imposed PIN rules (handled in base class update).
    """

    ks_aux: float
    kd_aux: float
    ks_arr: float
    kd_arr: float

    def __init__(self, cell: "Cell", init_vals: dict[str, Any]):
        super().__init__(cell, init_vals)
        if cell.get_sim().get_pin_loc_rules() != PinLocalizationRulesetEnum.IMPOSED:
            raise NotImplementedError(
                "CirculateModuleImposedPinArrActivity requires imposed PIN localization."
            )

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

        # Keep transporter abundance dynamics off; localization/activity are handled elsewhere.
        self.pin = 0.0
        self.pina = 0.0
        self.pinb = 0.0
        self.pinl = 0.0
        self.pinm = 0.0
        self.auxlax = 1.0

    def calculate_auxin(self, auxini: float) -> float:
        return (self.ks_aux * self.auxin_w) - (self.kd_aux * auxini)

    def calculate_arr(self, arri: float) -> float:
        """
        ARR dynamics with auxin-dependent induction and delayed self-repression.

        This coupling is the core requirement for oscillations to emerge:

        dARR/dt = ks_arr * [A/(A + k3)] * [k1/(ARR(t-τ) + k1)] - kd_arr * ARR

        - Auxin (A) activates ARR synthesis via a Hill function (TIR1/AFB pathway).
          k3 (k_auxin_pin) is the auxin half-saturation constant.
        - Delayed ARR (arr_hist[0], τ ticks ago) provides self-repression, which
          combined with the delay creates the oscillatory instability.
        - Without the auxin-coupling term, ARR dynamics are decoupled from auxin
          and cannot drive auxin oscillations regardless of parameter values.

        Notes
        -----
        self.auxin is used as a quasi-static approximation for the auxin
        concentration during the ODE integration interval (valid for short dt).
        """
        aux = max(float(self.auxin), 0.0)
        arr_delayed = max(float(self.arr_hist[0]), 0.0)

        # Auxin activates ARR synthesis (k3 = k_auxin_pin, from base class init)
        auxin_activation = aux / (aux + self.k_auxin_pin)

        # Delayed ARR self-repression (k1 = k_arr_arr)
        arr_self_repression = self.k_arr_arr / (arr_delayed + self.k_arr_arr)

        return (self.ks_arr * auxin_activation * arr_self_repression) - (
            self.kd_arr * arri
        )

    def get_pin_reg_factor(self) -> float:
        """
        ARR-mediated PIN transport inhibition, scaled to the actual ARR steady-state.

        k_half is set to the expected ARR steady-state at the current auxin level:

            k_half = ks_arr × [A / (A + k3)] / kd_arr

        This is the ARR_ss that calculate_arr() converges to when arr_hist is also
        at ARR_ss (ignoring the self-repression term for the half-saturation estimate,
        which is a valid first-order approximation).

        Why this matters
        ----------------
        The previous implementation used k_half = ks_arr/kd_arr, which ignores the
        auxin-activation factor [A/(A+k3)].  For typical OZ XPP auxin levels
        (~5–20 a.u.) and k3 = 42.5, this factor is only ~0.1–0.32, so the
        ACTUAL ARR steady-state is 3–10× smaller than k_half.  As a result
        reg = k_half/(ARR+k_half) ≈ 0.8–0.9 at steady state, leaving very little
        dynamic range for oscillations to modulate PIN activity.

        With the corrected k_half, reg ≈ 0.5 at steady state regardless of parameter
        values.  Deviations of ARR above/below steady state (driven by the delayed
        self-repression) then translate directly to PIN inhibition above/below 50%,
        creating the ~[-50%, +50%] dynamic range needed for auxin oscillations.

        Returns a dimensionless factor in [0, 1]:
          - → 1.0  when ARR << ARR_ss  (low ARR, minimal inhibition)
          - ≈ 0.5  when ARR ≈ ARR_ss   (half-maximal inhibition at steady state)
          - → 0    when ARR >> ARR_ss  (strong inhibition)
        """
        arr = max(float(self.arr), 0.0)
        aux = max(float(self.auxin), 0.0)

        # Auxin-activation factor (same as in calculate_arr)
        auxin_activation = aux / (aux + self.k_auxin_pin + 1e-10)

        # k_half = ARR steady-state estimate (1st-order: ignores self-repression)
        # Bounded below to prevent division-by-zero when auxin ≈ 0
        k_half = self.ks_arr * auxin_activation / max(self.kd_arr, 1e-9)
        k_half = max(k_half, 1e-9)

        reg = k_half / (arr + k_half)
        return max(0.0, min(1.0, reg))

    def calculate_auxlax(self, auxin: float, auxlax: float) -> float:
        return 0.0

    def calculate_pin(self, auxin: float, arr: float) -> float:
        return 0.0

    def calculate_membrane_pin(
        self, pin: float, membrane_pin: float, direction: str, weight: float
    ) -> float:
        return 0.0

    def get_state(self) -> dict[str, Any]:
        return {
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
            "auxin_w": self.auxin_w,
            "arr_hist": self.arr_hist,
            "circ_mod": "imposed_pin_arr_activity",
        }
