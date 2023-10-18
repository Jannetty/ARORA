import unittest
from src.plantem.loc.quad_perimeter.quad_perimeter import (
    QuadPerimeter,
    get_apical,
    get_basal,
    get_left,
    get_right,
    get_len_perimeter_in_common,
)
from src.plantem.loc.vertex.vertex import Vertex


class TestQuadPerimeter(unittest.TestCase):
    def test_QuadPerimeter_get_apical(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        expected_apical = [v2, v3]
        found_apical = get_apical([v1, v2, v3, v4])
        self.assertCountEqual(expected_apical, found_apical)

    def test_QuadPerimeter_get_basal(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        expected_basal = [v1, v4]
        found_basal = get_basal([v1, v2, v3, v4])
        self.assertCountEqual(expected_basal, found_basal)

    def test_QuadPerimeter_get_left(self):
        v1 = Vertex(100, 100)
        v3 = Vertex(300, 300)
        expected_left = v1
        found_left = get_left([v1, v3])
        self.assertEqual(expected_left, found_left)

    def test_QuadPerimeter_get_right(self):
        v1 = Vertex(100, 100)
        v3 = Vertex(300, 300)
        expected_right = v3
        found_right = get_right([v1, v3])
        self.assertEqual(expected_right, found_right)

    def test_QuadPerimeter_assign_corners(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)

        this_qp = QuadPerimeter([v1, v2, v3, v4])

        self.assertEqual(v1, this_qp.get_bottom_left())
        self.assertEqual(v2, this_qp.get_top_left())
        self.assertEqual(v3, this_qp.get_top_right())
        self.assertEqual(v4, this_qp.get_bottom_right())

    def test_QuadPerimeter_get_corners_for_disp(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)

        this_qp = QuadPerimeter([v1, v2, v3, v4])

        corners_for_disp = [v4.get_xy(), v1.get_xy(), v2.get_xy(), v3.get_xy()]
        self.assertEqual(corners_for_disp, this_qp.get_corners_for_disp())

    def test_QuadPerimeter_calc_midpointx_get_midpointx(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        this_qp = QuadPerimeter([v1, v2, v3, v4])
        self.assertEqual(200, this_qp.get_midpointx())

    def test_QuadPerimeter_get_perimeter_len(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        this_qp = QuadPerimeter([v1, v2, v3, v4])
        self.assertEqual(800, this_qp.get_perimeter_len())

    def test_get_len_perimeter_in_common_right_neighbor(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp_1 = QuadPerimeter([v1, v2, v3, v4])
        v5 = Vertex(500, 100)
        v6 = Vertex(500, 300)
        qp_2 = QuadPerimeter([v3, v4, v5, v6])
        self.assertEqual(200, get_len_perimeter_in_common(qp_1, qp_2, "m"))
        self.assertEqual(200, get_len_perimeter_in_common(qp_1, qp_2, "l"))

    def test_get_len_perimeter_in_common_left_neighbor(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp_1 = QuadPerimeter([v1, v2, v3, v4])
        v5 = Vertex(0, 100)
        v6 = Vertex(0, 300)
        qp_2 = QuadPerimeter([v3, v4, v5, v6])
        self.assertEqual(200, get_len_perimeter_in_common(qp_1, qp_2, "m"))
        self.assertEqual(200, get_len_perimeter_in_common(qp_1, qp_2, "l"))

    def test_get_len_perimeter_in_common_top_neighbor(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp_1 = QuadPerimeter([v1, v2, v3, v4])
        v5 = Vertex(100, 500)
        v6 = Vertex(300, 500)
        qp_2 = QuadPerimeter([v3, v2, v5, v6])
        self.assertEqual(200, get_len_perimeter_in_common(qp_1, qp_2, "a"))
        self.assertEqual(200, get_len_perimeter_in_common(qp_1, qp_2, "b"))

    def test_get_len_perimeter_in_common_top_neighbor(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp_1 = QuadPerimeter([v1, v2, v3, v4])
        v5 = Vertex(100, 0)
        v6 = Vertex(300, 0)
        qp_2 = QuadPerimeter([v3, v2, v5, v6])
        self.assertEqual(200, get_len_perimeter_in_common(qp_1, qp_2, "a"))
        self.assertEqual(200, get_len_perimeter_in_common(qp_1, qp_2, "b"))

    def test_get_each_vertex(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp_1 = QuadPerimeter([v1, v2, v3, v4])
        self.assertEqual(v1, qp_1.get_bottom_left())
        self.assertEqual(v2, qp_1.get_top_left())
        self.assertEqual(v3, qp_1.get_top_right())
        self.assertEqual(v4, qp_1.get_bottom_right())

    def test_qp_set_corners(self):
        v01 = Vertex(1, 1)
        v02 = Vertex(1, 3)
        v03 = Vertex(3, 3)
        v04 = Vertex(3, 1)
        qp1 = QuadPerimeter([v01, v02, v03, v04])
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp1.set_corners([v1, v2, v3, v4])
        self.assertEqual(v1, qp1.get_bottom_left())
        self.assertEqual(v2, qp1.get_top_left())
        self.assertEqual(v3, qp1.get_top_right())
        self.assertEqual(v4, qp1.get_bottom_right())

    def test_determine_left_right(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp = QuadPerimeter([v1, v2, v3, v4])
        self.assertEqual(("lateral", "medial"), qp.determine_left_right(250))
        self.assertEqual(("lateral", "lateral"), qp.determine_left_right(200))
        self.assertEqual(("medial", "lateral"), qp.determine_left_right(120))

    def test_get_memfrac(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp = QuadPerimeter([v1, v2, v3, v4])
        self.assertEqual(0.25, qp.get_memfrac("a", "lateral"))

    def test_get_left(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp = QuadPerimeter([v1, v2, v3, v4])
        self.assertEqual("lateral", qp.get_left(250))
        self.assertEqual("lateral", qp.get_left(200))
        self.assertEqual("medial", qp.get_left(120))

    def test_get_right(self):
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        qp = QuadPerimeter([v1, v2, v3, v4])
        self.assertEqual("medial", qp.get_right(250))
        self.assertEqual("lateral", qp.get_right(200))
        self.assertEqual("lateral", qp.get_right(120))
