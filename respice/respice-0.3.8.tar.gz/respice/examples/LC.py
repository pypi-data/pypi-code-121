from respice.analysis import Circuit
from respice.components import Capacitance, Inductance


class LC(Circuit):
    """
    Example ideal LC circuit.
    """

    def __init__(self, l: float, c: float, initial_v: float = 1.0, initial_i: float = 0.0):
        """
        :param l:
            The inductance value (measured in Henry).
        :param c:
            The capacitance value (measured in Farad).
        :param initial_v:
            The initial voltage of the capacitance (measured in Volts).
        :param initial_i:
            The initial current of the inductance (measured in Amperes).
        """
        super().__init__()

        self.L = Inductance(l, initial_i)
        self.L.name = 'L'
        self.C = Capacitance(c, initial_v)
        self.C.name = 'C'

        self.add(self.L, 0, 1)
        self.add(self.C, 1, 0)
