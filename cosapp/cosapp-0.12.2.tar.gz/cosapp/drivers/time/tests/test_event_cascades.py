import pytest
import numpy as np

from cosapp.systems import System
from cosapp.multimode import Event
from cosapp.recorders import DataFrameRecorder
from cosapp.drivers import RungeKutta
from .conftest import ScalarOde


class ChildFSystem(System):
    def setup(self):
        self.add_inward("x")
        input = self.add_event("input_event")
        self.add_event("e", trigger = input.filter("x >= -1"))

    def transition(self):
        if self.e.present:
            self.x = -self.x


class TopFSystem(System):
    def setup(self):
        self.add_child(ScalarOde("ode"), pulling=['f', 'df'])
        left = self.add_child(ChildFSystem("left"))
        right = self.add_child(ChildFSystem("right"))
        p = self.add_event("p", trigger = "f >= 1.")
        left.input_event.trigger = p
        right.input_event.trigger = p

    def transition(self):
        if self.p.present:
            self.f = 0.


def test_MultimodeSystem_filter():

    period = 0.15
    top = TopFSystem("top")
    driver = top.add_driver(RungeKutta("driver", order = 3, time_interval = (0, 1.5), dt = period))
    driver.add_recorder(DataFrameRecorder(includes=['f', 'left.x', 'right.x']), period = period)

    driver.set_scenario(
        init = {'f': 0., 'left.x': 1.5, 'right.x': -0.5},
        values = {'df': '2. * t'},
    )

    top.run_drivers()
    data = driver.recorder.export_data()

    te1 = 1.
    te2 = np.sqrt(2.)
    exact_t = np.array([0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, te1, te1, 1.05, 1.2, 1.35, te2, te2, 1.5])
    exact_f = [0, 0.0225, 0.09, 0.2025, 0.36, 0.5625, 0.81, 1, 0, 0.1025, 0.44, 0.8225, 1, 0, 0.25]
    exact_left_x = [1.5] * 8 + [-1.5] * 7
    exact_right_x = [-0.5] * 8 + [0.5] * 5 + [-0.5] * 2
    expected = {
        'f': exact_f,
        'left.x': exact_left_x,
        'right.x': exact_right_x,
        'time': exact_t
    }
    assert np.asarray(data['time']) == pytest.approx(np.asarray(expected['time']), abs=1.e-12)
    assert np.asarray(data['f']) == pytest.approx(expected['f'], abs=1.e-12)
    assert np.asarray(data['left.x']) == pytest.approx(expected['left.x'], abs=1.e-12)
    assert np.asarray(data['right.x']) == pytest.approx(expected['right.x'], abs=1.e-12)


class CascadingSystem(System):
    def setup(self):

        self.add_inward("x1", 0.5)
        self.add_inward("x2", 1.5)
        self.add_inward("x3", 2.5)

        self.add_child(ScalarOde("ode"), pulling=['f', 'df'])

        p = self.add_event("p", trigger = "f >= 0.863")
        p1 = self.add_event("p1", trigger = "x1 < 0.")
        p2 = self.add_event("p2", trigger = "x2 < 0.")
        p3 = self.add_event("p3", trigger = "x3 < 0.")

        self.add_event("merged_event", trigger = Event.merge(p, p1, p2, p3))

    def transition(self):
        if self.merged_event.present:
            self.x1 -= 1.
            self.x2 -= 1.
            self.x3 -= 1.


def test_MultimodeSystem_cascade():
    period = 0.1
    top = CascadingSystem("top")
    driver = top.add_driver(RungeKutta("driver", order = 3, time_interval = (0, 1), dt = period))
    driver.add_recorder(DataFrameRecorder(includes=['f', 'x1', 'x2', 'x3']), period = period)

    driver.set_scenario(
        init = {'f': 0., 'x1': 0.5, 'x2': 1.5, 'x3': 2.5},
        values = {'df': 1.},
    )

    top.run_drivers()
    data = driver.recorder.export_data()
    assert len(driver.event_data) == 5

    te = 0.863
    exact_t = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8] + [te] * 2 + [0.9, 1.]
    exact_f = exact_t
    exact_x1 = [0.5] * 10 + [-3.5] * 3
    exact_x2 = [1.5] * 10 + [-2.5] * 3
    exact_x3 = [2.5] * 10 + [-1.5] * 3
    expected = {
        'f': exact_f,
        'x1': exact_x1,
        'x2': exact_x2,
        'x3': exact_x3,
        'time': exact_t
    }
    assert np.asarray(data['time']) == pytest.approx(expected['time'], abs=1.e-12)
    assert np.asarray(data['f']) == pytest.approx(expected['f'], abs=1.e-12)
    assert np.asarray(data['x1']) == pytest.approx(expected['x1'], abs=1.e-12)
    assert np.asarray(data['x2']) == pytest.approx(expected['x2'], abs=1.e-12)
    assert np.asarray(data['x3']) == pytest.approx(expected['x3'], abs=1.e-12)


class CascadingParentSystem(System):
    def setup(self):
        self.add_child(ScalarOde("ode"), pulling = ['f', 'df'])
        self.add_event("p", trigger = "f >= 0.863")
        self.add_event("merged_event")


class CascadingChildSystem(System):
    def setup(self):
        self.add_inward("x")
        self.add_event("p", trigger = "x < 0.")
        self.add_event("m")

    def transition(self):
        if self.m.present:
            self.x -= 1.


def test_MultimodeSystem_cascade2():
    period = 0.1
    top = CascadingParentSystem("top")
    c1 = top.add_child(CascadingChildSystem("c1"))
    c2 = top.add_child(CascadingChildSystem("c2"))
    c3 = top.add_child(CascadingChildSystem("c3"))

    top.merged_event.trigger = Event.merge(top.p, c1.p, c2.p, c3.p)
    c1.m.trigger = top.merged_event
    c2.m.trigger = top.merged_event
    c3.m.trigger = top.merged_event

    driver = top.add_driver(RungeKutta("driver", order=3, time_interval=(0, 1), dt=period))
    driver.add_recorder(DataFrameRecorder(includes=['f', 'c1.x', 'c2.x', 'c3.x']), period=period)

    driver.set_scenario(
        init = {'f': 0., 'c1.x': 0.5, 'c2.x': 1.5, 'c3.x': 2.5},
        values = {'df': 1.},
    )

    top.run_drivers()
    data = driver.recorder.export_data()
    assert len(driver.event_data) == 5
    #print(driver.event_data)

    te = 0.863
    exact_t = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8] + [te] * 2 + [0.9, 1.]
    exact_f = exact_t
    exact_x1 = [0.5] * 10 + [-3.5] * 3
    exact_x2 = [1.5] * 10 + [-2.5] * 3
    exact_x3 = [2.5] * 10 + [-1.5] * 3
    expected = {
        'f': exact_f,
        'x1': exact_x1,
        'x2': exact_x2,
        'x3': exact_x3,
        'time': exact_t
    }
    assert np.asarray(data['f']) == pytest.approx(expected['f'], abs=1.e-12)
    assert np.asarray(data['time']) == pytest.approx(expected['time'], abs=1.e-12)
    assert np.asarray(data['c1.x']) == pytest.approx(expected['x1'], abs=1.e-12)
    assert np.asarray(data['c2.x']) == pytest.approx(expected['x2'], abs=1.e-12)
    assert np.asarray(data['c3.x']) == pytest.approx(expected['x3'], abs=1.e-12)

class LongCascadeSystem(System):
    def setup(self):

        # Primal time event, to be triggered a second time during the cascade
        # because of resets of f during certain transitions
        self.add_child(ScalarOde("ode"), pulling = ['f', 'df'])
        e_f = self.add_event("e_t", trigger = "f == 0.42")

        # Ad hoc variables for ensuring a cascade of events
        self.add_outward("x", np.array([-0.5,-1.5,-2.5,-3.5,-4.5]))
        e_0 = self.add_event("e_0", trigger = "x[0] > 0")
        e_1 = self.add_event("e_1", trigger = "x[1] > 0")
        e_2 = self.add_event("e_2", trigger = "x[2] > 0")
        e_3 = self.add_event("e_3", trigger = "x[3] > 0")
        e_4 = self.add_event("e_4", trigger = "x[4] > 0")

        # Merged event: all x_i's are changed at each discrete step
        self.add_event("any_event", trigger = Event.merge(e_f, e_0, e_1, e_2, e_3, e_4))

    def transition(self):
        if self.any_event.present:
            self.x += np.ones(5)
        if self.e_1.present: # e_f only unlocks after this transition
            self.f = -1.
        if self.e_4.present: # e_f triggers once again after this transition
            self.f = 1.

def test_MultimodeSystem_cascade_event_lock():
    """The event locking mechanism consists in preventing zero-crossing (ZC) events to erroneously trigger
    in rapid succession. Among others, it handles the case of bidirectional ZC events, which
    would be detected twice instead of only once without this mechanism: first when the ZC function
    reaches 0, and then, as soon as its value drifts away from 0.
    
    In this test, the first triggered event is top.e_f, interrupting an integration time step
    at time t=0.42. Then, events top.e_0 to top.e_4, in this order, will trigger successive
    discrete steps.
    
    The transition caused by e_1 makes the value of f switch from 0 to -1; this would cause event top.e_f
    to immediately trigger if the event locking mechanism was not (or incorrectly) implemented.
    On the other hand, as event top.e_f has to be unlocked just after this step, it has to trigger after
    the discrete step caused by top.e_4, as the associated transition makes the value of f switch from -1 to 1.

    As a result, a discrete loop of exactly seven discrete steps, each triggered by a single primitive event
    (e_f, e_0, e_1, e_2, e_3, e_4, e_f in this order), is expected.
    """
    period = 0.1
    top = LongCascadeSystem("top")

    driver = top.add_driver(RungeKutta("driver", order=3, time_interval=(0, 0.6), dt=period))
    driver.add_recorder(DataFrameRecorder(includes=['f', 'x']), period=period)

    driver.set_scenario(
        init = {'f': 0.},
        values = {'df': 1.},
    )

    top.run_drivers()
    data = driver.recorder.export_data()
    assert len(driver.event_data) == 8  # A single discrete loop of 7 steps

    expected = {
        'f': [0, 0.1, 0.2, 0.3, 0.4, 0.42, 1, 1.08, 1.18],
        'time': [0, 0.1, 0.2, 0.3, 0.4, 0.42, 0.42, 0.5, 0.6],
        'x': [
            [-0.5] * 6 + [6.5] * 3,  # time values of x[0]
            [-1.5] * 6 + [5.5] * 3,  # time values of x[1]
            [-2.5] * 6 + [4.5] * 3,  # etc.
            [-3.5] * 6 + [3.5] * 3,
            [-4.5] * 6 + [2.5] * 3,
        ],
    }

    assert np.asarray(data['f']) == pytest.approx(expected['f'], abs=1.e-12)
    assert np.asarray(data['time']) == pytest.approx(expected['time'], abs=1.e-12)
    
    # Transpose data such that x[i] contains time values of top.x[i]
    x = np.transpose(data['x'].tolist())

    for i, xi in enumerate(x):
        assert xi == pytest.approx(expected['x'][i], abs=1e-12), f"@ i = {i}"
