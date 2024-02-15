import os
import unittest
from src.plantem.sim.mover.vertex_mover import VertexMover
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.agent.cell import Cell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class TestVertexMover(unittest.TestCase):

    init_vals = {
        "auxin": 2,
        "arr": 3,
        "al": 3,
        "pina": 0.5,
        "pinb": 0.7,
        "pinl": 0.4,
        "pinm": 0.2,
        "k1": 1,
        "k2": 1,
        "k3": 1,
        "k4": 1,
        "k_s": 0.005,
        "k_d": 0.0015,
        "growing": True,
        "circ_mod": "cont",
    }

    @classmethod
    def setUpClass(cls):
        super(TestVertexMover, cls).setUpClass()
        os.environ["ARCADE_HEADLESS"] = "True"

    @classmethod
    def teadDownClass(cls):
        del os.environ["ARCADE_HEADLESS"]
        super(TestVertexMover, cls).tearDownClass()

    def test_add_cell_delta_val(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        simulation.setup()
        simulation.get_vertex_mover().add_cell_delta_val(cell1, 1.5)
        self.assertEqual(1.5, simulation.get_vertex_mover().get_cell_delta_val(cell1))

    def test_add_cell_b_vertices_to_vertex_deltas(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        simulation.setup()
        simulation.get_vertex_mover().add_cell_b_vertices_to_vertex_deltas(cell1, 1.5)
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v1))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v4))

    def test_propogate_deltas(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v5 = Vertex(10, 40)
        v6 = Vertex(30, 40)
        a_neighbor = Cell(
            simulation, [v2, v3, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        simulation.setup()
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(b_neighbor)
        a_neighbor.add_neighbor(cell1)
        self.assertEqual(a_neighbor.get_b_neighbors(), [cell1])
        self.assertEqual(cell1.get_b_neighbors(), [b_neighbor])
        self.assertEqual(cell1.get_a_neighbors(), [a_neighbor])
        simulation.get_vertex_mover().add_cell_delta_val(a_neighbor, 1.5)
        simulation.get_vertex_mover().propogate_deltas([a_neighbor])
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v1))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v2))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v3))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v4))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v9))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v10))

    def test_execute_vertex_movement(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v5 = Vertex(10, 40)
        v6 = Vertex(30, 40)
        a_neighbor = Cell(
            simulation, [v2, v3, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        simulation.setup()
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(b_neighbor)
        a_neighbor.add_neighbor(cell1)
        simulation.get_vertex_mover().add_cell_delta_val(a_neighbor, 1.5)
        simulation.get_vertex_mover().propogate_deltas([a_neighbor])
        simulation.get_vertex_mover().execute_vertex_movement(
            min(simulation.get_vertex_mover().vertex_deltas.values())
        )
        self.assertAlmostEqual(10 + 1.5, v1.get_y())
        self.assertAlmostEqual(30 + 1.5, v2.get_y())
        self.assertAlmostEqual(30 + 1.5, v3.get_y())
        self.assertAlmostEqual(10 + 1.5, v4.get_y())
        self.assertAlmostEqual(1 + 1.5, v9.get_y())
        self.assertAlmostEqual(1 + 1.5, v10.get_y())

    def test_get_top_row(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, vis=False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v5 = Vertex(10, 40)
        v6 = Vertex(30, 40)
        a_neighbor = Cell(
            simulation, [v2, v3, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        v11 = Vertex(50, 10)
        v12 = Vertex(50, 30)
        m_neighbor = Cell(
            simulation, [v11, v12, v4, v3], self.init_vals, simulation.get_next_cell_id()
        )
        cell1.add_neighbor(a_neighbor)
        a_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(l_neighbor)
        l_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(b_neighbor)
        b_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(m_neighbor)
        m_neighbor.add_neighbor(cell1)
        simulation.setup()
        simulation.get_vertex_mover().add_cell_delta_val(a_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(b_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(m_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(l_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(cell1, 1.5)
        self.assertEqual([a_neighbor], simulation.get_vertex_mover().get_top_row())

    def test_update(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, vis=False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v5 = Vertex(10, 40)
        v6 = Vertex(30, 40)
        a_neighbor = Cell(
            simulation, [v2, v3, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        v11 = Vertex(50, 10)
        v12 = Vertex(50, 30)
        m_neighbor = Cell(
            simulation, [v11, v12, v4, v3], self.init_vals, simulation.get_next_cell_id()
        )
        cell1.add_neighbor(a_neighbor)
        a_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(l_neighbor)
        l_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(b_neighbor)
        b_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(m_neighbor)
        m_neighbor.add_neighbor(cell1)
        simulation.setup()
        simulation.get_vertex_mover().add_cell_delta_val(a_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(b_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(m_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(l_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(cell1, 1.5)
        self.assertEqual([a_neighbor], simulation.get_vertex_mover().get_top_row())

    def test_sort_top_row(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        v11 = Vertex(50, 10)
        v12 = Vertex(50, 30)
        m_neighbor = Cell(
            simulation, [v11, v12, v4, v3], self.init_vals, simulation.get_next_cell_id()
        )
        cell1.add_neighbor(l_neighbor)
        l_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(b_neighbor)
        b_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(m_neighbor)
        m_neighbor.add_neighbor(cell1)
        simulation.setup()
        simulation.get_vertex_mover().add_cell_delta_val(b_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(m_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(l_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(cell1, 1.5)
        self.assertEqual(
            [l_neighbor, cell1, m_neighbor],
            simulation.get_vertex_mover().sort_top_row([cell1, m_neighbor, l_neighbor]),
        )

    def test_update_onecol(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v5 = Vertex(10, 40)
        v6 = Vertex(30, 40)
        a_neighbor = Cell(
            simulation, [v2, v3, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(b_neighbor)
        a_neighbor.add_neighbor(cell1)
        b_neighbor.add_neighbor(cell1)
        simulation.get_cell_list().append(cell1)
        simulation.get_cell_list().append(a_neighbor)
        simulation.get_cell_list().append(b_neighbor)
        simulation.get_vertex_mover().add_cell_delta_val(a_neighbor, 1.5)
        simulation.get_vertex_mover().update()
        self.assertAlmostEqual(10 + 1.5, v1.get_y())
        self.assertAlmostEqual(30 + 1.5, v2.get_y())
        self.assertAlmostEqual(30 + 1.5, v3.get_y())
        self.assertAlmostEqual(10 + 1.5, v4.get_y())
        self.assertAlmostEqual(1 + 1.5, v9.get_y())
        self.assertAlmostEqual(1 + 1.5, v10.get_y())

    def test_update_threecol(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, vis=False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )
        v11 = Vertex(50, 10)
        v12 = Vertex(50, 30)
        m_neighbor = Cell(
            simulation, [v11, v12, v4, v3], self.init_vals, simulation.get_next_cell_id()
        )
        v13 = Vertex(50, 1)
        mb_neighbor = Cell(
            simulation, [v4, v11, v10, v13], self.init_vals, simulation.get_next_cell_id()
        )
        v14 = Vertex(1, 1)
        lb_neighbor = Cell(
            simulation, [v14, v7, v1, v9], self.init_vals, simulation.get_next_cell_id()
        )
        simulation.setup()

        cell1.add_neighbor(l_neighbor)
        l_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(b_neighbor)
        b_neighbor.add_neighbor(cell1)
        cell1.add_neighbor(m_neighbor)
        m_neighbor.add_neighbor(cell1)
        l_neighbor.add_neighbor(lb_neighbor)
        lb_neighbor.add_neighbor(l_neighbor)
        m_neighbor.add_neighbor(mb_neighbor)
        mb_neighbor.add_neighbor(m_neighbor)

        simulation.get_vertex_mover().add_cell_delta_val(cell1, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(l_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(m_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(b_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(mb_neighbor, 1.5)
        simulation.get_vertex_mover().add_cell_delta_val(lb_neighbor, 1.5)

        simulation.get_vertex_mover().update()
        self.assertAlmostEqual(10 + 1.5, v7.get_y())
        self.assertAlmostEqual(10 + 1.5, v1.get_y())
        self.assertAlmostEqual(10 + 1.5, v4.get_y())
        self.assertAlmostEqual(10 + 1.5, v11.get_y())
        self.assertAlmostEqual(1 + 3, v14.get_y())
        self.assertAlmostEqual(1 + 3, v9.get_y())
        self.assertAlmostEqual(1 + 3, v10.get_y())
        self.assertAlmostEqual(1 + 3, v13.get_y())

    def test_check_if_divide(self):
        timestep = 1
        root_midpoint_x = 1000
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        simulation.setup()
        v2.set_y(50)
        v3.set_y(50)
        simulation.get_vertex_mover().check_if_divide([cell1])
        self.assertEqual([cell1], simulation.get_divider().get_cells_to_divide())
