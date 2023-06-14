import unittest

from src.plantem.agent.circ_module import BaseCirculateModule
from src.plantem.agent.cell import GrowingCell


class BaseCirculateModuleTests(unittest.TestCase):
    def test_update(self):
        cell1 = GrowingCell(self, [[100.0,100.0], [100.0,300.0], [300.0,300.0], [300.0,100.0]], {})

        test_dict = {cell1: 1}

        for cell in test_dict:
            with self.subTest(cell=cell):
                circ_module = BaseCirculateModule(cell)
                found_delta = circ_module.update()[cell]
                expected_delta = test_dict[cell]

                self.assertEqual(found_delta, expected_delta)

    def test_calculate_auxin(self):
        timestep = 1
        area = 100
        


if __name__ == "__main__":
    unittest.main()