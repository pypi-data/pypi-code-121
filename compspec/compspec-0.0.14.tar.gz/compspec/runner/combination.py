__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import compspec.solver
from compspec.solver import fn
from .base import CompositionBase, FactGenerator


class Combination(CompositionBase):
    """
    A combination combines one or more graphs.
    """

    def __init__(self, out=None, quiet=False):
        self.driver = compspec.solver.PyclingoDriver(out=out)
        self.facts = CombinedFactsGenerator()
        self.set_verbosity(out, quiet)

    def add_graph(self, g, ns):
        """
        Add a graph to the namespace.
        """
        self.facts.add_graph(g, ns)


class CombinedFactsGenerator(FactGenerator):
    """
    The SingleCorpusGenerator generates facts for one graph.
    """

    def __init__(self):

        # Lookup of graphs by namespace
        self.graphs = {}

    def add_graph(self, g, ns):
        """
        Add a graph to the namespace
        """
        self.graphs[ns] = g

    def setup(self, driver):
        self.gen = driver
        for ns, g in self.graphs.items():
            self.gen.h1(f"Composition Namespace {ns}")
            self.gen.fact(fn.namespace(ns))
            self.generate_facts(g, ns)
