__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from compspec.solver import fn
import compspec.lp
import sys


class CompositionBase:
    """
    A composition base is the base for a Composition or Diff.
    """

    def set_verbosity(self, out, quiet=False):
        """
        Set the verbosity
        """
        out = out if out else sys.stdout
        if quiet:
            out = None
        self.out = out
        self.driver.set_verbosity(out)

    def solve(self, logic_programs=None):
        """
        Run the solve, optionally with extra logic programs.
        """
        result = self.driver.solve(self.facts, logic_programs=logic_programs)
        if result.answers and hasattr(self, "prepare_result"):
            result.answers = self.prepare_result(result.answers)
        return result.answers

    def _load_logic_programs(self, logic_programs=None):
        """
        Load user- and class- provided logic programs.
        """
        # This will ensure any provided logic programs also exist
        logic_programs = logic_programs or []
        if isinstance(logic_programs, str):
            logic_programs = [logic_programs]
        logic_programs += getattr(self, "_logic_programs", [])
        if logic_programs:
            logic_programs = compspec.lp.get_facts(logic_programs)
        return logic_programs

    def run(self, logic_programs=None, quiet=False):
        """
        Run of a composition will output ASP facts, unless a logic program
        is provided then we do this full solve.
        """
        logic_programs = self._load_logic_programs(logic_programs)
        return self.solve(logic_programs=logic_programs)


class FactGenerator:
    """
    The FactGenerator generates facts for one graph.
    """

    def generate_facts(self, g, ns):
        """
        Generate facts for a namespaced graph
        """
        for relation in g.iter_relations():
            self.gen.fact(fn.relation(ns, *relation))
        for node in g.iter_connectors():
            self.gen.fact(fn.is_connector(ns, node))
        for node in g.iter_nodes():
            self.gen.fact(fn.node(ns, *node))
