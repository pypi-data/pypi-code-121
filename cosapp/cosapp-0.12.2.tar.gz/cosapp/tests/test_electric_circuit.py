"""Regression test from tutorials"""
import pytest

from cosapp.tests.library.systems import Resistor, Node, Source, Ground
from cosapp.systems import System
from cosapp.drivers import NonLinearSolver, RunSingleCase
from cosapp.recorders import DataFrameRecorder


class Circuit(System):
    """Simple resistor circuit

    --->--+--[R2]--+
          |        |
        [R1]     [R3]
          |        |
          +--------+---/ Ground
    """
    def setup(self):
        ground = self.add_child(Ground('ground', V=0.0))
        R1 = self.add_child(Resistor('R1', R=1000))
        R2 = self.add_child(Resistor('R2', R=500))
        R3 = self.add_child(Resistor('R3', R=250))
        
        Node.make(self, 'n1',
            incoming = [],
            outgoing = [R1, R2],
            pulling = {'I_in0': 'source'},
        )
        Node.make(self, 'n2',
            incoming = [R2],
            outgoing = [R3],
        )
        self.connect(ground.V_out, R1.V_out)
        self.connect(ground.V_out, R3.V_out)
        
        self.exec_order = ('ground', 'n1', 'n2', 'R1', 'R2', 'R3')

        # design methods
        self.add_inward('V1_design', 0.0)
        self.add_inward('V2_design', 0.0)
        self.add_design_method('R1').add_unknown('R1.R').add_equation('n1.V == V1_design')
        self.add_design_method('R2').add_unknown('R2.R').add_equation('n2.V == V2_design')


class LegacyCircuit(System):
    """Legacy circuit model, as originally given in tutorials"""
    def setup(self):
        n1 = self.add_child(Node('n1', n_in=1, n_out=2), pulling={'I_in0': 'I_in'})
        n2 = self.add_child(Node('n2'))
        
        R1 = self.add_child(Resistor('R1', R=1000), pulling={'V_out': 'Vg'})
        R2 = self.add_child(Resistor('R2', R=500))
        R3 = self.add_child(Resistor('R3', R=250), pulling={'V_out': 'Vg'})
        
        self.connect(R1.V_in, n1.inwards, 'V')
        self.connect(R2.V_in, n1.inwards, 'V')
        self.connect(R1.I, n1.I_out0)
        self.connect(R2.I, n1.I_out1)
        
        self.connect(R2.V_out, n2.inwards, 'V')
        self.connect(R3.V_in, n2.inwards, 'V')
        self.connect(R2.I, n2.I_in0)
        self.connect(R3.I, n2.I_out0)
        
        self.exec_order = ('n1', 'n2', 'R1', 'R2', 'R3')

        # design methods
        self.add_inward('V1_design', 0.0)
        self.add_inward('V2_design', 0.0)
        self.add_design_method('R1').add_unknown('R1.R').add_equation('n1.V == V1_design')
        self.add_design_method('R2').add_unknown('R2.R').add_equation('n2.V == V2_design')


@pytest.fixture
def model():
    """Legacy model, as originally given in tutorials

     +----+--[R2]--+
     |    |        |
    (S)  [R1]     [R3]
     |    |        |
     +----+--------+---/ Ground
    """
    model = System('model')
    model.add_child(Source('source', I=0.1))
    model.add_child(Ground('ground', V=0.0))
    model.add_child(LegacyCircuit('circuit'))

    model.connect(model.source.I_out, model.circuit.I_in)
    model.connect(model.ground.V_out, model.circuit.Vg)

    model.circuit.R1.R = 1e3
    model.circuit.R2.R = 0.5e3
    model.circuit.R3.R = 0.25e3

    return model


@pytest.fixture
def circuit():
    circuit = Circuit('circuit')
    circuit.R1.R = 1e3
    circuit.R2.R = 0.5e3
    circuit.R3.R = 0.25e3
    circuit.source.I = 0.1
    return circuit


def test_LegacyCircuit_solve(model):
    model.add_driver(NonLinearSolver('solver'))
    model.run_drivers()

    assert model.source.I == 0.1
    assert model.circuit.R1.R == 1000
    assert model.circuit.R2.R == 500
    assert model.circuit.R3.R == 250
    assert model.circuit.R1.I.I == pytest.approx(0.04285714286)
    assert model.circuit.R2.I.I == pytest.approx(0.05714285714)
    assert model.circuit.R3.I.I == pytest.approx(0.05714285715)
    assert model.circuit.n1.V == pytest.approx(42.85714286)
    assert model.circuit.n2.V == pytest.approx(14.28571429)


def test_LegacyCircuit_design_multipoint(model):
    solver = model.add_driver(NonLinearSolver('solver', tol=1e-9))
    model.run_drivers()  # balance system

    # Add driver to set boundary conditions on point 1
    point1 = solver.add_child(RunSingleCase('point1'))
    point1.design.extend(model.circuit.design_methods['R2'])

    model.circuit.V2_design = 8.
    point1.set_values({
        'source.I': 0.08, 
        'ground.V': 0,
    })

    # Same as previous for a second point
    point2 = solver.add_child(RunSingleCase('point2')) 
    point2.design.extend(model.circuit.design_methods['R1'])

    model.circuit.V1_design = 50.
    point2.set_values({
        'source.I': 0.15,
        'ground.V': 0,
    })

    solver.add_recorder(
        DataFrameRecorder(includes=['*n?.V', '*R', 'source.I'], excludes='*R3*')
    )

    model.run_drivers()

    data = solver.recorder.export_data()
    assert data.at[0, 'circuit.n2.V'] == pytest.approx(8)
    assert data.at[1, 'circuit.n1.V'] == pytest.approx(50)
    assert model.circuit.R1.R == pytest.approx(5000 / 9)
    assert model.circuit.R2.R == pytest.approx(5250 / 9)


def test_Circuit_solve(circuit):
    circuit.add_driver(NonLinearSolver('solver'))
    circuit.run_drivers()

    assert circuit.source.I == 0.1
    assert circuit.R1.R == 1000
    assert circuit.R2.R == 500
    assert circuit.R3.R == 250
    assert circuit.R1.I.I == pytest.approx(0.04285714286)
    assert circuit.R2.I.I == pytest.approx(0.05714285714)
    assert circuit.R3.I.I == pytest.approx(0.05714285715)
    assert circuit.n1.V == pytest.approx(42.85714286)
    assert circuit.n2.V == pytest.approx(14.28571429)


def test_Circuit_design_multipoint(circuit):
    solver = circuit.add_driver(NonLinearSolver('solver', tol=1e-9))
    circuit.run_drivers()  # balance system

    # Add driver to set boundary conditions on point 1
    point1 = solver.add_child(RunSingleCase('point1'))
    point1.design.extend(circuit.design_methods['R2'])

    circuit.V2_design = 8.
    point1.set_values({
        'source.I': 0.08, 
        'ground.V': 0,
    })

    # Same as previous for a second point
    point2 = solver.add_child(RunSingleCase('point2')) 
    point2.design.extend(circuit.design_methods['R1'])

    circuit.V1_design = 50.
    point2.set_values({
        'source.I': 0.15,
        'ground.V': 0,
    })

    solver.add_recorder(
        DataFrameRecorder(includes=['n?.V', '*R', 'source.I'], excludes='*R3*')
    )

    circuit.run_drivers()

    data = solver.recorder.export_data()
    assert data.at[0, 'n2.V'] == pytest.approx(8)
    assert data.at[1, 'n1.V'] == pytest.approx(50)
    assert circuit.R1.R == pytest.approx(5000 / 9)
    assert circuit.R2.R == pytest.approx(5250 / 9)
