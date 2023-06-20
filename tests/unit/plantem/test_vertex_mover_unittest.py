import unittest
from src.plantem.sim.mover.vertex_mover import VertexMover
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

class TestVertexMover(unittest.TestCase):
    def test_add_cell_delta_val(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x)
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        simulation.setup()
        simulation.get_vertex_mover().add_cell_delta_val(cell1, 1.5)
        self.assertEqual(1.5, simulation.get_vertex_mover().get_cell_delta_val(cell1))

    def test_add_cell_b_vertices_to_vertex_deltas(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x)
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        simulation.setup()
        simulation.get_vertex_mover().add_cell_b_vertices_to_vertex_deltas(cell1, 1.5)
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v1))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v4))