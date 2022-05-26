from respice.analysis import Circuit
from respice.components import Resistance, Capacitance, Inductance


class RLC(Circuit):
    """
    Example RLC circuit (without current supply).
    """

    def __init__(self, r: float, l: float, c: float, initial_v: float = 1.0, initial_i: float = 0.0):
        """
        :param r:
            The resistance value (measured in Ohm).
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

        self.R = Resistance(r)
        self.R.name = 'R'
        self.L = Inductance(l, initial_i)
        self.L.name = 'L'
        self.C = Capacitance(c, initial_v)
        self.C.name = 'C'

        self.add(self.R, 0, 1)
        self.add(self.L, 1, 2)
        self.add(self.C, 2, 0)
