import unittest
from src.plantem.sim.divider.divider import Divider
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim
from src.plantem.loc.vertex.vertex import Vertex

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

class TestVertexMover(unittest.TestCase):
    init_vals = {"auxin": 2, "arr": 3, "al": 3, "pina": 0.5, "pinb": 0.7,
                "pinl": 0.4, "pinm": 0.2, "k_arr_arr": 1, "k_auxin_auxlax": 1,
                "k_auxin_pin": 1, "k_arr_pin": 1, "ks": 0.005, "kd": 0.0015}
    
    def test_get_new_vs(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], self.init_vals)
        new_vs = simulation.get_divider().get_new_vs(cell1)
        self.assertEqual([100,200], new_vs[0].get_xy())
        self.assertEqual([300,200], new_vs[1].get_xy())