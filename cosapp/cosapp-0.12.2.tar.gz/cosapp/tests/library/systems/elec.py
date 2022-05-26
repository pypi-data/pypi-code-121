"""Systems from tutorials used in regression tests"""

from cosapp.systems import System
from cosapp.ports import Port
from typing import List


class Voltage(Port):
    def setup(self):
        self.add_variable('V', unit='V')

        
class Current(Port):
    def setup(self):
        self.add_variable('I', unit='A')


class Dipole(System):
    """Simple dipole model of the kind: {V_in, V_out} -> I"""
    def setup(self):
        self.add_input(Voltage, "V_in")
        self.add_input(Voltage, "V_out")
        self.add_output(Current, "I")
        self.add_outward("deltaV", 0.0)

    def compute(self):
        self.deltaV = self.V_in.V - self.V_out.V
        self.I.I = 0.0


class Resistor(Dipole):
    """Linear resistor model: {V_in, V_out} -> I"""
    def setup(self, R=100):
        super().setup()
        self.add_inward("R", float(R), unit="ohm", desc="Resistance")

    def compute(self):
        super().compute()
        self.I.I = self.deltaV / self.R


class Node(System):
    """Electric node model from Kirchhoff laws"""

    def setup(self, n_in=1, n_out=1):
        self.add_property('n_in', int(n_in))
        self.add_property('n_out', int(n_out))

        if min(self.n_in, self.n_out) < 1:
            raise ValueError("Node needs at least one incoming and one outgoing current")

        self.add_property('incoming', [
            self.add_input(Current, f"I_in{i}")
            for i in range(self.n_in)
        ])
        self.add_property('outgoing', [
            self.add_input(Current, f"I_out{i}")
            for i in range(self.n_out)
        ])
        
        self.add_inward('V', unit='V')
        self.add_outward('sum_I_in', 0., desc='Total incoming current')
        self.add_outward('sum_I_out', 0., desc='Total outgoing current')
        
        # Off-design problem
        self.add_unknown('V').add_equation(
            'sum_I_in == sum_I_out',
            name='Current balance',
        )
        
        self.add_inward('V_design', 10.)

    def compute(self):
        self.sum_I_in = sum(current.I for current in self.incoming)
        self.sum_I_out = sum(current.I for current in self.outgoing)

    @classmethod
    def make(cls, parent, name, incoming: List[Dipole], outgoing: List[Dipole], pulling=None) -> "Node":
        """Factory method making appropriate connections with parent system"""
        node = cls(name, n_in=max(len(incoming), 1), n_out=max(len(outgoing), 1))
        parent.add_child(node, pulling=pulling)
        
        for i, dipole in enumerate(incoming):
            parent.connect(dipole.V_out, node.inwards, "V")
            parent.connect(dipole.I, node[f"I_in{i}"])
        
        for i, dipole in enumerate(outgoing):
            parent.connect(dipole.V_in, node.inwards, "V")
            parent.connect(dipole.I, node[f"I_out{i}"])

        return node


class Source(System):
    def setup(self, I=0.1):
        self.add_inward('I', I, unit='A')
        self.add_output(Current, 'I_out', {'I': I})
    
    def compute(self):
        self.I_out.I = self.I


class Ground(System):
    def setup(self, V=0.0):
        self.add_inward('V', V, unit='V')
        self.add_output(Voltage, 'V_out', {'V': V})
    
    def compute(self):
        self.V_out.V = self.V
