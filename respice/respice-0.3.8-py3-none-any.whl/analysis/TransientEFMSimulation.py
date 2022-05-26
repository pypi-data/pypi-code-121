from itertools import chain
from threading import RLock, Event
from typing import Iterable, List, Hashable, Tuple, Union, Collection, Optional

import numpy as np

from respice.collections import OneToManyInvertibleMapping
from respice.components import Component, SwitchBranch, Branch
from respice.itertools import flatten, pairwise
from respice.itertools.custom import deresolve, intersperse
from .TransientSimulation import TransientSimulation


class TransientEFMSimulation:
    class _LockedOperationsInterface:
        def __init__(self, parent):
            self._parent = parent

        @property
        def tss(self):
            return self._parent._tss

        @property
        def node_potentials(self):
            return self._parent._node_potentials

        @property
        def branch_voltages(self):
            return self._parent._branch_voltages

        @property
        def branch_currents(self):
            return self._parent._branch_currents

        @property
        def component_states(self):
            return self._parent._component_states

        @property
        def switch_states(self):
            return self._parent._switch_states

        def append_from_simulation(self, simulation: TransientSimulation):
            self.tss.append(simulation.get_timesteps())
            for node in self._parent._nodes:
                self.node_potentials[node].append(simulation.get_potentials(node))
            for branch in self._parent._components_to_branches.reverse:
                self.branch_voltages[branch].append(simulation.get_voltages(branch))
                self.branch_currents[branch].append(simulation.get_currents(branch))
                if isinstance(branch, SwitchBranch):
                    self.switch_states[branch].append(simulation.get_switch_states(branch))
            for component in self._parent._components_to_branches:
                self.component_states[component].append(simulation.get_states(component))

        def extend_from_simulation(self, simulation):
            self.tss.extend(simulation.get_interval_timesteps())
            for node in self._parent._nodes:
                self.node_potentials[node].extend(simulation.get_interval_potentials(node))
            for branch in self._parent._components_to_branches.reverse:
                self.branch_voltages[branch].extend(simulation.get_interval_voltages(branch))
                self.branch_currents[branch].extend(simulation.get_interval_currents(branch))
                if isinstance(branch, SwitchBranch):
                    self.switch_states[branch].extend(simulation.get_interval_switch_states(branch))
            for component in self._parent._components_to_branches:
                self.component_states[component].extend(simulation.get_interval_states(component))

    def __init__(self,
                 skips: List[float],
                 components_to_branches: OneToManyInvertibleMapping,
                 nodes: Iterable[Hashable]):

        self._skips = list(skips)

        self._components_to_branches = OneToManyInvertibleMapping(components_to_branches)
        self._nodes = list(nodes)
        self._tss = []
        self._node_potentials = {node: [] for node in self._nodes}
        self._branch_voltages = {branch: [] for branch in components_to_branches.reverse}
        self._branch_currents = {branch: [] for branch in components_to_branches.reverse}
        self._component_states = {component: [] for component in components_to_branches}
        self._switch_states = {branch: []
                               for branch in components_to_branches.reverse
                               if isinstance(branch, SwitchBranch)}

        self._modification_lock = RLock()
        self._finished = Event()
        self._cancelled = Event()
        self._aborted = Event()
        self._exception = None

    def __enter__(self) -> _LockedOperationsInterface:
        """
        Acquire the *modification lock*.

        :return:
            A view into the object data allowing direct, thread-safe modifications.
        """
        self._modification_lock.acquire()
        if self._finished.is_set():
            self._modification_lock.release()
            raise RuntimeError('modifications after the simulation has finished are prohibited')
        return self._LockedOperationsInterface(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Releases the modification lock.
        """
        self._modification_lock.release()

    def finish(self):
        """
        Signals the simulation to be finished.

        This function shouldn't be used from user perspective but is intended to be used from inside the simulation
        implementations.
        """
        with self._modification_lock:
            self._finished.set()

    def cancel(self):
        """
        Cancels an ongoing simulation.

        If the simulation has finished or is about to be finished, this function has no effect except still
        setting `is_cancelled` to `True`.
        """
        self._cancelled.set()
        self._finished.set()

    @property
    def is_cancelled(self) -> bool:
        """
        Determines whether the simulation was cancelled.
        """
        return self._cancelled.is_set()

    def abort(self, ex: Exception):
        """
        Aborts the simulation due to an error.

        This function shouldn't be used from user perspective but is intended to be used from inside the simulation
        implementations.

        :param ex:
            Exception that occurred causing the simulatino to abort.
        """
        self._exception = ex
        self._aborted.set()
        self._finished.set()

    @property
    def is_aborted(self) -> bool:
        """
        Determines whether the simulation was aborted due to an error.
        """
        return self._aborted.is_set()

    def wait(self, timeout: Optional[float] = None, throw: bool = True) -> bool:
        """
        Wait for the simulation to finish.

        :param timeout:
            Timeout to wait. If `None`, blocks infinitely until result is ready.
        :param throw:
            Whether exceptions from the computation thread are thrown in the calling thread.
        :return:
            `True` if the result is ready, `False` if not. Only meaningful when a timeout is given.
        """
        finished = self._finished.wait(timeout)
        if throw and self._aborted.is_set():
            raise self._exception
        return finished

    @staticmethod
    def _interpolate_intervals(tss, intervals, skips):
        interpolated_ts = list(tss[0])
        interpolated_vs = list(intervals[0])

        for ss, ((ts1, vs1), (ts2, vs2)) in zip(skips, pairwise(zip(tss, intervals))):
            merged_relative_ts = np.fromiter(
                deresolve(sorted(chain(ts1 - ts1[0], ts2 - ts2[0]))),
                dtype=float)

            distributed_ts = np.fromiter(
                flatten(merged_relative_ts + t
                        for t in np.linspace(ts1[-1], ts2[0], ss, endpoint=False)),
                dtype=float)

            interpolated_ts.extend(distributed_ts)

            linear_ramp = (distributed_ts - ts1[-1]) / (ts2[0] - ts1[-1])

            # Normalized voltages with the slope of the envelope taken into account to avoid jumps in the interpolation.
            nvs1 = vs1 - np.interp(ts1, [ts1[0], ts1[-1]], [vs1[0] - vs1[-1], 0])
            nvs2 = vs2 - np.interp(ts2, [ts2[0], ts2[-1]], [0, vs2[-1] - vs2[0]])

            interpolated_vs.extend(
                np.tile(np.interp(merged_relative_ts, ts1 - ts1[0], nvs1), ss) * (1 - linear_ramp) +
                np.tile(np.interp(merged_relative_ts, ts2 - ts2[0], nvs2), ss) * linear_ramp
            )

            # Also append the real result to interpolation.
            interpolated_ts.extend(ts2)
            interpolated_vs.extend(vs2)

        return np.fromiter(interpolated_ts, dtype=float), np.fromiter(interpolated_vs, dtype=float)

    @staticmethod
    def _retrieve_envelope(intervals):
        return TransientEFMSimulation._straighten([x[0], x[-1]] for x in intervals)

    @staticmethod
    def _straighten(intervals):
        return np.fromiter(flatten(intervals), dtype=float)

    def get_interval_timesteps(self) -> List[np.ndarray]:
        """
        Returns all discrete time steps simulated, structured accordingly into EFM intervals.
        """
        with self._modification_lock:
            return list(np.array(ts) for ts in self._tss)

    def get_timesteps(self) -> np.ndarray:
        """
        Returns all discrete time steps simulated.
        """
        with self._modification_lock:
            return self._straighten(self._tss)

    def get_envelope_timesteps(self) -> np.ndarray:
        """
        Returns all discrete time steps of the simulation envelope.
        """
        with self._modification_lock:
            return self._retrieve_envelope(self._tss)

    def get_interval_potentials(self, node: Hashable) -> List[np.ndarray]:
        """
        Returns the calculated potentials (in Volts) at the given node, structured accordingly into EFM intervals.

        :param node:
            The node.
        """
        with self._modification_lock:
            return self._node_potentials[node]

    def get_potentials(self, node: Hashable) -> np.ndarray:
        """
        Returns the calculated potentials (in Volts) at the given node.

        :param node:
            The node.
        """
        return self._straighten(self.get_interval_potentials(node))

    def get_envelope_potentials(self, node: Hashable) -> np.ndarray:
        """
        Returns the calculated potentials (in Volts) at the given node of the simulation envelope.

        :param node:
            The node.
        """
        return self._retrieve_envelope(self.get_interval_potentials(node))

    def get_interpolated_potentials(self, node: Hashable) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Creates an interpolation using the solved potentials.

        The EFM (Envelope Following Method) skips over large intervals. For these skipped intervals, this function
        creates a simple interpolation :math:`f_{m \leftrightarrow n}` by linearly blending two adjacent EFM intervals
        :math:`f_m` and :math:`f_n` with the blend function :math:`q` repeating the interval across the skipped section.

        .. math::

            (m + 1) T < t < n T: & q(t) = \frac{t - (m+1)T}{(n - m - 1)T}, \\
            & f_{m \leftrightarrow n}(t) = (1 - q) \cdot f_m(t \mod T) + q \cdot f_n(t \mod T)

        :param node:
            The node.
        :return:
            The interpolation time steps measured in seconds and interpolated potentials measured in Volts.
        """
        with self._modification_lock:
            return self._interpolate_intervals(
                self.get_interval_timesteps(),
                self.get_interval_potentials(node),
                self._skips,
            )

    t = get_timesteps  # Shorthand function

    def get_interval_voltages(self,
                              entity: Union[Component, Branch, Hashable],
                              target_node: Hashable = None) -> List[np.ndarray]:
        """
        Returns the solved voltages over a given entity, structured accordingly into EFM intervals.

        :param entity:
            Can be either:
            * a component (where `default_branch` must be set and not return `None` - e.g. two-terminal-components).
            * a branch.
            * a node.
        :param target_node:
            If `entity` is a (source) node, this parameter denotes the target node to get the voltages from in between.
        :return:
            The solved EFM-interval voltages measured in Volts as a list of `np.ndarray`s.
        """
        if target_node is None:
            # Lookup by single component or branch.
            branch = entity.default_branch if isinstance(entity, Component) else entity

            with self._modification_lock:
                return [np.array(voltages) for voltages in self._branch_voltages[branch]]
        else:
            # Lookup between nodes.
            with self._modification_lock:
                return [np.fromiter((target - source for target, source in zip(targets, sources)),
                                    dtype=float)
                        for targets, sources in zip(self._node_potentials[target_node],
                                                    self._node_potentials[entity])]

    def get_voltages(self, entity: Union[Component, Branch, Hashable], target_node: Hashable = None) -> np.ndarray:
        """
        Returns the solved voltages over a given entity.

        :param entity:
            Can be either:
            * a component (where `default_branch` must be set and not return `None` - e.g. two-terminal-components).
            * a branch.
            * a node.
        :param target_node:
            If `entity` is a (source) node, this parameter denotes the target node to get the voltages from in between.
        :return:
            The solved voltages measured in Volts in form of an `np.ndarray`.
        """
        return self._straighten(self.get_interval_voltages(entity, target_node))

    v = get_voltages  # Shorthand function

    def get_envelope_voltages(self,
                              entity: Union[Component, Branch, Hashable],
                              target_node: Hashable = None) -> np.ndarray:
        """
        Returns the solved voltages over a given entity of the simulation envelope.

        :param entity:
            Can be either:
            * a component (where `default_branch` must be set and not return `None` - e.g. two-terminal-components).
            * a branch.
            * a node.
        :param target_node:
            If `entity` is a (source) node, this parameter denotes the target node to get the voltages from in between.
        :return:
            The solved voltages measured in Volts in form of an `np.ndarray`.
        """
        return self._retrieve_envelope(self.get_interval_voltages(entity, target_node))

    def get_interpolated_voltages(self,
                                  entity: Union[Component, Branch, Hashable],
                                  target_node: Hashable = None) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Creates an interpolation using the solved voltages.

        The EFM (Envelope Following Method) skips over large intervals. For these skipped intervals, this function
        creates a simple interpolation :math:`f_{m \leftrightarrow n}` by linearly blending two adjacent EFM intervals
        :math:`f_m` and :math:`f_n` with the blend function :math:`q` repeating the interval across the skipped section.

        .. math::

            (m + 1) T < t < n T: & q(t) = \frac{t - (m+1)T}{(n - m - 1)T}, \\
            & f_{m \leftrightarrow n}(t) = (1 - q) \cdot f_m(t \mod T) + q \cdot f_n(t \mod T)

        :param entity:
            Can be either:
            * a component (where `default_branch` must be set and not return `None` - e.g. two-terminal-components).
            * a branch.
            * a node.
        :param target_node:
            If `entity` is a (source) node, this parameter denotes the target node to get the voltages from in between.
        :return:
            The interpolation time steps measured in seconds and interpolated voltages measured in Volts.
        """
        with self._modification_lock:
            return self._interpolate_intervals(
                self.get_interval_timesteps(),
                self.get_interval_voltages(entity, target_node),
                self._skips,
            )

    def get_interval_currents(self, entity: Union[Component, Branch]) -> List[np.ndarray]:
        """
        Returns the solved currents over a given entity, structured accordingly into EFM intervals.

        :param entity:
            Can be either:
            * a component (where `default_branch` must be set and not return `None` - e.g. two-terminal-components).
            * a branch.
        :return:
            The solved currents measured in Amperes in form of an `np.ndarray`.
        """
        branch = entity.default_branch if isinstance(entity, Component) else entity

        with self._modification_lock:
            return [np.array(currents) for currents in self._branch_currents[branch]]

    def get_currents(self, entity: Union[Component, Branch]) -> np.ndarray:
        """
        Returns the solved currents over a given entity.

        :param entity:
            Can be either:
            * a component (where `default_branch` must be set and not return `None` - e.g. two-terminal-components).
            * a branch.
        :return:
            The solved currents measured in Amperes in form of an `np.ndarray`.
        """
        return self._straighten(self.get_interval_currents(entity))

    i = get_currents  # Shorthand function

    def get_envelope_currents(self, entity: Union[Component, Branch]) -> np.ndarray:
        """
        Returns the solved currents over a given entity of the simulation envelope.

        :param entity:
            Can be either:
            * a component (where `default_branch` must be set and not return `None` - e.g. two-terminal-components).
            * a branch.
        :return:
            The solved currents measured in Amperes in form of an `np.ndarray`.
        """
        return self._retrieve_envelope(self.get_interval_currents(entity))

    def get_interpolated_currents(self, entity: Union[Component, Branch]) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Creates an interpolation using the solved currents.

        The EFM (Envelope Following Method) skips over large intervals. For these skipped intervals, this function
        creates a simple interpolation :math:`f_{m \leftrightarrow n}` by linearly blending two adjacent EFM intervals
        :math:`f_m` and :math:`f_n` with the blend function :math:`q` repeating the interval across the skipped section.

        .. math::

            (m + 1) T < t < n T: & q(t) = \frac{t - (m+1)T}{(n - m - 1)T}, \\
            & f_{m \leftrightarrow n}(t) = (1 - q) \cdot f_m(t \mod T) + q \cdot f_n(t \mod T)

        :param entity:
            Can be either:
            * a component (where `default_branch` must be set and not return `None` - e.g. two-terminal-components).
            * a branch.
        :return:
            The interpolation time steps measured in seconds and interpolated currents measured in Amperes.
        """
        with self._modification_lock:
            return self._interpolate_intervals(
                self.get_interval_timesteps(),
                self.get_interval_currents(entity),
                self._skips,
            )

    def get_interval_power(self, *entities: Union[Component, Branch]) -> List[np.ndarray]:
        """
        Calculates power consumption over multiple components or branches, structured accordingly into EFM intervals.

        :param entities:
            (Multiple) entities to calculate power for. If a component is given, its default branch is taken.
        :return:
            The power measured in Watts.
        """
        with self._modification_lock:
            powers = ([[v * i for v, i in zip(intv_v, intv_i)]
                       for intv_v, intv_i in zip(self.get_interval_voltages(entity),
                                                 self.get_interval_currents(entity))]
                      for entity in entities)

            return [np.fromiter((sum(p) for p in zip(*intv_p)), dtype=float) for intv_p in zip(*powers)]

    def get_power(self, *entities: Union[Component, Branch]) -> np.ndarray:
        """
        Calculates power consumption over multiple components or branches.

        :param entities:
            (Multiple) entities to calculate power for. If a component is given, its default branch is taken.
        :return:
            The power measured in Watts.
        """
        return self._straighten(self.get_interval_power(*entities))

    def get_envelope_power(self, *entities: Union[Component, Branch]) -> np.ndarray:
        """
        Calculates power consumption over multiple components or branches of the simulation envelope.

        :param entities:
            (Multiple) entities to calculate power for. If a component is given, its default branch is taken.
        :return:
            The power measured in Watts.
        """
        return self._retrieve_envelope(self.get_interval_power(*entities))

    def get_interpolated_power(self, *entities: Union[Component, Branch]) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Creates an interpolation using the solved powers.

        The EFM (Envelope Following Method) skips over large intervals. For these skipped intervals, this function
        creates a simple interpolation :math:`f_{m \leftrightarrow n}` by linearly blending two adjacent EFM intervals
        :math:`f_m` and :math:`f_n` with the blend function :math:`q` repeating the interval across the skipped section.

        .. math::

            (m + 1) T < t < n T: & q(t) = \frac{t - (m+1)T}{(n - m - 1)T}, \\
            & f_{m \leftrightarrow n}(t) = (1 - q) \cdot f_m(t \mod T) + q \cdot f_n(t \mod T)

        :param entities:
            (Multiple) entities to calculate power for. If a component is given, its default branch is taken.
        :return:
            The interpolation time steps measured in seconds and interpolated powers measured in Watts.
        """
        with self._modification_lock:
            return self._interpolate_intervals(
                self.get_interval_timesteps(),
                self.get_interval_power(*entities),
                self._skips,
            )

    p = get_power  # Shorthand function

    def get_interval_states(self, component: Component) -> List[List[np.ndarray]]:
        """
        Returns the computed states of the component, structured accordingly to EFM intervals.

        :param component:
            The component.
        :return:
            The state vectors. Refer to each component type individually which entry means what state.
        """
        with self._modification_lock:
            return [[np.array(state) for state in states] for states in self._component_states[component]]

    def get_states(self, component: Component) -> List[np.ndarray]:
        """
        Returns the computed states of the component.

        :param component:
            The component.
        :return:
            The state vectors. Refer to each component type individually which entry means what state.
        """
        return list(flatten(self.get_interval_states(component)))

    def get_envelope_states(self, component: Component) -> List[np.ndarray]:
        """
        Returns the computed states of the component of the simulation envelope.

        :param component:
            The component.
        :return:
            The state vectors. Refer to each component type individually which entry means what state.
        """
        return list(flatten([x[0], x[-1]] for x in self.get_interval_states(component)))

    def get_interpolated_states(self, component: Component) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Creates an interpolation using the solved component states.

        The EFM (Envelope Following Method) skips over large intervals. For these skipped intervals, this function
        creates a simple interpolation :math:`f_{m \leftrightarrow n}` by linearly blending two adjacent EFM intervals
        :math:`f_m` and :math:`f_n` with the blend function :math:`q` repeating the interval across the skipped section.

        .. math::

            (m + 1) T < t < n T: & q(t) = \frac{t - (m+1)T}{(n - m - 1)T}, \\
            & f_{m \leftrightarrow n}(t) = (1 - q) \cdot f_m(t \mod T) + q \cdot f_n(t \mod T)

        :param component:
            The component.
        :return:
            The interpolation time steps measured in seconds and interpolated states.
        """
        with self._modification_lock:
            ts = np.zeros(0)
            interpolations = []
            for states in zip(*(list(zip(*interval)) for interval in self.get_interval_states(component))):
                ts, interpolated = self._interpolate_intervals(self.get_interval_timesteps(), states, self._skips)
                interpolations.append(interpolated)

            return ts, np.transpose(interpolations)

    s = get_states  # Shorthand function

    def get_interval_switch_states(self, switch: SwitchBranch) -> List[np.ndarray]:
        """
        Returns the computed switch states during simulation, structured accordingly into EFM intervals.

        :param switch:
            The switch.
        :return:
            The switch states, an array with `bool`s.
        """
        with self._modification_lock:
            return [np.array(states) for states in self._switch_states[switch]]

    def get_switch_states(self, switch: SwitchBranch) -> np.ndarray:
        """
        Returns the computed switch states during simulation.

        :param switch:
            The switch.
        :return:
            The switch states, an array with `bool`s.
        """
        return np.fromiter(flatten(self.get_interval_switch_states(switch)), dtype=bool)

    def plot(self, *entities: Union[Component, Branch], features: Collection[str] = 'vip', throw: bool = True):
        """
        Plots the result.

        Uses Plotly to present graphs in your browser. Make sure to have it installed.

        :param entities:
            Optional specific entities to plot. If none are specified, all available are plotted.
            Branches as well as components can be specified. In case the component defines a valid `default_branch`,
            this branch's data will be plotted. If `default_branch` returns `None`, all associated branches of this
            component will be plotted.

            Duplicate branches are filtered properly and won't be plotted twice.
        :param features:
            What kind of plots to make. Must be an iterable made out of following values:
            * v: voltage plot
            * i: current plot
            * p: power plot
            * s: component states
            * c: *c*ontrolled switch states
        :param throw:
            Whether exceptions from the computation thread are thrown in the calling thread.
            Set it to `False` if you also want to print partial results.
        """
        if not features:
            raise ValueError('no features specified')

        component_features = {}
        branch_features = {}
        for i, feature in enumerate(features, start=1):
            if feature == 'v' or feature == 'i' or feature == 'p' or feature == 'c':
                branch_features[i] = feature
            elif feature == 's':
                component_features[i] = feature
            else:
                raise ValueError(f'invalid feature: {feature}')

        self.wait(throw=throw)

        # Determine necessary components and respective branches to plot.
        if entities:
            plotset = {}
            for entity in entities:
                if isinstance(entity, Component):
                    component = entity
                    plotset[component] = (self._components_to_branches[component]
                                          if component.default_branch is None else
                                          {component.default_branch})
                else:
                    branch = entity
                    plotset[self._components_to_branches.reverse[branch]] = branch
        else:
            plotset = self._components_to_branches

        from itertools import cycle

        try:
            from plotly.subplots import make_subplots
            from plotly.graph_objects import Scatter
            from plotly.express import colors
        except ImportError:
            raise RuntimeError('plotly not found! Please install before using this function.')

        fig = make_subplots(rows=len(features), cols=1, shared_xaxes=True)

        colorcycle = cycle(colors.qualitative.Plotly)

        for component, branches in plotset.items():
            color = next(colorcycle)

            for i, feature in component_features.items():
                # Currently there is only the "state"-feature, no need for an if-else.

                intervals = list(zip(*(list(zip(*interval)) for interval in self.get_interval_states(component))))
                envelopes = list(zip(*self.get_envelope_states(component)))
                ts, interpolations = self.get_interpolated_states(component)
                interpolations = np.transpose(interpolations)

                for k in range(len(intervals)):
                    fig.append_trace(
                        Scatter(
                            x=list(intersperse(self._tss, None)),
                            y=list(intersperse(intervals[k], None)),
                            legendgroup=f'state({str(component)})[{k}] (simulated)',
                            name=f'state({component})[{k}] (simulated)',
                            mode='lines',
                            line={'color': color},
                            showlegend=True,
                        ),
                        row=i,
                        col=1,
                    )

                    fig.append_trace(
                        Scatter(
                            x=self.get_envelope_timesteps(),
                            y=envelopes[k],
                            legendgroup=f'state({str(component)})[{k}] (envelope)',
                            name=f'state({component})[{k}] (envelope)',
                            mode='lines',
                            line={'color': color, 'dash': 'dash'},
                            showlegend=True,
                        ),
                        row=i,
                        col=1,
                    )

                    fig.append_trace(
                        Scatter(
                            x=ts,
                            y=interpolations[k],
                            legendgroup=f'state({str(component)})[{k}] (interpolated)',
                            name=f'state({component})[{k}] (interpolated)',
                            mode='lines',
                            line={'color': color, 'dash': 'dot', 'width': 0.85},
                            showlegend=True,
                            visible='legendonly',
                        ),
                        row=i,
                        col=1,
                    )

            for branch in branches:
                showlegend = True
                for i, feature in branch_features.items():
                    if feature == 'v':
                        get_interval_solutions = self.get_interval_voltages
                        get_envelope = self.get_envelope_voltages
                        get_interpolation = self.get_interpolated_voltages
                    elif feature == 'i':
                        get_interval_solutions = self.get_interval_currents
                        get_envelope = self.get_envelope_currents
                        get_interpolation = self.get_interpolated_currents
                    elif feature == 'p':
                        get_interval_solutions = self.get_interval_power
                        get_envelope = self.get_envelope_power
                        get_interpolation = self.get_interpolated_power
                    elif feature == 'c':
                        if not isinstance(branch, SwitchBranch):
                            continue

                        get_interval_solutions = lambda branch: [[1 if s else 0 for s in interval]
                                                                 for interval in self.get_interval_switch_states(branch)]
                        get_envelope = None
                        get_interpolation = None
                    else:
                        raise AssertionError

                    fig.append_trace(
                        Scatter(
                            x=list(intersperse(self._tss, None)),
                            y=list(intersperse(get_interval_solutions(branch), None)),
                            legendgroup=f'{str(component)} (simulated)',
                            name=f'{str(branch)} (simulated)',
                            mode='lines',
                            line={'color': color},
                            showlegend=showlegend,
                        ),
                        row=i,
                        col=1,
                    )

                    if get_envelope is not None:
                        fig.append_trace(
                            Scatter(
                                x=self.get_envelope_timesteps(),
                                y=get_envelope(branch),
                                legendgroup=f'{str(component)} (envelope)',
                                name=f'{str(branch)} (envelope)',
                                mode='lines',
                                line={'color': color, 'dash': 'dash'},
                                showlegend=showlegend,
                            ),
                            row=i,
                            col=1,
                        )

                    if get_interpolation is not None:
                        ts, interpolated_solutions = get_interpolation(branch)

                        fig.append_trace(
                            Scatter(
                                x=ts,
                                y=interpolated_solutions,
                                legendgroup=f'{str(component)} (interpolated)',
                                name=f'{str(branch)} (interpolated)',
                                mode='lines',
                                line={'color': color, 'dash': 'dot', 'width': 0.85},
                                showlegend=showlegend,
                                visible='legendonly',
                            ),
                            row=i,
                            col=1,
                        )

                    showlegend = False

        # Update xaxis properties
        axis_labels = {
            'v': 'voltage V [V]',
            'i': 'current I [A]',
            'p': 'power P [W]',
            's': 'state',
            'c': 'switch state',
        }

        for i, feature in enumerate(features, start=1):
            fig.update_yaxes(row=i, col=1, title_text=axis_labels[feature])

            if feature == 'c':
                fig.update_yaxes(
                    row=i,
                    col=1,
                    tickmode='array',
                    tickvals=[0, 1],
                    ticktext=['off', 'on'],
                )

        fig.update_xaxes(row=len(features), col=1, title_text="time t [s]")
        fig.update_layout(title="Transient EFM Simulation Results")

        fig.show()

    def save(self, filename: str):
        """
        Stores quickly simulation data inside the given circuit to CSV-format.

        :param filename:
            The filename to store the data in.
        """
        self.wait()

        data = [('t', self.get_timesteps())]

        # Additionally iterating over components sorts branches by component,
        # thus makes it easier for humans to read.
        for component in self._components_to_branches:
            for branch in self._components_to_branches[component]:
                data.append((f'v({str(branch)})', self.get_voltages(branch)))
                data.append((f'i({str(branch)})', self.get_currents(branch)))
                if isinstance(branch, SwitchBranch):
                    data.append((f'switchstate({str(branch)})',
                                 ['on' if ss else 'off' for ss in self.get_switch_states(branch)]))

            for i, state in enumerate(zip(*self.get_states(component)), start=1):
                data.append((f'state({str(component)})[{i}]', state))

        import csv
        with open(filename, 'w', newline='') as fl:
            w = csv.writer(fl)
            w.writerow(name for name, _ in data)
            w.writerows(zip(*(d for _, d in data)))

    def print_progress(self):
        try:
            import rich.progress
        except ImportError:
            raise RuntimeError('rich not found! Please install before using this function.')

        progress = rich.progress.Progress(
            '[progress.description]{task.description}',
            rich.progress.BarColumn(),
            '[progress.percentage]{task.percentage:>3.1f}% ({task.completed}/{task.total})',
            '•',
            'ETC',
            rich.progress.TimeRemainingColumn(),
            refresh_per_second=2,
        )

        total = len(self._skips) + 1
        with progress:
            task = progress.add_task(
                'simulate (EFM)',
                total=total,
                completed=len(self._tss),
            )

            while not self._finished.wait(0.5):
                progress.update(task, completed=len(self._tss))

            progress.update(task, completed=total)
