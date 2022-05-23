__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from compspec.solver import fn
from compspec.logger import logger
from .base import CompositionBase, FactGenerator
import compspec.lp
import sys


class IterativeComposition(CompositionBase):
    """
    An iterative base base for an IterativeComposition or IterativeDiff.

    An iterative composition uses a FactIterativeGenerator, meaning
    the graph is expected to have a dictionary with named fact groups
    to solve one group at a time, giving the user the option to stop
    if needed.
    """

    def __init__(self, g, out=None, namespace=None, quiet=False):
        self.driver = compspec.solver.PyclingoDriver(out=out)
        self.set_verbosity(out, quiet)
        self.g = g

    def solve(self, logic_programs=None):
        """
        Run the solve, optionally with extra logic programs.

        This solve function is different from a traditional base because
        the facts are presented in groups, and results yielded so we can
        stop at any point.
        """
        for group, facts in self.g.iter_groups():

            # This setup takes the facts (nodes and relations) direcly from the graph
            setup = IterativeCorpusGenerator(group, facts, namespace=namespace)
            yield group, self.driver.solve(setup, logic_programs=logic_programs).answers


class IterativeDifference(CompositionBase):
    """
    An iterative diff base, meaning we compare entities in named groups.
    The named groups must match.
    """

    _logic_programs = ["is-compatible.lp"]

    def __init__(self, A, B, namespaceA=None, namespaceB=None, out=None, quiet=False):
        self.driver = compspec.solver.PyclingoDriver(out=out)
        self.set_verbosity(out, quiet)
        self.A = A
        self.B = B
        self.nsA = namespaceA
        self.nsB = namespaceB

    def solve(self, logic_programs=None):
        """
        Run the solve, optionally with extra logic programs.

        This solve function is different from a traditional base because
        the facts are presented in groups, and results yielded so we can
        stop at any point.
        """
        # We can only compare overlapping groups
        groups = set(self.A.groups.keys()).intersection(set(self.B.groups.keys()))
        if not groups:
            logger.exit("Libraries do not have overlapping groups for comparison.")

        for group in groups:
            logger.info("Running model for group %s" % group)
            factsA = self.A.groups[group]
            factsB = self.B.groups[group]

            # This setup takes the facts (nodes and relations) direcly from the graph
            setup = IterativeDiffGenerator(
                factsA, factsB, namespaceA=self.nsA, namespaceB=self.nsB
            )
            yield group, self.driver.solve(setup, logic_programs=logic_programs).answers


class IterativeDiffGenerator(FactGenerator):
    """
    The IterativeDiffGenerator expects two groups of facts for a named group
    that is shared between two entities.
    """

    def __init__(self, factsA, factsB, namespaceA=None, namespaceB=None):
        self.factsA = factsA
        self.factsB = factsB
        self.nsA = namespaceA or "A"
        self.nsB = namespaceB or "B"

    def setup(self, driver):
        """
        Setup data for one library.
        This is called by the PyclingoDriver
        """
        self.gen = driver
        self.gen.h1(f"Iterative Corpus Namespace {self.nsA} vs {self.nsB}")
        self.gen.fact(fn.is_a(self.nsA))
        self.gen.fact(fn.is_b(self.nsB))
        for facts, ns in [[self.factsA, self.nsA], [self.factsB, self.nsB]]:
            for nid, node in facts.get("nodes", {}).items():
                self.gen.fact(fn.node(ns, *node))
            for relation in facts.get("relations", []):
                self.gen.fact(fn.relation(ns, *relation))


class IterativeCorpusGenerator(FactGenerator):
    """
    The FactIterativeGenerator generates facts for one graph, but in iterations.
    The expected use case is to be run on an entity that has a huge number of
    checks to do, and we group the checks together in chunks so we can cut
    out early upon the first failure.
    """

    def __init__(self, group, facts, namespace=None):
        self.group = group
        self.facts = facts
        self.ns = namespace or "A"

    def setup(self, driver):
        """
        Setup data for one library.
        This is called by the PyclingoDriver
        """
        self.gen = driver
        self.gen.h1(f"Iterative Corpus Namespace {self.ns}")

        # Set the library namespace
        self.gen.fact(fn.namespace(self.ns))
        for nid, node in self.facts.get("nodes", {}).items():
            self.gen.fact(fn.node(ns, *node))
        for relation in self.facts.get("relations", []):
            self.gen.fact(fn.relation(ns, *relation))
