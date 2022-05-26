import sys
from bisect import insort
from dataclasses import dataclass
from itertools import compress, chain
from threading import Thread
from types import SimpleNamespace
from typing import Hashable, List, Set, Collection, Union

import numpy as np
from networkx import Graph, connected_components, incidence_matrix
from scipy.sparse.linalg import spsolve

from respice.cachetools import LRUCache
from respice.collections import OneToManyInvertibleMapping
from respice.components import Component, CurrentBranch, VoltageBranch, SwitchBranch
from respice.itertools.custom import compact, uncompact
from respice.math import flcm
from respice.math.optimization.rootsolvers.mixed import solve
from respice.threading import prefer_thread_yield
from .MNAEquationStack import MNAEquationStack
from .TransientEFMSimulation import TransientEFMSimulation
from .TransientSimulation import TransientSimulation
from .TransientSteadyStateEFMSimulation import TransientSteadyStateEFMSimulation
from .TransientSteadyStateSimulation import TransientSteadyStateSimulation
from .UniqueEdgeMultiDiGraph import UniqueEdgeMultiDiGraph


def linear_interpolation(x1, ys1, x2, ys2):
    if x2 - x1 == 0.0:
        return constant_interpolation(ys2)

    # Do not use numpy.polyfit to perform this task! It is about an order of magnitude slower.
    # It is actually tailored for least square fitting, so it prepares much more data under the hood which takes time.
    polys = [np.poly1d([(y2 - y1) / (x2 - x1), (y1 * x2 - x2 * x1) / (x2 - x1)])
             for y1, y2 in zip(ys1, ys2)]
    return lambda v: np.fromiter((poly(v) for poly in polys), dtype=float)


def constant_interpolation(y):
    return lambda v: y


@dataclass(eq=False)
class _MergedNode:
    nodes: Set[Hashable]


class ConvergenceError(Exception):
    pass


class Circuit:
    _EVENT_RESAMPLING_PRECISION = sys.float_info.epsilon * 2**20
    _CIRCUIT_SWITCH_CONFIGURATION_CACHE_SIZE = 2 ** 16

    def __init__(self):
        self._graph = UniqueEdgeMultiDiGraph()

        # Enforces uniqueness of elements across all graph edges (additionally, since uniqueness is effectively already
        # enforced by the special MultiDiGraph type used, because same branches of components can't be added twice as
        # well). Since adding the same component twice would cause the data in its branches to become mixed up, since
        # multiple results get appended to the same branch instance.
        self._component_branches = OneToManyInvertibleMapping()

        self._cache = SimpleNamespace()
        self._cache.circuit_switch_configurations = LRUCache(maxsize=self._CIRCUIT_SWITCH_CONFIGURATION_CACHE_SIZE)

    def add(self, component: Component, *terminals: Hashable):
        """
        Adds a new component to the circuit.

        :param component:
            The component to connect.
        :param terminals:
            The nodes/potentials to connect the component to. See each component's documentation about the order of
            each terminal to be specified.
        """
        if component in self._component_branches:
            raise KeyError(f'given component {repr(component)} already added to circuit.')

        component_branches = component.connect(*terminals)

        for source, target, branch in component_branches:
            self._component_branches[component] = branch
            self._graph.add_edge(source, target, branch)

        self._cache.circuit_switch_configurations.clear()

    def remove(self, component: Component):
        """
        Removes a component from the circuit.

        :param component:
            The component to remove from the circuit.
        """
        for branch in self._component_branches[component]:
            self._graph.remove_edge(branch)

        del self._component_branches[component]

        self._cache.circuit_switch_configurations.clear()

    @property
    def components(self):
        """
        :return:
            All components added to this circuit.
        """
        return self._component_branches.keys()

    def _get_coupled_vi_vector(self, component, result, eq):
        coupled_v_i = []
        for coupled_branch in self._component_branches[component]:
            if isinstance(coupled_branch, CurrentBranch):
                coupled_v_i.append(eq.get_voltage(result, coupled_branch))
            elif isinstance(coupled_branch, VoltageBranch):
                coupled_v_i.append(eq.get_current(result, coupled_branch))
            elif isinstance(coupled_branch, SwitchBranch):
                pass
            else:
                raise AssertionError(f'Unknown branch type encountered: f{type(coupled_branch)}')

        return np.array(coupled_v_i)

    def _get_switches(self):
        # Ensures the same order of switches between calls so switch configurations can be stored reliably.
        return [branch for branch in self._component_branches.reverse if isinstance(branch, SwitchBranch)]

    def simulate(self, ts1: float, ts2: float, steps: int, preferred_ground_nodes=frozenset()) -> TransientSimulation:
        """
        Perform a circuit simulation.

        The simulation is *asynchronous*! A future object is returned that allows you to access results and progress
        during simulation runtime. Note the following:

        * Accesses to single component or branch values (such as voltage, current, etc.) will immediately return the
          most recent simulation data. Between calls, the data may change. For safe access, although not really intended
          to be utilized by users, you can acquire the modification lock by:

          .. code-block:: python

              simulation = circuit.simulate(...)
              with simulation as sim:
                  # Acquired the simulation lock. The simulation will halt when attempting to write results.
                  # This means be sure to release it again if you don't want to interrupt the simulation too long.
                  pass

        * Accessing properties and fields of components or branches is safe, but writing is not and will consequently
          influence the simulation and causes undefined behavior.

        * Cancelling a simulation via `KeyboardInterrupt` alias `Ctrl + C` is not handled automatically. If you want to
          support aborting simulations, wrap the simulation code in a try-except and cancel it:

          .. code-block:: python

              simulation = circuit.simulate(...)
              try:
                  simulation.wait()
              except KeyboardInterrupt:
                  simulation.cancel()

        States after a simulation remain. This means you can chain simulations
        together altering parameters in between (for example turning off a voltage supply by removing
        it from the circuit or changing a resistance value).

        :param ts1:
            Initial point in time to start simulation from.
        :param ts2:
            Point in time to simulate up to.
        :param steps:
            The number of steps to simulate between `t1` and `t2` (`t1` and `t2` included).
        :param preferred_ground_nodes:
            Notes to prefer as ground (GND).
        :return:
            A `TransientSimulation` to access the result of the simulation from.
            Note that computation happens *asynchronously*!
        """
        if steps < 1:
            raise ValueError('at least 1 step required for simulation')

        simulation = TransientSimulation(ts1, ts2, self._component_branches, self._graph.nodes)

        def simulate_async(simulation, ts1, ts2, steps, preferred_ground_nodes):
            try:
                self._simulate(simulation, ts1, ts2, steps, preferred_ground_nodes)
            except Exception as ex:
                simulation.abort(ex)

        Thread(target=simulate_async,
               args=(simulation, ts1, ts2, steps, preferred_ground_nodes)).start()

        return simulation

    def _simulate(self,
                  simulation: TransientSimulation,
                  ts1: float,
                  ts2: float,
                  steps: int,
                  preferred_gnd_nodes=frozenset()):
        # A standard list is explicitly needed to allow modifications during iteration.
        ts = list(np.linspace(ts1, ts2, steps))

        # Closures for less code duplication.

        def create_switch_configured_graph(switch_config):
            # Generate a graph representation that can be fed into MNAEquationStack.
            # MNAEquationStack is not able to handle switches by itself, so graphs are "configured", which means that
            # off-switches are plainly removed from the graph and adjacent nodes of on-switches are merged together
            # effectively symbolizing a short-circuit between those nodes.
            switch_configured_graph: UniqueEdgeMultiDiGraph = self._graph.copy()
            merged_nodes = Graph()  # Use a graph to relate nodes for later merge.
            for switch, switch_on in zip(self._get_switches(), switch_config):
                if switch_on:
                    merged_nodes.add_edge(*self._graph.get_nodes(switch))

                switch_configured_graph.remove_edge(switch)

            for nodes in connected_components(merged_nodes):
                switch_configured_graph.merge_nodes(nodes, _MergedNode(nodes))

            return switch_configured_graph

        def solve_circuit(eq1, eq2, x0, t1, t2):
            if eq1 is not eq2:
                # Convert old result/guess to new guess.
                x0 = eq2.assemble_vector(*eq1.disassemble_vector(x0))

            # eq2 is the equation to be solved for current time t2.
            result = solve(eq2.lambdify(), x0, args=(t1, t2), jac=eq2.lambdify_jacobian())

            if result.success:
                return result.x
            else:
                raise ConvergenceError(result)

        def get_equation(t):
            # Get the correct circuit configuration and according equations at time t.

            switch_config = tuple(switch.switch_state(t) for switch in self._get_switches())

            if switch_config in self._cache.circuit_switch_configurations:
                switch_configured_graph, equation = self._cache.circuit_switch_configurations[switch_config]
            else:
                try:
                    # Prefer ground nodes from a previous simulation.
                    _, (_, eq) = self._cache.circuit_switch_configurations.last()
                    gnd_nodes = set(eq.get_reference_nodes())
                except KeyError:
                    gnd_nodes = set()

                gnd_nodes |= preferred_gnd_nodes
                switch_configured_graph = create_switch_configured_graph(switch_config)

                equation = MNAEquationStack(
                    switch_configured_graph,
                    ([branch
                      for branch in coupled_branches
                      if not isinstance(branch, SwitchBranch)]
                     for coupled_branches in self._component_branches.values()),
                    gnd_nodes)
                self._cache.circuit_switch_configurations[switch_config] = switch_configured_graph, equation

            return switch_config, switch_configured_graph, equation

        def store_result(t1, t2, eq, result, switch_config, switch_configured_graph):
            with simulation as sim:
                sim.ts.append(t2)

                # Store node->voltages map.
                for node, v in eq.get_node_voltages(result).items():
                    if isinstance(node, _MergedNode):
                        for merged_node in node.nodes:
                            sim.node_potentials[merged_node].append(v)
                    else:
                        sim.node_potentials[node].append(v)

                # Store switch states.
                for switch, switch_state in zip(self._get_switches(), switch_config):
                    sim.switch_states[switch].append(switch_state)

                # Map back calculated voltages and currents to actual elements.
                for component in self._component_branches:
                    coupled_v_i = self._get_coupled_vi_vector(component, result, eq)

                    for branch in self._component_branches[component]:
                        if isinstance(branch, CurrentBranch):
                            v = eq.get_voltage(result, branch)
                            i = branch.get_current(coupled_v_i, t1, t2)
                            sim.branch_voltages[branch].append(v)
                            sim.branch_currents[branch].append(i)
                        elif isinstance(branch, VoltageBranch):
                            i = eq.get_current(result, branch)
                            v = branch.get_voltage(coupled_v_i, t1, t2)
                            sim.branch_voltages[branch].append(v)
                            sim.branch_currents[branch].append(i)
                        elif isinstance(branch, SwitchBranch):
                            # If the switch is on, it produces a merged node. This scenario is handled below.
                            if not branch.switch_state(t2):
                                source, target = self._graph.get_nodes(branch)
                                sim.branch_voltages[branch].append(sim.node_potentials[target][-1] -
                                                                   sim.node_potentials[source][-1])
                                sim.branch_currents[branch].append(0.0)
                        else:
                            raise AssertionError(f'Unknown branch type encountered: f{type(branch)}')

                    component.update(coupled_v_i, t1, t2)

                    # Save state results now that components are updated.
                    sim.component_states[component].append(component.state)

                # Calculate switch branch currents.
                for node in switch_configured_graph.nodes:
                    if isinstance(node, _MergedNode):
                        # Use the incidence matrix to solve for any kind of switch layout.
                        # If especially switches are connected to other switches, with the help of the
                        # incidence matrix it is possible to solve for all currents through those switches.
                        merged_graph = self._graph.subgraph(node.nodes).copy()

                        # Sometimes other branches than switches can form self loops if they are connected between
                        # the switches of the same merged node. In this case we need to exclude those from the
                        # incidence matrix.
                        merged_graph.remove_edges_from({branch
                                                        for _, _, branch in merged_graph.edges
                                                        if not isinstance(branch, SwitchBranch)})

                        nodes = list(merged_graph.nodes)[:-1]

                        A = incidence_matrix(merged_graph, oriented=True)[:-1]
                        bi = np.fromiter(
                            (sum(sim.branch_currents[branch][-1]
                                 for _, _, branch in (set(self._graph.in_edges(node, keys=True)) -
                                                      set(merged_graph.in_edges(node, keys=True))))
                             for node in nodes),
                            dtype=float,
                        )
                        bo = np.fromiter(
                            (sum(sim.branch_currents[branch][-1]
                                 for _, _, branch in (set(self._graph.out_edges(node, keys=True)) -
                                                      set(merged_graph.out_edges(node, keys=True))))
                             for node in nodes),
                            dtype=float,
                        )

                        switch_currents_solutions = spsolve(A, bo - bi)
                        for i, (_, _, branch) in zip(switch_currents_solutions, merged_graph.edges(keys=True)):
                            sim.branch_voltages[branch].append(0.0)
                            sim.branch_currents[branch].append(i)

        def get_events(t1, t2, xinterp):
            return [event
                    for event in (
                        component.next_event(xinterp(component), t1, t2)
                        for component in self._component_branches)
                    if event is not None and t1 <= event <= t2]

        def get_next_event(t1, t2, xinterp):
            events = get_events(t1, t2, xinterp)
            return min(events) if events else None

        titer = iter(ts)
        t1 = next(titer)

        # Specially solve for t0.
        sc1, sc1graph, eq1 = get_equation(t1)
        x0 = np.zeros(len(eq1))
        result1 = solve_circuit(eq1, eq1, x0, t1, t1)
        store_result(t1, t1, eq1, result1, sc1, sc1graph)
        # Event handling is special in the region [t0, t0+ERP].
        # Events before t0 must be considered too, since they resolve inside the desired calculation range.
        # All events' (that have an influence, thus (t0-ERP, t0+ERP)) post-resolution points must be staged for
        # analysis.
        # Although less accurrate, for performance the state is assumed to be the result at t0.
        # It is possible to back-compute, but not worth the effort considering the interval is very small
        # (although as of the time writing this, all components use the trapezoidal integration rule which is symmetric
        # in this regard).
        for event in get_events(np.nextafter(t1 - self._EVENT_RESAMPLING_PRECISION, np.inf),
                                np.nextafter(t1 + self._EVENT_RESAMPLING_PRECISION, -np.inf),  # This is not a typo, it is t1.
                                lambda component: constant_interpolation(
                                    self._get_coupled_vi_vector(component, result1, eq1)
                                )):
            insort(ts, event + self._EVENT_RESAMPLING_PRECISION)

        t2 = next(titer)
        # Due to event handling, additional points after the desired range may be inserted, which make the loop
        # condition necessary.
        while t2 <= ts2:
            if simulation.is_cancelled:
                return simulation

            if t1 == t2:
                # Sometimes event times and externally desired time steps fall exactly on the same spot. In this case,
                # skip the redundant simulation.
                try:
                    t2 = next(titer)
                except StopIteration:
                    break

            sc2, sc2graph, eq2 = get_equation(t2)
            result2 = solve_circuit(eq1, eq2, result1, t1, t2)

            te1 = np.nextafter(t1 + self._EVENT_RESAMPLING_PRECISION, np.inf)
            te2 = np.nextafter(t2 + self._EVENT_RESAMPLING_PRECISION, -np.inf)

            event = get_next_event(
                te1,
                te2,
                lambda component: linear_interpolation(
                    t1,
                    self._get_coupled_vi_vector(component, result1, eq1),
                    t2,
                    self._get_coupled_vi_vector(component, result2, eq2),
                ),
            )

            if event is None:
                store_result(t1, t2, eq2, result2, sc2, sc2graph)
                t1 = t2
                try:
                    t2 = next(titer)
                except StopIteration:
                    break
            else:
                te1 = event - self._EVENT_RESAMPLING_PRECISION
                te2 = event + self._EVENT_RESAMPLING_PRECISION

                sc2, sc2graph, eq2 = get_equation(te1)
                result2 = solve_circuit(eq1, eq2, result1, t1, te1)

                store_result(t1, te1, eq2, result2, sc2, sc2graph)

                if te2 < t2:
                    t2 = te2

                insort(ts, te2)  # This operation has no considerable side-effects on the iterator.

                t1 = te1

            result1 = result2
            eq1 = eq2
            sc1graph = sc2graph

            # To allow cooperative programming, prefer to yield the thread here after a certain runtime.
            prefer_thread_yield()

        simulation.finish()
        return simulation

    def simulate_efm(self,
                     t0: float,
                     T: float,
                     interval_steps: int,
                     skips: List[int],
                     preferred_ground_nodes: Set = frozenset()) -> TransientEFMSimulation:
        """
        Simulates the circuit using the envelope-following-method (EFM).

        The simulation is *asynchronous*! A future object is returned that allows you to access results and progress
        during simulation runtime. The same notes as for the standard `simulate` apply.

        The EFM is beneficial to analyze systems faster with the trade-off of accuracy.
        With appropriate parameters and a suitable circuit this method can simulate significantly faster.
        This is especially beneficial for multi-rate systems with highly different intrinsical frequencies.

        The EFM requires you to know the intrinsical period time T where jumps can be properly made from.
        After that you define how many steps a single interval is simulated with and how many skips (`m`) should be
        performed.
        With this information the EFM performs skips according to following implicit equation:

        .. math::

            f(t + m T) = f(t) + \\frac12 m [f(t+T) - f(t) + f(t + (m+1) T) - f(t + mT)]

        The solution is then the so called "envelope", the guiding solution of the system.

        You can choose arbitrary consecutive skips organized in a list. If you simply want constant skipping, you can
        do `[s] * n` instead of writing out `[s, s, ..., s]`.

        For reference, see the paper at https://ieeexplore.ieee.org/document/4342106.

        :param t0:
            The initial time to start simulation from.
        :param T:
            Period time of a single interval.
        :param interval_steps:
            How many steps to simulate for a single interval.
        :param skips:
            Consecutive skips to perform encoded in a list.
        :param preferred_ground_nodes:
            Notes to prefer as ground (GND).
        :return:
            A `TransientEFMSimulation` object containing the result of the simulation.
            Note that computation happens *asynchronously*!.
        """

        if len(skips) <= 0:
            raise ValueError('skips must contain at least one value')
        if interval_steps < 1:
            raise ValueError('interval_steps must be greater than 1')

        simulation = TransientEFMSimulation(skips, self._component_branches, self._graph.nodes)

        def simulate_efm_async(simulation, t0, T, interval_steps, skips, preferred_ground_nodes):
            try:
                self._simulate_efm(simulation, t0, T, interval_steps, skips, preferred_ground_nodes)
            except Exception as ex:
                simulation.abort(ex)

        Thread(target=simulate_efm_async,
               args=(simulation, t0, T, interval_steps, skips, preferred_ground_nodes)).start()

        return simulation

    def _simulate_efm(self,
                      simulation: TransientEFMSimulation,
                      t0: float,
                      T: float,
                      interval_steps: int,
                      skips: List[int],
                      preferred_ground_nodes: Set = frozenset()):

        # shorthand prefixes for variables: li -> left interval, ri -> right interval

        li_ts1 = t0
        # s corresponds to m - 2 in the backing paper.
        for s in skips:
            if simulation.is_cancelled:
                return simulation

            li_ts2 = li_ts1 + T

            li_state1, state_compactification = compact([component.state for component in self.components])
            li_state1 = np.array(li_state1)
            subsim = self.simulate(li_ts1, li_ts2, interval_steps, preferred_ground_nodes)
            subsim.wait()
            li_state2, _ = compact([component.state for component in self.components])
            li_state2 = np.array(li_state2)
            li_state_delta = li_state2 - li_state1

            with simulation as sim:
                sim.append_from_simulation(subsim)

            ri_ts1 = li_ts2 + s * T
            ri_ts2 = ri_ts1 + T

            def efm_equation(ri_state1):
                for component, state in zip(self.components, uncompact(ri_state1, state_compactification)):
                    component.state = state

                ri_state1 = np.array(ri_state1)
                self.simulate(ri_ts1, ri_ts2, interval_steps, preferred_ground_nodes).wait()
                ri_state2, _ = compact([component.state for component in self.components])
                ri_state2 = np.array(ri_state2)
                ri_state_delta = ri_state2 - ri_state1

                # The equations are an adjusted version with better solution consistency.
                # Instead of calculating up to the end of the second interval, the efm-equations have to hold only up to
                # the beginning of the second interval. Effectively, m was changed from the original m to m - 1.
                return li_state2 - ri_state1 + s * 0.5 * (li_state_delta + ri_state_delta)

            initial_guess = li_state2 + s * li_state_delta  # Initial guess by forward euler approximation.
            satisfying_state = solve(efm_equation, initial_guess).x

            states = uncompact(satisfying_state, state_compactification)
            for component, state in zip(self.components, states):
                component.state = state

            li_ts1 = ri_ts1

            # To allow cooperative programming, prefer to yield the thread here after a certain runtime.
            prefer_thread_yield()

        # With steps > 0 being enforced above, referencing i won't cause any problems. The loop runs at least once.
        li_ts2 = li_ts1 + T
        subsim = self.simulate(li_ts1, li_ts2, interval_steps, preferred_ground_nodes)
        subsim.wait()

        with simulation as sim:
            sim.append_from_simulation(subsim)

        simulation.finish()
        return simulation

    def steadystate(self, T, steps, t0=0, preferred_ground_nodes: Set = frozenset()) -> TransientSteadyStateSimulation:
        """
        Finds the periodic steady-state solution of the circuit.

        The simulation is *asynchronous*! A future object is returned that allows you to access results and progress
        during simulation runtime. The same notes as for the standard `simulate` apply.

        Periodic steady-states occur for example for all linear circuits where complex analysis can be applied
        (i.e. circuits with sinusoidal sources, resistors, capacitors, inductors).
        This function requires you to pass ahead a suitable period `T` that denotes the circuit system's period time.
        For multi-rate circuits (i.e. with many sinusoidal sources), `T` becomes the least common multiple of all
        those period times Ts (the least common multiple is here extended to rational numbers - for non-rational
        frequencies, T can be approximated by rationalizing).

        The steady-state result is stored as a single period simulation inside the circuit's components and can be
        accessed exactly like with `simulate`. If the state-solution itself is of interest, respective states can
        be queried by using `component.state`.

        :param T:
            The circuit system's characteristic period time `T`.
        :param steps:
            Steps to simulate per period `T`.
            For sinusoidal sources, can be approximately set to `10 * T / min(Ts)`.
        :param t0:
            Initial time to start simulation from.
        :param preferred_ground_nodes:
            Notes to prefer as ground (GND).
        :return:
            A simulation object.
            Note that computation happens *asynchronously*!
        """
        simulation = TransientSteadyStateSimulation(t0, t0 + T, self._component_branches, self._graph.nodes)

        def steadystate_async(simulation, T, steps, t0, preferred_ground_nodes):
            try:
                self._steadystate(simulation, T, steps, t0, preferred_ground_nodes)
            except Exception as ex:
                simulation.abort(ex)

        Thread(target=steadystate_async,
               args=(simulation, T, steps, t0, preferred_ground_nodes)).start()

        return simulation

    def _steadystate(self,
                     simulation: TransientSteadyStateSimulation,
                     T: float,
                     steps: int,
                     t0=0,
                     preferred_ground_nodes=frozenset()):
        state0, state_compactification = compact([component.state for component in self.components])

        ts1 = t0
        ts2 = t0 + T

        def problem(compacted_state):
            states = uncompact(compacted_state, state_compactification)

            for component, state in zip(self.components, states):
                component.state = state

            self.simulate(ts1, ts2, steps, preferred_ground_nodes).wait()

            new_state, _ = compact([component.state for component in self.components])

            return compacted_state - np.array(new_state)

        state_result = solve(problem, state0).x

        states = uncompact(state_result, state_compactification)
        for component, state in zip(self.components, states):
            component.state = state

        subsim = self.simulate(ts1, ts2, steps, preferred_ground_nodes)
        subsim.wait()

        with simulation as sim:
            sim.extend_from_simulation(subsim)

        simulation.finish()
        return simulation

    def multirate_steadystate(self,
                              t0: float,
                              *Ts: float,
                              fast_steps: int = 10,
                              subdivisions: Union[int, Collection] = 8,
                              periodicity_tolerance: float = 2**-26,
                              preferred_ground_nodes: Set = frozenset()) -> TransientSteadyStateEFMSimulation:
        """
        Finds the periodic steady-state solution of the circuit using the envelope-following-method (EFM) for
        multi-rate systems.

        The simulation is *asynchronous*! A future object is returned that allows you to access results and progress
        during simulation runtime. The same notes as for the standard `simulate` apply.

        Periodic steady-states occur for example for all linear circuits where complex analysis can be applied
        (i.e. circuits with sinusoidal sources, resistors, capacitors, inductors).
        This function requires you to pass ahead a suitable fundamental periods `T` (inverse of fundamental frequency).
        For multi-rate circuits (i.e. with many sinusoidal sources), `T` becomes the least common multiple of all
        those period times :math:`T` (the least common multiple is here extended to rational numbers - for non-rational
        frequencies, T can be approximated by rationalizing).

        In contrast to a single-rate system, multi-rate systems have multiple fundamental frequencies. If they are
        vastly different, simulation can be extremely time-consuming because the fastest frequency has to be simulated
        in accordance to not miss out on its effects.
        Usually, such systems' "main behavior" is only slightly influenced by the fast-rate frequency. For this case,
        the EFM can be utilized and many fast-rate intervals can be safely skipped to increase performance significantly
        without missing on accuracy.

        For the EFM-equations, see method `simulate_efm`.

        For reference, see the paper at https://ieeexplore.ieee.org/document/4342106.

        :param t0:
            The starting time.
        :param Ts:
            Fundamental period times (inverse of fundamental frequency) the circuit contains.
        :param fast_steps:
            The steps to simulate inside a single fast-rate interval.
        :param subdivisions:
            How many steps shall be simulated via EFM inside the slow-rate interval.
            Effectively determines the skip intervals for the EFM.

            * If of type `int`: Divides the fundamental period time equally.
            * If of type `typing.Collection`: Relative time points to place into the fundamental period time.
              Elements must be of type `float`.
        :param periodicity_tolerance
            A rounding tolerance to apply to the fundamental period times to obtain the overall
            covering fundamental frequency. The smaller this value, the rougher the simulation
            might estimate the whole steady state solution, but if too high insignificant floating
            point number precision may be caught up and lead to an extreme overall fundamental
            period time and again reduce simulation precision because for a longer fundamental
            frequency more subdivisions should be made over the interval to get a fairly correct
            solution.

            Especially reduce this value if you require lower period times than this tolerance, otherwise
            they will be effectively rounded to 0.
        :param preferred_ground_nodes:
            Notes to prefer as ground (GND).
        :return:
            A simulation object containing the steady-state solution.
            Note that computation happens *asynchronously*!
        """
        T_slow = flcm(*Ts, tol=periodicity_tolerance, ignore_zeros=True)
        T_fast = min(Ts)

        # Quantization step to find properly aligned intervals / skips that can be used for EF-method.
        if isinstance(subdivisions, int):
            if subdivisions < 0:
                raise ValueError('parameter subdivisions must be 0 or greater')

            discrete_subdivisions = np.linspace(0, T_slow // T_fast - 1, subdivisions + 2)
        elif isinstance(subdivisions, Collection):
            discrete_subdivisions = np.sort(np.fromiter(chain((s for s in subdivisions if 0.0 <= s <= 1.0), [0.0, 1.0]),
                                                        dtype=float)) * (T_slow // T_fast - 1)
        else:
            raise TypeError()

        interval_diffs = np.diff(np.floor(discrete_subdivisions).astype(int))
        skips = np.fromiter(compress(interval_diffs, interval_diffs > 0), dtype=int) - 1

        simulation = TransientSteadyStateEFMSimulation(skips, self._component_branches, self._graph.nodes)

        def multirate_steadystate_async(simulation, t0, T_fast, T_fast_steps, skips, preferred_ground_nodes):
            try:
                self._multirate_steadystate(simulation, t0, T_fast, T_fast_steps, skips, preferred_ground_nodes)
            except Exception as ex:
                simulation.abort(ex)

        Thread(target=multirate_steadystate_async,
               args=(simulation, t0, T_fast, fast_steps, skips, preferred_ground_nodes)).start()

        return simulation

    def _multirate_steadystate(self,
                               simulation: TransientSteadyStateEFMSimulation,
                               t0: float,
                               T_fast: float,
                               T_fast_steps: int,
                               skips: List[int],
                               preferred_ground_nodes: Set = frozenset()):

        state0, state_compactification = compact([component.state for component in self.components])

        def problem(first_interval_state):
            states = uncompact(first_interval_state, state_compactification)
            for component, state in zip(self.components, states):
                component.state = state

            self.simulate_efm(t0, T_fast, T_fast_steps, skips, preferred_ground_nodes).wait()

            final_interval_state, _ = compact([component.state for component in self.components])
            final_interval_state = np.array(final_interval_state)
            return first_interval_state - final_interval_state

        steadystate_vector = solve(problem, state0).x

        states = uncompact(steadystate_vector, state_compactification)
        for component, state in zip(self.components, states):
            component.state = state

        subsim = self.simulate_efm(t0, T_fast, T_fast_steps, skips, preferred_ground_nodes)
        subsim.wait()

        with simulation as sim:
            sim.extend_from_simulation(subsim)

        simulation.finish()
        return simulation
