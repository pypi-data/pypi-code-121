import unittest
from ..consistency_analysis import UmFinder
from cobra.test import create_test_model


class TestUmFinder(unittest.TestCase):

    def __init__(self):
        self._model = create_test_model('iJO1366')

    def setUp(self):
        pass

    def test_model(self):
        self.assertTrue(len(self._model.reactions) == 2583)
        self.assertTrue(len(self._model.metabolites) == 1805)

    def test_umfinder(self):
        um_finder = UmFinder(self._model)
        self.assertTrue(len(um_finder.blocked_reactions) == 226)
        self.assertTrue(len(um_finder.gap_metabolites) == 203)
        self.assertTrue(len(um_finder.unconnected_modules) == 105)


if __name__ == '__main__':
    unittest.main()