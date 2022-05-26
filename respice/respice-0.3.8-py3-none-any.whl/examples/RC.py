from respice.analysis import Circuit
from respice.components import Resistance, Capacitance


class RC(Circuit):
    """
    Example RC circuit (without current supply).
    """

    def __init__(self, r: float, c: float, initial_v: float = 1.0):
        """
        :param r:
            Resistance value (measured in Ohm).
        :param c:
            Capacitance value (measured in Farad).
        :param initial_v:
            The initial voltage of the capacitance (measured in Volts).
        """
        super().__init__()

        self.R = Resistance(r)
        self.R.name = 'R'
        self.C = Capacitance(c, initial_v)
        self.C.name = 'C'

        self.add(self.R, 0, 1)
        self.add(self.C, 1, 0)
