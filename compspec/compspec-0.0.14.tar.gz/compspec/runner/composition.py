__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import compspec.solver
from compspec.solver import fn
from .base import CompositionBase, FactGenerator


class Composition(CompositionBase):
    """
    A composition is simply facts about one graph (object of interest).
    It uses a simple FactGenerator under the hood, and does not add any
    extra logic program (unless the user requests it).
    """

    def __init__(self, g, out=None, namespace=None, quiet=False):
        self.driver = compspec.solver.PyclingoDriver(out=out)
        self.facts = SingleCorpusGenerator(g, namespace=namespace)
        self.set_verbosity(out, quiet)


class SingleCorpusGenerator(FactGenerator):
    """
    The SingleCorpusGenerator generates facts for one graph.
    """

    def __init__(self, g, namespace=None):
        self.g = g
        self.ns = namespace or "A"

    def setup(self, driver):
        """
        Setup data for one library.
        This is called by the PyclingoDriver
        """
        self.gen = driver
        self.gen.h1(f"Composition Namespace {self.ns}")

        # Set the library namespace
        self.gen.fact(fn.namespace(self.ns))
        self.generate_facts(self.g, self.ns)
