import os
import platform
if platform.system() == 'Linux':
    os.environ["ARCADE_HEADLESS"] = "True"
from param_est.ARORA_genetic_alg import ARORAGeneticAlg
import unittest

class TestARORAGeneticAlg(unittest.TestCase):

    SYNDEG_ONLY = "auxsyndeg_only"
    INDEP_SYNDEG = "indep_syn_deg"

    def test_initialize(self):
        ga = ARORAGeneticAlg("filename.json", self.SYNDEG_ONLY)
        self.assertIsInstance(ga, ARORAGeneticAlg)
