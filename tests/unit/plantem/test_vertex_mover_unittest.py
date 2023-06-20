import unittest
from src.plantem.sim.mover.vertex_mover import VertexMover
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.agent.cell import GrowingCell

class TestVertexMover(unittest.TestCase):
    def test_VertexMover_add_delta_val(self):
        pass
        #v1 = Vertex(100, 100)
        #v2 = Vertex(100, 300)
        #v3 = Vertex(300, 300)
        #v4 = Vertex(300, 100)
        #qp_1 = QuadPerimeter([v1, v2, v3, v4])
        #v5 = Vertex(100, 0)
        #v6 = Vertex(300, 0)
        #qp_2 = QuadPerimeter([v3, v2, v5, v6])
        # cell1 = GrowingCell(qp_1, 0)
        # cell2 = GrowingCell(qp_2, 0)
        # cell1.add_neighbor(cell2)

