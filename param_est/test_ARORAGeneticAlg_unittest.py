import os
os.environ["ARCADE_HEADLESS"] = "True"
from param_est.run_ga import ARORAGeneticAlg
import unittest

class TestARORAGeneticAlg(unittest.TestCase):

    def test_initialize(self):
        initial_parent_gen_file = "param_est/test_first_gen.csv"
        ga = ARORAGeneticAlg(initial_parent_gen_file)
        self.assertEqual(ga.parameters_df.shape, (18, 9))

    def test_run_ARORA(self):
        initial_parent_gen_file = "param_est/test_first_gen.csv"
        ga = ARORAGeneticAlg(initial_parent_gen_file)
        params = ga.parameters_df.iloc[0]
        cost = ga.run_ARORA(params)
        self.assertIsInstance(cost, float)
