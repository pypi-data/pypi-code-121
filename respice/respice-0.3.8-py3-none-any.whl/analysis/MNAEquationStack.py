from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import List, Tuple, Hashable, Union, Iterable, Set, Dict

import numpy as np
from ordered_set import OrderedSet

from respice.analysis import UniqueEdgeMultiDiGraph
from respice.collections import OneToManyInvertibleMapping
from respice.components import Branch
from respice.components.Branch import VoltageBranch, CurrentBranch

from networkx.algorithms.components import weakly_connected_components


@dataclass
class KirchhoffEquationTerm:
    negative: bool
    branch: CurrentBranch
    coupled_branches: List[Union[VoltageBranch, CurrentBranch]]


@dataclass
class KirchhoffEquationBranchConsecutiveTerm:
    negative: bool
    branch: VoltageBranch


@dataclass
class KirchhoffEquation:
    terms: List[Union[KirchhoffEquationTerm, KirchhoffEquationBranchConsecutiveTerm]] = field(default_factory=list)


@dataclass
class BranchConsecutiveEquation:
    branch: VoltageBranch
    potentials: Tuple[Hashable, Hashable]
    coupled_branches: List[Union[VoltageBranch, CurrentBranch]]


class MNAEquationStack:
    """
    Manages the master equation that comprises an electrical circuit system using the so called MNA - Modified Nodal
    Analysis. Used inside the simulation algorithm to find the final solution.

    The MNA equation stack automatically generates an inner representation of all mathematical terms and equations
    necessary to describe the problem. The problem is a multivariate non-linear root-finding problem.

    This class is majorly to be used via solvers like scipy's fsolve function, where you feed in evaluate() or
    the optimized expression returned by lambdify().

    For more information about the MNA itself, see https://en.wikipedia.org/wiki/Modified_nodal_analysis
    """

    def __init__(self, graph: UniqueEdgeMultiDiGraph, couplings: Iterable[List[Branch]], references: Set[Hashable] = frozenset()):
        """
        Create a new equation system for a circuit.

        :param graph:
            The circuit graph that stores the connectivity between branches.
        :param couplings:
            The coupled branches. Coupled branches will receive the same voltage-current-vector ("coupling-vector") so
            they can describe mutual dynamics between themselves (e.g. for coupled inductors).
        :param references:
            Ground nodes to prefer.
            Invalid or conflicting ground nodes are ignored or resolved automatically by picking the first eligible
            node. If no ground nodes are specified or if ground nodes are missing for a connected subgraph where another
            ground node is required, it is automatically selected.
        """
        self._cache = SimpleNamespace()
        self._cache.equation_lambdified = None
        self._cache.jacobian_lambdified = None

        self._graph: UniqueEdgeMultiDiGraph = graph
        self._reference_nodes = OneToManyInvertibleMapping()

        # Stores the vector-index relations to potential nodes.
        self._nodes: OrderedSet[Hashable] = OrderedSet()
        # Stores the vector-index relations to branch currents when voltage-branches are used. The branch consecutive
        # currents are stored after the nodes in the input vector for evaluate().
        self._currents: OrderedSet[VoltageBranch] = OrderedSet()

        self._kirchhoff_equations: List[KirchhoffEquation] = []
        self._branch_consecutive_equations: List[BranchConsecutiveEquation] = []

        self._coupling_dictionary = {branch: coupled_branches
                                     for coupled_branches in couplings
                                     for branch in coupled_branches}

        for subset in weakly_connected_components(graph):
            # A bug in NetworkX prohibits editing the yielded sets directly, so we need to make a copy.
            # See https://github.com/networkx/networkx/issues/4331.
            subset = set(subset)

            # Pin down ground node. Depending on the given preferred reference nodes, either the immediate next node is
            # picked or one of the references specified. If more than one preferred ground node is specified that belong
            # to the same subset, the first available one is picked.
            preferred_ref_nodes = subset & references
            if preferred_ref_nodes:
                ref_node = preferred_ref_nodes.pop()
                subset.remove(ref_node)
            else:
                ref_node = subset.pop()

            for node in subset:
                self._reference_nodes[ref_node] = node

            subset_iter = iter(subset)

            for potential in subset_iter:
                self._nodes.add(potential)

                kirchhoff_equation = KirchhoffEquation()

                for negative, branches in [(False, graph.in_edges(potential, keys=True)),
                                           (True, graph.out_edges(potential, keys=True))]:
                    for source, target, branch in branches:
                        # Add equations according to MNA (Modified Nodal Analysis) technique.
                        if isinstance(branch, CurrentBranch):
                            term = KirchhoffEquationTerm(
                                negative=negative,
                                branch=branch,
                                coupled_branches=self._coupling_dictionary[branch],
                            )
                        elif isinstance(branch, VoltageBranch):
                            term = KirchhoffEquationBranchConsecutiveTerm(
                                negative=negative,
                                branch=branch,
                            )

                            # Branch consecutive equations are processed in a later step for more efficient iteration
                            # over nodes. Since branches are always connected between two nodes, but we can just have
                            # one branch consecutive equation per branch, we would need to track that information if we
                            # do it here.

                        else:
                            raise ValueError(f'Unknown branch type encountered: {type(branch)}')

                        kirchhoff_equation.terms.append(term)

                self._kirchhoff_equations.append(kirchhoff_equation)

        # Now processing branch consecutive equations.
        for source, target, branch in graph.edges(keys=True):
            if isinstance(branch, VoltageBranch):
                self._branch_consecutive_equations.append(BranchConsecutiveEquation(
                    branch=branch,
                    potentials=(source, target),
                    coupled_branches=self._coupling_dictionary[branch],
                ))

                self._currents.add(branch)

    def __len__(self):
        """
        :return:
            The number of equations inside the equation stack.
        """
        return len(self._nodes) + len(self._currents)

    def _expand_jacobi_vector(self, jacobi, coupled_branches: List[Union[VoltageBranch, CurrentBranch]]) -> np.ndarray:
        # Properly creates a Jacobian vector suiting the problem from a component-tailored Jacobian.
        # Effectively increases dimension and inserts zeroes accordingly so the Jacobian's from different branches can
        # be easily blended together.

        jacobi_vector = np.zeros(len(self))

        for i, branch in enumerate(coupled_branches):
            if isinstance(branch, VoltageBranch):
                jacobi_vector[self._currents.index(branch) + len(self._nodes)] += jacobi[i]
            elif isinstance(branch, CurrentBranch):
                source, target = self._graph.get_nodes(branch)

                # Although the Jacobian is calculated for the voltage difference over the branch, one can easily
                # prove that it can still be used to get the right Jacobian suited for the target problem. Assume
                # that the voltage over a branch v = b - a. b is the target voltage and a the source voltage. Our
                # problem is that we have df/dv at hand, but we need df/da and df/db instead.
                # Using substitution rule one can derive dv = db and dv = -da. Then we get
                # df/dv = df/db and -df/dv = df/da.
                if target in self._nodes:
                    jacobi_vector[self._nodes.index(target)] += jacobi[i]
                if source in self._nodes:
                    jacobi_vector[self._nodes.index(source)] += -jacobi[i]
            else:
                raise AssertionError(f'Unknown branch type encountered: {type(branch)}')

        return jacobi_vector

    def _create_coupled_v_i_vector(self,
                                   v_i: np.ndarray,
                                   coupled_branches: List[Union[VoltageBranch, CurrentBranch]]) -> np.ndarray:
        # Creates the voltage-current-vector ("coupling-vector") for a set of coupled branches from a solution.

        vec = []

        for branch in coupled_branches:
            if isinstance(branch, VoltageBranch):
                val = v_i[self._currents.index(branch) + len(self._nodes)]
            elif isinstance(branch, CurrentBranch):
                source, target = self._graph.get_nodes(branch)
                val = (
                    # If the nodes are not there, they were classified as reference nodes and would have a value of
                    # zero.
                    (v_i[self._nodes.index(target)] if target in self._nodes else 0) -
                    (v_i[self._nodes.index(source)] if source in self._nodes else 0)
                )
            else:
                raise AssertionError(f'Unknown branch type encountered: {type(branch)}')

            vec.append(val)

        return np.array(vec)

    def evaluate(self, v_i: np.ndarray, t1: float, t2: float) -> np.ndarray:
        """
        Evaluates the equation stack.

        :param v_i:
            The voltages (measured in Volts) and branch consecutive currents (measured in Ampere) as input.
        :param t1:
            Previous point in time (measured in seconds).
        :param t2:
            Present point in time (measured in seconds).
        :return:
            The result.
        """
        out_vector = []

        for kirchhoff_equation in self._kirchhoff_equations:
            summation = 0.0

            for term in kirchhoff_equation.terms:
                if isinstance(term, KirchhoffEquationTerm):
                    summation += (-1 if term.negative else 1) * term.branch.get_current(
                        self._create_coupled_v_i_vector(v_i, term.coupled_branches),
                        t1,
                        t2,
                    )
                elif isinstance(term, KirchhoffEquationBranchConsecutiveTerm):
                    summation += (
                        (-1 if term.negative else 1) *
                        v_i[self._currents.index(term.branch) + len(self._nodes)]
                    )
                else:
                    raise AssertionError(f'Invalid term type encountered: {type(term)}')

            out_vector.append(summation)

        for branch_consecutive_equation in self._branch_consecutive_equations:
            source, target = branch_consecutive_equation.potentials

            out_vector.append(
                branch_consecutive_equation.branch.get_voltage(
                    self._create_coupled_v_i_vector(v_i, branch_consecutive_equation.coupled_branches),
                    t1,
                    t2,
                )
                + (v_i[self._nodes.index(source)] if source in self._nodes else 0)
                - (v_i[self._nodes.index(target)] if target in self._nodes else 0)
            )

        return np.array(out_vector)

    def get_voltage_between_nodes(self, solution: np.ndarray, source, target) -> float:
        """
        Returns the voltage between two nodes from a calculated solution.

        :param solution:
            The solution vector.
        :param source:
            The source node.
        :param target:
            The target node.
        :return:
            The voltage between `source` and `target` nodes.
        """
        return (
            (solution[self._nodes.index(target)] if target in self._nodes else 0) -
            (solution[self._nodes.index(source)] if source in self._nodes else 0)
        )

    def get_reference_nodes(self):
        """
        Return all ground nodes (a.k.a. GND or reference nodes).
        """
        return self._reference_nodes.keys()

    def get_node_voltage(self, solution: np.ndarray, node: Hashable) -> float:
        """
        Returns the voltage (or potential) of a node from a given solution.

        :param solution:
            The solution to get the voltage from.
        :param node:
            The node.
        :return:
            The voltage/potential measured in Volts.
        """
        return solution[self._nodes.index(node)]

    def get_node_voltages(self, solution: np.ndarray) -> Dict[Hashable, float]:
        """
        Returns the voltages (or potentials) from all nodes.

        :param solution:
            The solution to get the voltages from.
        :return:
            A dictionary mapping nodes to their respective voltage/potential.
        """
        vs = {node: self.get_node_voltage(solution, node) for node in self._nodes}
        vs.update({gnd_node: 0 for gnd_node in self._reference_nodes})
        return vs

    def get_voltage(self, solution: np.ndarray, branch: CurrentBranch) -> float:
        """
        Returns the voltage for a given current-branch from a calculated solution.

        Since only this stack knows how branches and their voltages and currents are tracked in the solution vector,
        use this function afterwards to reassign those values back to the actual branches.

        :param solution:
            The solution vector.
        :param branch:
            The current-branch to get the voltage for.
        :return:
            The voltage for `branch`.
        """
        source, target = self._graph.get_nodes(branch)
        return self.get_voltage_between_nodes(solution, source, target)

    def get_current(self, solution: np.ndarray, branch: VoltageBranch) -> float:
        """
        Returns the current for a given voltage-branch from a calculated solution.

        Since only this stack knows how branches and their voltages and currents are tracked in the solution vector,
        use this function afterwards to reassign those values back to the actual branches.

        :param solution:
            The solution vector.
        :param branch:
            The voltage-branch to get the current for.
        :return:
            The current for `branch`.
        """
        return solution[self._currents.index(branch) + len(self._nodes)]

    def assemble_vector(self, v: Dict[Hashable, float], i: Dict[VoltageBranch, float], fill: float = 0.0):
        """
        Assembles a proper vector from voltages and currents that can be used to evaluate this equation stack.

        :param v:
            Mapping of nodes to voltages.
        :param i:
            Mapping of voltage branches to their respective currents (other branch types are insignificant).
        :param fill:
            Fill value to use if a needed node or branch is missing.
        :return:
            A vector that can be used for `evaluate` and `jacobian` for equation evaluation.
        """
        vec = np.full(len(self), fill, dtype=float)
        for node in v:
            if node in self._nodes:
                # Subtract also the reference potential if one was given explicitly to properly offset all voltages
                # within a joint group of nodes.
                vec[self._nodes.index(node)] = v[node] - v.get(self._reference_nodes.reverse[node], 0)

        for branch in i:
            if branch in self._currents:
                vec[self._currents.index(branch) + len(self._nodes)] = i[branch]

        return vec

    def disassemble_vector(self, solution: np.ndarray):
        """
        Reverse operation of `assemble_vector`, creates `node -> potential` and `branch -> current` dictionaries
        from a solution.

        :param solution:
            The solution to create the dictionaries from.
        :return:
            `node -> potential` and `branch -> current` dicts as a 2-tuple.
        """
        v = {}
        i = {}

        for branch in self._currents:
            i[branch] = self.get_current(solution, branch)

        for node in self._nodes:
            v[node] = self.get_node_voltage(solution, node)

        for gnd_node in self._reference_nodes:
            v[gnd_node] = 0

        return v, i

    def _create_lambdified_coupled_v_i_vector(self, coupled_branches: List[Union[VoltageBranch, CurrentBranch]]) -> List[str]:
        coupled_entries = []

        for branch in coupled_branches:
            if isinstance(branch, VoltageBranch):
                coupled_val = f'v_i[{self._currents.index(branch) + len(self._nodes)}]'
            elif isinstance(branch, CurrentBranch):
                source, target = self._graph.get_nodes(branch)

                coupled_val = ''
                if source is target:
                    # Coupling that self-closes on a ground node might end up here.
                    coupled_val = '0'
                else:
                    if target in self._nodes:
                        coupled_val += f'v_i[{self._nodes.index(target)}]'
                    if source in self._nodes:
                        coupled_val += f'-v_i[{self._nodes.index(source)}]'
            else:
                raise AssertionError(f'Unknown branch type encountered: {type(branch)}')

            coupled_entries.append(coupled_val)

        return coupled_entries

    def lambdify(self):
        """
        Optimizes the MNA equation stack by returning a lambdified expression.

        This function compiles a Python function that immediately computes `evaluate()`.

        Note that the returned object is immediately callable and does not have an `evaluate()` member function.
        Also later updates on the instance of the MNA equation stack will not reflect into already lambdified
        expressions. In this case it has to be recompiled.

        :return:
            A function that is callable like `evaluate()` and behaves exactly like it.
        """
        if self._cache.equation_lambdified is not None:
            return self._cache.equation_lambdified

        mapped_branches = OrderedSet()
        code_globals = {'branches': mapped_branches}

        vector_entries = []

        for equation in self._kirchhoff_equations:
            terms = []

            for term in equation.terms:
                if isinstance(term, KirchhoffEquationTerm):
                    val = (f'branches[{mapped_branches.add(term.branch)}]'
                           f'.get_current(np.array(['
                           f'{",".join(self._create_lambdified_coupled_v_i_vector(term.coupled_branches))}'
                           f']),t1,t2)')

                elif isinstance(term, KirchhoffEquationBranchConsecutiveTerm):
                    val = f'v_i[{self._currents.index(term.branch) + len(self._nodes)}]'
                else:
                    raise AssertionError(f'Unexpected equation term type: {type(term)}')

                if term.negative:
                    val = '-' + val

                terms.append(val)

            vector_entries.append('+'.join(terms))

        for equation in self._branch_consecutive_equations:
            source, target = equation.potentials
            vector_entries.append(
                f'branches[{mapped_branches.add(equation.branch)}]'
                f'.get_voltage(np.array(['
                f'{",".join(self._create_lambdified_coupled_v_i_vector(equation.coupled_branches))}'
                f']),t1,t2)'
                f'{f"+v_i[{self._nodes.index(source)}]" if source in self._nodes else ""}'
                f'{f"-v_i[{self._nodes.index(target)}]" if target in self._nodes else ""}'
            )

        code = [
            'import numpy as np',
            'def eq(v_i: np.ndarray, t1: float, t2: float) -> np.ndarray:',
            ' return np.array([',
        ] + [entry + ',' for entry in vector_entries] + [
            ' ])',
        ]

        # Compile the expression and get back the set up eq() function.
        code_object = compile('\n'.join(code), '<lambdified-mna-equation-stack>', 'exec')
        exec(code_object, code_globals)
        fun = code_globals['eq']

        self._cache.equation_lambdified = fun

        return fun

    def jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> np.ndarray:
        """
        Evaluates the Jacobian of the equation stack.

        :param v_i:
            The voltages (measured in Volts) and branch consecutive currents (measured in Ampere) as input.
        :param t1:
            Previous point in time (measured in seconds).
        :param t2:
            Present point in time (measured in seconds).
        :return:
            The result.
        """
        jacobi_matrix = []

        for kirchhoff_equation in self._kirchhoff_equations:
            jacobi_vector = np.zeros(len(self))

            for term in kirchhoff_equation.terms:
                if isinstance(term, KirchhoffEquationTerm):
                    jacobi_vector += (-1 if term.negative else 1) * self._expand_jacobi_vector(
                        term.branch.get_jacobian(
                            self._create_coupled_v_i_vector(v_i, term.coupled_branches),
                            t1,
                            t2,
                        ),
                        term.coupled_branches,  # TODO Maybe I should move all this into a function, since I reuse coupled_branches twice.
                    )
                elif isinstance(term, KirchhoffEquationBranchConsecutiveTerm):
                    jacobi_vector[self._currents.index(term.branch) + len(self._nodes)] += 1.0
                else:
                    raise AssertionError(f'Invalid term type encountered: {type(term)}')

            jacobi_matrix.append(jacobi_vector)

        for branch_consecutive_equation in self._branch_consecutive_equations:
            jacobi_vector = np.zeros(len(self))

            source, target = branch_consecutive_equation.potentials

            jacobi_vector += self._expand_jacobi_vector(
                branch_consecutive_equation.branch.get_jacobian(
                    self._create_coupled_v_i_vector(v_i, branch_consecutive_equation.coupled_branches),
                    t1,
                    t2,
                ),
                branch_consecutive_equation.coupled_branches,  # TODO Maybe I should move all this into a function, since I reuse coupled_branches twice.
            )

            # We have 2 additional entries for branch consecutive equations: 1 and -1
            # respectively for source and target voltage Jacobians.
            if source in self._nodes:
                jacobi_vector[self._nodes.index(source)] = 1.0
            if target in self._nodes:
                jacobi_vector[self._nodes.index(target)] = -1.0

            jacobi_matrix.append(jacobi_vector)

        return np.array(jacobi_matrix)

    def lambdify_jacobian(self):
        """
        Creates an optimized version of `jacobian` by compiling a more efficient Python expression.

        :return:
            A callable object that behaves like `jacobian` but faster.
        """
        if self._cache.jacobian_lambdified is not None:
            return self._cache.jacobian_lambdified

        mapped_branches = OrderedSet()
        code_globals = {'branches': mapped_branches}

        jacobi_matrix = []

        for kirchhoff_equation in self._kirchhoff_equations:
            jacobi_vector = [[] for _ in range(len(self))]

            for term in kirchhoff_equation.terms:
                if isinstance(term, KirchhoffEquationTerm):
                    jacobi = f'{"-" if term.negative else ""}jacobians[{mapped_branches.add(term.branch)}]'

                    for i, branch in enumerate(term.coupled_branches):
                        jacobi_value = f'{jacobi}[{i}]'
                        if isinstance(branch, VoltageBranch):
                            jacobi_vector[self._currents.index(branch) + len(self._nodes)].append(jacobi_value)
                        elif isinstance(branch, CurrentBranch):
                            source, target = self._graph.get_nodes(branch)
                            if target in self._nodes:
                                jacobi_vector[self._nodes.index(target)].append(jacobi_value)
                            if source in self._nodes:
                                jacobi_vector[self._nodes.index(source)].append('-' + jacobi_value)
                        else:
                            raise AssertionError(f'Unknown branch type encountered: {type(branch)}')
                elif isinstance(term, KirchhoffEquationBranchConsecutiveTerm):
                    jacobi_vector[self._currents.index(term.branch) + len(self._nodes)].append('-1' if term.negative else '1')
                else:
                    raise AssertionError(f'Invalid term type encountered: {type(term)}')

            jacobi_matrix.append(jacobi_vector)

        for branch_consecutive_equation in self._branch_consecutive_equations:
            jacobi_vector = [[] for _ in range(len(self))]

            source, target = branch_consecutive_equation.potentials

            jacobi = f'jacobians[{mapped_branches.add(branch_consecutive_equation.branch)}]'

            for i, branch in enumerate(branch_consecutive_equation.coupled_branches):
                jacobi_value = f'{jacobi}[{i}]'
                if isinstance(branch, VoltageBranch):
                    jacobi_vector[self._currents.index(branch) + len(self._nodes)].append(jacobi_value)
                elif isinstance(branch, CurrentBranch):
                    source, target = self._graph.get_nodes(branch)
                    if target in self._nodes:
                        jacobi_vector[self._nodes.index(target)].append(jacobi_value)
                    if source in self._nodes:
                        jacobi_vector[self._nodes.index(source)].append('-' + jacobi_value)
                else:
                    raise AssertionError(f'Unknown branch type encountered: {type(branch)}')

            if source in self._nodes:
                jacobi_vector[self._nodes.index(source)].append('1')
            if target in self._nodes:
                jacobi_vector[self._nodes.index(target)].append('-1')

            jacobi_matrix.append(jacobi_vector)

        precalculated_jacobians = [
            (f'branches[{i}].get_jacobian(np.array(['
             f'{",".join(self._create_lambdified_coupled_v_i_vector(self._coupling_dictionary[branch]))}'
             f']),t1,t2)')
            for i, branch in enumerate(mapped_branches)
        ]

        jacobi_matrix_rows = [
            f'[{",".join("+".join(column if column else ["0"]) for column in row)}]'
            for row in jacobi_matrix
        ]

        code = [
            f'import numpy as np',
            f'def jac(v_i: np.ndarray, t1: float, t2: float) -> np.ndarray:',
            f' jacobians = [{",".join(precalculated_jacobians)}]',
            f' return np.array([{",".join(jacobi_matrix_rows)}])',
        ]

        # Compile the expression and get back the set up eq() function.
        code_object = compile('\n'.join(code), '<lambdified-mna-equation-stack-jacobian>', 'exec')
        exec(code_object, code_globals)
        fun = code_globals['jac']

        self._cache.jacobian_lambdified = fun

        return fun
