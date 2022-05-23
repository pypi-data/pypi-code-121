__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import compspec.solver
from compspec.solver import fn
import compspec.utils as utils
from .base import CompositionBase, FactGenerator


class Difference(CompositionBase):
    """
    A composition is simply facts about one graph (object of interest).
    It uses a simple FactGenerator under the hood, and does not add any
    extra logic program (unless the user requests it).
    """

    _logic_programs = ["is-compatible.lp"]

    def __init__(self, A, B, namespaceA=None, namespaceB=None, out=None, quiet=False):
        self.driver = compspec.solver.PyclingoDriver(out=out)
        self.facts = DiffFactsGenerator(
            A, B, namespaceA=namespaceA, namespaceB=namespaceB
        )
        self.set_verbosity(out, quiet)

    @classmethod
    def table(cls, result):
        """
        Generate a table from results
        """
        out = "| Name | Value | Change Type | A | B | Description |\n"
        out += "|------|-------|-------------|---|---|-------------|\n"

        if "changed_node_value" in result:
            for entry in result["changed_node_value"]:
                out += utils.row(
                    [
                        entry[4],
                        entry[5] + " -> " + entry[6],
                        "change",
                        entry[0],
                        entry[1],
                        entry[-2] + " -> " + entry[-1],
                    ]
                )

        if "added_node" in result:
            for entry in result["added_node"]:
                out += utils.row(
                    [entry[3], entry[4], "add", entry[0], entry[1], entry[-1]]
                )

        if "removed_node" in result:
            for entry in result["removed_node"]:
                out += utils.row(
                    [entry[3], "", "remove", entry[0], entry[1], entry[-1]]
                )

        return out

    def prepare_result(self, result):
        """
        If defined, we further process the result json before returning.

        This preparation is based on the default compsec diff is-compatible facts:

        """
        # An added node is in B but not A
        if "added_node" in result:
            added_nodes = []
            for entry in result["added_node"]:
                entry.append(self.facts.B.lookup[entry[2]])
                added_nodes.append(entry)
            result["added_node"] = added_nodes

        # An removed node is in A but not B
        if "removed_node" in result:
            removed_nodes = []
            for entry in result["removed_node"]:
                entry.append(self.facts.A.lookup[entry[2]])
                removed_nodes.append(entry)
            result["removed_node"] = removed_nodes

        if "changed_node_value" in result:
            changed_node_values = []
            for entry in result["changed_node_value"]:

                # Add what was changed for a human to read
                # ['A', 'B', 'IDA', "IDB"...]
                entry.append(self.facts.A.lookup[entry[2]])
                entry.append(self.facts.B.lookup[entry[3]])
                changed_node_values.append(entry)
            result["changed_node_value"] = changed_node_values
        return result


class DiffFactsGenerator(FactGenerator):
    """
    The DiffFactsGenerator generates facts for two graphs to compare.
    """

    def __init__(self, A, B, namespaceA=None, namespaceB=None):
        self.A = A
        self.B = B
        self.nsA = namespaceA or "A"
        self.nsB = namespaceB or "B"

    def setup(self, driver):
        """
        Setup data for one library.
        This is called by the PyclingoDriver
        """
        self.gen = driver
        self.gen.h1(f"Difference Betweeen {self.nsA} and {self.nsB}")

        # Set the library namespace
        self.gen.fact(fn.is_a(self.nsA))
        self.gen.fact(fn.is_b(self.nsB))
        self.gen.h2(f"Namespace {self.nsA}")
        self.generate_facts(self.A, self.nsA)
        self.generate_facts(self.B, self.nsB)
