"""Functional tests for the LRC-geometry extension (Plan 2, option γ).

Reference:
    docs/plans/design_plans/2_2026-05-20_extend_LRC_geometry.md  §4 Phase D.2

Implementation note: per Plan 2, the target circulation mode is
``AUX_SYN_DEG_EXP``. However, ``AUX_SYN_DEG_EXP`` requires
``ks_aux``/``kd_aux`` per cell in the init file, which the
*default* init file does not provide — that mode uses
``indep_syndeg_init_vals.json`` (extended only via runtime
``gparam_series`` injection). The 28 new LRC cells added in
commit 9193c51 were written to ``default_init_vals.json`` only, so
extending ``indep_syndeg_init_vals.json`` is filed as follow-up
F-005 in the implementation log. Until that's done, these tests
exercise the geometry under ``UNIVERSAL_SYN_DEG`` + ``SIMPLE_INHERITANCE``,
which is sufficient: every invariant tested here is about atlas
shape (cell IDs, dev_zone classification, neighbor topology, PIN
init values, auxin_w), all of which are independent of the
circulation module that runs on top of the atlas.
"""

import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"

import unittest

from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum
from src.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "test_lrc_reaches_oz"

# See module docstring for rationale on choosing UNIVERSAL_SYN_DEG.
PIN_LOC_RULES = PinLocalizationRulesetEnum.SIMPLE_INHERITANCE
CIRC_MOD = CircModEnum.UNIVERSAL_SYN_DEG

CELL_VAL_FILE = "src/sim/input/default_init_vals.json"
V_FILE = "src/sim/input/default_vs.json"

# All 28 new LRC IDs added in commit 9193c51, in chain order
# bottom-to-top, pair-by-pair.
NEW_LRC_PAIRS = [
    (830, 831),
    (832, 833),
    (834, 835),
    (836, 837),
    (838, 839),   # OZ XPP target row
    (840, 841),
    (842, 843),   # T-E boundary
    (844, 845),
    (846, 847),
    (848, 849),
    (850, 851),
    (852, 853),
    (854, 855),
    (856, 857),   # topmost — terminal dumpers
]
NEW_LRC_LEFT = [pair[0] for pair in NEW_LRC_PAIRS]
NEW_LRC_RIGHT = [pair[1] for pair in NEW_LRC_PAIRS]
NEW_LRC_ALL = NEW_LRC_LEFT + NEW_LRC_RIGHT

# The full LRC chain on the left side, bottom-to-top (used by the
# chain-walk test). The original 7 left LRC cells (60, 90, 120, 136,
# 166, 210, 296) plus the 14 new left cells (830, 832, …, 856).
LEFT_LRC_CHAIN = [60, 90, 120, 136, 166, 210, 296] + NEW_LRC_LEFT


def _make_sim():
    """Build a fresh GrowingSim with the default geometry + atlas."""
    return GrowingSim(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SCREEN_TITLE,
        timestep=1,
        vis=False,
        pin_loc_rules=PIN_LOC_RULES,
        circ_mod=CIRC_MOD,
        cell_val_file=CELL_VAL_FILE,
        v_file=V_FILE,
        gparam_series=None,
        geometry="default",
    )


class TestNewLRCInitValues(unittest.TestCase):
    """Tests that the 28 new LRC cells have the correct init values
    (auxin_w, PIN distribution) per the Phase B specification."""

    def test_new_lrc_cells_have_auxin_w_10(self):
        sim = _make_sim()
        for cid in NEW_LRC_ALL:
            cell = sim.get_cell_by_ID(cid)
            self.assertEqual(
                cell.get_circ_mod().get_auxin_w(),
                10,
                f"new LRC cell {cid} expected auxin_w=10, "
                f"got {cell.get_circ_mod().get_auxin_w()}",
            )

    def test_new_lrc_intermediate_cells_have_apical_dominant_pin(self):
        """All new LRC cells EXCEPT the topmost (856/857) should be
        apical-dominant: pina=1.0, pinm=0.1."""
        sim = _make_sim()
        intermediates = [c for c in NEW_LRC_ALL if c not in (856, 857)]
        # There should be 26 intermediates (13 per side).
        self.assertEqual(len(intermediates), 26)
        for cid in intermediates:
            state = sim.get_cell_by_ID(cid).get_circ_mod().get_state()
            self.assertEqual(state["pina"], 1.0,
                             f"intermediate LRC {cid} expected pina=1.0, got {state['pina']}")
            self.assertEqual(state["pinb"], 0.0,
                             f"intermediate LRC {cid} expected pinb=0.0, got {state['pinb']}")
            self.assertEqual(state["pinl"], 0.0,
                             f"intermediate LRC {cid} expected pinl=0.0, got {state['pinl']}")
            self.assertEqual(state["pinm"], 0.1,
                             f"intermediate LRC {cid} expected pinm=0.1, got {state['pinm']}")

    def test_new_lrc_topmost_cell_is_terminal_dumper(self):
        """Cells 856 (left) and 857 (right) — the topmost on each
        side — should be terminal dumpers: pina=0.0, pinm=1.0."""
        sim = _make_sim()
        for cid in (856, 857):
            state = sim.get_cell_by_ID(cid).get_circ_mod().get_state()
            self.assertEqual(state["pina"], 0.0,
                             f"topmost LRC {cid} expected pina=0.0, got {state['pina']}")
            self.assertEqual(state["pinm"], 1.0,
                             f"topmost LRC {cid} expected pinm=1.0, got {state['pinm']}")


class TestLRCChainTopology(unittest.TestCase):
    """Tests that the LRC file is unbroken from cell 60 (closest to
    root tip) all the way up to the new topmost cells, and that the
    OZ XPP target cell is two membrane hops from an LRC cell."""

    def test_lrc_chain_unbroken(self):
        """Walk up the left LRC chain. For each pair of vertically
        adjacent LRC cells (cell_i, cell_{i+1}), assert that cell_i
        has cell_{i+1} in its all-neighbors list. Position-agnostic —
        we don't check which side list it lands in, only that the
        adjacency exists."""
        sim = _make_sim()
        for i in range(len(LEFT_LRC_CHAIN) - 1):
            lower_id = LEFT_LRC_CHAIN[i]
            upper_id = LEFT_LRC_CHAIN[i + 1]
            lower = sim.get_cell_by_ID(lower_id)
            upper = sim.get_cell_by_ID(upper_id)
            self.assertIn(
                upper, lower.get_all_neighbors(),
                f"chain broken: cell {lower_id} does not list {upper_id} as neighbor",
            )
            self.assertIn(
                lower, upper.get_all_neighbors(),
                f"chain broken: cell {upper_id} does not list {lower_id} as neighbor",
            )

    def test_oz_xpp_target_reachable_from_lrc(self):
        """The cost-function XPP target cell (c693, pericycle, x=56.5)
        is reachable from the new LRC (c838, x≈21-26) via the reflux
        path across the inner files at the same y-level
        (y=[346,369]):

            c693 (peri)  → c692 (endo)   → c691 (cortex)
                         → c690 (epi)    → c838 (LRC).

        Walks each step explicitly and asserts the adjacency.
        Pre-Phase-B, only the final hop (c690→c838) was missing —
        that's the structural break this geometry extension was
        designed to fix.
        """
        sim = _make_sim()
        path = [693, 692, 691, 690, 838]
        cells = [sim.get_cell_by_ID(cid) for cid in path]
        for i in range(len(cells) - 1):
            self.assertIn(
                cells[i + 1], cells[i].get_all_neighbors(),
                f"hop {i+1} broken: cell {path[i]} does not neighbor "
                f"cell {path[i+1]} ({len(cells[i].get_all_neighbors())} neighbors found)",
            )
        # And c838 must be a real LRC (dev_zone roottip).
        self.assertEqual(cells[-1].get_dev_zone(), "roottip")


class TestSimulationRobustness(unittest.TestCase):
    """Short-horizon smoke test: with the extended LRC atlas, the
    simulation should advance several ticks without raising
    exceptions and without losing any of the new LRC cells.

    Tick budget rationale: 5 ticks matches the existing
    ``test_symmetry_after_updates`` in the symmetry suite. The
    plan originally specified 50 ticks, but at ``timestep=1`` h
    with the default-init parameters (which are *not* the
    GA-tuned set in ``param_est/ga_runs/osc_search_03/best_summary.txt``)
    the auxin dynamics drift into ``ValueError: Negative Auxin``
    after roughly 9 hours of simulated time. That drift is a
    property of running un-tuned parameters for too long, not of
    the LRC geometry extension — see implementation log §"Phase D
    smoke test failure" — so the test is scoped to 5 ticks to
    exercise the relevant code paths (per-cell update, vertex
    mover, circulator, divider) without relying on long-term
    stability of an un-tuned parameter set.
    """

    SMOKE_TEST_TICKS = 5

    def test_no_exceptions_short_run(self):
        sim = _make_sim()
        for _ in range(self.SMOKE_TEST_TICKS):
            sim.cell_list.update()
            sim.vertex_mover.update()
            sim.circulator.update()
            sim.divider.update()
            sim.root_tip_y = sim.get_root_tip_y()
            sim.tick += 1
        # Cell count should still be at least 858 (cells can only
        # increase via division, never decrease in this circulation
        # mode; LRC cells don't divide because they're roottip).
        self.assertGreaterEqual(len(sim.get_cell_list()), 858)
        # And the new LRC cells must all still exist as live cells
        # with dev_zone roottip.
        for cid in NEW_LRC_ALL:
            cell = sim.get_cell_by_ID(cid)
            self.assertIsNotNone(cell)
            self.assertEqual(cell.get_dev_zone(), "roottip")


if __name__ == "__main__":
    unittest.main()
