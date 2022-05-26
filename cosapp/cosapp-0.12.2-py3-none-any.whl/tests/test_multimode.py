"""Various integration tests with multimode systems
"""
import pytest
import numpy

from cosapp.ports import Port
from cosapp.systems import System
from cosapp.drivers import EulerExplicit, NonLinearSolver
from cosapp.recorders import DataFrameRecorder
from typing import List


class ElecPort(Port):
    def setup(self):
        self.add_variable('V', 0.0, unit='V')
        self.add_variable('I', 1.0, unit='A')


class Resistor(System):
    """Resistor component

    Attributes:
        R : float
            Resistance in Ohms
    """
    def setup(self, R=0):
        self.add_input(ElecPort, 'elec_in')
        self.add_output(ElecPort, 'elec_out')

        self.add_inward('R', abs(float(R)), unit='ohm', desc='Internal resistance')
        self.add_outward('deltaV')

    def compute(self):
        self.elec_out.I = self.elec_in.I
        self.elec_out.V = self.elec_in.V - (self.elec_out.I * self.R)
        self.deltaV = self.elec_in.V - self.elec_out.V


class Node(System):
    """System representing an electric circuit node with
    an arbitrary number of incoming and outgoing branches.

    Nodes provide an off-design problem ensuring potential equality
    and global current balance (see 'Unknowns' and 'Equations' below).

    Constructor arguments:
    ----------------------
    - n_in [int], optional: Number of incoming branches. Defaults to 1.
    - n_out [int], optional: Number of outgoing branches. Defaults to 1.

    Properties:
    -----------
    - n_in [int]: Number of incoming branches.
    - n_out [int]: Number of outgoing branches.
    - incoming: Tuple containing all `ElecPort` inputs.
    - outgoing: Tuple containing all `ElecPort` outputs.

    Unknowns:
    ---------
    - n_out current fractions (one per outgoing branch), if n_out > 1.

    Equations:
    ----------
    - (n_in - 1) potential equality conditions for incoming branches.
    - 1 total current balance equation, if n_out > 1.
    """
    def setup(self, n_in=1, n_out=1):
        """Node constructor.

        Arguments:
        -----------
        - n_in [int], optional: Number of incoming branches. Defaults to 1.
        - n_out [int], optional: Number of outgoing branches. Defaults to 1.
        """
        self.add_property('n_in', int(n_in))
        self.add_property('n_out', int(n_out))

        if min(self.n_in, self.n_out) < 1:
            raise ValueError("Node needs at least one incoming and one outgoing branch")

        self.add_property('incoming',
            tuple(
                self.add_input(ElecPort, f"elec_in{i}")
                for i in range(self.n_in)
            )
        )
        self.add_property('outgoing',
            tuple(
                self.add_output(ElecPort, f"elec_out{i}")
                for i in range(self.n_out)
            )
        )

        if self.n_out > 1:  # unnecessary otherwise
            self.add_inward('I_frac',
                value = numpy.full(self.n_out, 1.0 / self.n_out),
                desc = f"Current fractions distributed to outgoing branches",
                limits = (0, 1),
            )
            self.add_unknown('I_frac', lower_bound=0, upper_bound=1)
            self.add_equation('sum(I_frac) == 1', name='Current balance')

        for i in range(1, self.n_in):   # case where node is 'joiner'
            self.add_equation(f'elec_in{i}.V == elec_in0.V')

        self.add_outward('V', 0., unit='V', desc='Actual node voltage')
        self.add_outward('sum_I_in', 0., unit='A', desc='Sum of all incoming currents')
        self.add_outward('sum_I_out', 0., unit='A', desc='Sum of all outgoing currents')

    def compute(self):
        # Sum of incoming currents
        self.sum_I_in = I = sum(port.I for port in self.incoming)

        # Output voltage
        self.V = V = numpy.mean([port.V for port in self.incoming])

        # Current distribution
        try:
            I_frac = self.I_frac
        except AttributeError:
            I_frac = [1]
        for j, port in enumerate(self.outgoing):
            port.V = V
            port.I = I * I_frac[j]

        self.sum_I_out = I * sum(I_frac)

    @classmethod
    def make(cls, parent, name, incoming: List[ElecPort], outgoing: List[ElecPort], pulling=None) -> "Node":
        """Factory method making appropriate connections with parent system"""
        node = cls(name, n_in=max(len(incoming), 1), n_out=max(len(outgoing), 1))
        parent.add_child(node, pulling=pulling)
        
        for branch_elec, node_elec in zip(incoming, node.incoming):
            parent.connect(branch_elec, node_elec)
        
        for branch_elec, node_elec in zip(outgoing, node.outgoing):
            parent.connect(branch_elec, node_elec)

        return node


class TwoWayCircuit(System):
    def setup(self):
        self.add_outward_modevar('upbranch', True)
        self.reconfig()

        self.add_outward('Requiv', 0.0)
        self.add_outward('deltaV', 0.0)
        self.add_event('switch', trigger='elec_in.V == elec_out.V')
    
    def compute(self):
        self.deltaV = self.elec_in.V - self.elec_out.V
        I = self.elec_in.I
        self.Requiv = self.deltaV / I if abs(I) > 0 else numpy.nan

    def transition(self):
        if self.switch.present:
            self.upbranch = not self.upbranch
            self.reconfig()

    def reconfig(self):
        for name in self.children:
            self.pop_child(name)
        pulled_ports = ['elec_in', 'elec_out']
        if self.upbranch:
            child = self.add_child(Resistor("R1", R=100), pulling=pulled_ports)
        else:
            child = self.add_child(Resistor("R2", R=500), pulling=pulled_ports)
        self.elec_out.V = child.elec_out.V = 0.0


class TwoWayCircuitWithEq(System):
    def setup(self):
        self.add_outward_modevar('upbranch', True)
        self.add_child(Resistor("R0", R=100), pulling=['elec_in', 'elec_out'])
        self.reconfig()

        self.add_outward('Requiv', 0.0)
        self.add_outward('deltaV', 0.0)
        self.add_event('switch', trigger='elec_in.V == elec_out.V')
    
    def compute(self):
        self.deltaV = self.elec_in.V - self.elec_out.V
        I = self.elec_in.I
        self.Requiv = self.deltaV / I if abs(I) > 0 else numpy.nan

    def transition(self):
        if self.switch.present:
            self.upbranch = not self.upbranch
            self.reconfig()

    def reconfig(self):
        problem = self._math
        if not self.upbranch and problem.shape == (0, 0):
            self.add_unknown("R0.R").add_equation("R0.R == 500")
        else:
            problem.clear()
            self.R0.R = 100


@pytest.fixture
def case_TwoWayCircuit():
    circuit = TwoWayCircuit('circuit')
    driver = circuit.add_driver(
        EulerExplicit(time_interval=[0, 1], dt=0.1)
    )
    driver.add_recorder(
        DataFrameRecorder(includes=['elec_in.*', 'elec_out.V', 'Requiv', 'deltaV', 'upbranch']),
        period = 0.1,
    )
    solver = driver.add_child(NonLinearSolver('solver', tol=1e-9))
    solver.add_unknown('elec_in.I').add_equation("elec_out.V == 0")
    return circuit, driver


def test_TwoWayCircuit(case_TwoWayCircuit):
    circuit, driver = case_TwoWayCircuit
    omega = 6
    driver.set_scenario(
        values = {
            'elec_in.V': f"cos({omega} * t)",
        }
    )
    circuit.run_drivers()

    df = driver.recorder.export_data()
    # print("", df.drop(['Section', 'Status', 'Error code'], axis=1), sep="\n")

    for i, row in df.iterrows():
        I = row['elec_in.I']
        R = row['Requiv']
        context = f"row #{i}, I = {I}, {list(circuit.exec_order)}"
        if I > 1e-12:
            assert R == pytest.approx(100), context
        elif I < -1e-12:
            assert R == pytest.approx(500), context
    
    assert [record.time for record in driver.recorded_events] == pytest.approx(
        [(2 * k + 1) * 0.5 * numpy.pi / omega for k in range(2)]
    )


@pytest.fixture
def case_TwoWayCircuitWithEq():
    circuit = TwoWayCircuitWithEq('circuit')
    driver = circuit.add_driver(
        EulerExplicit(time_interval=[0, 1], dt=0.1)
    )
    driver.add_recorder(
        DataFrameRecorder(includes=['elec_in.*', 'elec_out.V', 'Requiv', 'deltaV', 'upbranch']),
        period = 0.1,
    )
    solver = driver.add_child(NonLinearSolver('solver', tol=1e-9))
    solver.add_unknown('elec_in.I').add_equation("elec_out.V == 0")
    return circuit, driver


def test_TwoWayCircuitWithEq(case_TwoWayCircuitWithEq):
    circuit, driver = case_TwoWayCircuitWithEq
    omega = 6
    driver.set_scenario(
        values = {
            'elec_in.V': f"cos({omega} * t)",
        }
    )
    circuit.run_drivers()

    df = driver.recorder.export_data()
    # print("", df.drop(['Section', 'Status', 'Error code'], axis=1), sep="\n")

    for i, row in df.iterrows():
        I = row['elec_in.I']
        R = row['Requiv']
        context = f"row #{i}, I = {I}"
        if I > 1e-12:
            assert R == pytest.approx(100), context
        elif I < -1e-12:
            assert R == pytest.approx(500), context
    
    assert [record.time for record in driver.recorded_events] == pytest.approx(
        [(2 * k + 1) * 0.5 * numpy.pi / omega for k in range(2)]
    )
