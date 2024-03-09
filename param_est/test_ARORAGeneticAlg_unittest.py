import os
import platform
if platform.system() == 'Linux':
    os.environ["ARCADE_HEADLESS"] = "True"
from param_est.ARORA_genetic_alg import ARORAGeneticAlg
import unittest

class TestARORAGeneticAlg(unittest.TestCase):

    def test_initialize(self):
        ga = ARORAGeneticAlg("filename.json")
        self.assertIsInstance(ga.ga_instance, type(None))

    # def test_run_ARORA(self):
    #     initial_parent_gen_file = "param_est/test_first_gen.csv"
    #     ga = ARORAGeneticAlg(initial_parent_gen_file)
    #     params = ga.parameters_df.iloc[0]
    #     cost = ga.run_ARORA(params)
    #     self.assertIsInstance(cost, float)
