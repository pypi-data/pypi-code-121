from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from respice.math.numerics import trap, trap_jac
from .TwoTerminalCurrentComponent import TwoTerminalCurrentComponent


@dataclass(eq=False)
class Motor(TwoTerminalCurrentComponent):
    r"""
    Describes a motor model according to following model:

    .. math::

        K_T i - T_L &= J \dot \omega + D \omega \\
        v &= i R + \dot i L + K_E \omega

    where :math:`i` denotes input current, :math:`v` terminal voltage and :math:`\omega` angular speed.

    The model supports an additional load torque :math:`T_L`, which can be an arbitrary function of time.

    R:
        Terminal resistance measured in Ohm (:math:`\Omega`).
    L:
        Internal inductance measured in Henry (:math:`H`).
    KT:
        Torque constant measured in :math:`Nm / A`.
    KE:
        Back-EMF constant measured in :math:`V \cdot rad / s`.
    J:
        Moment of inertia of rotor measured in :math:`kg \cdot m^2`.
    D:
        Damping constant due to viscous friction in :math:`Nm`.
    TL:
        A time-(only)-variate function specifying a load-torque depending on time. By default 0.
    state_voltage:
        The initial voltage of the motor. By default 0.
    state_current:
        The initial current of the motor. By default 0.
    state_angular_frequency:
        The initial angular frequency of the motor axis. By default 0.
    """

    R: float
    L: float
    KT: float
    KE: float
    J: float
    D: float
    TL: Callable[[float], float] = lambda t: 0
    state_voltage: float = field(default=0.0, repr=False)
    state_current: float = field(default=0.0, repr=False)
    state_angular_frequency: float = field(default=0.0, repr=False)

    def _get_state_space_model(self, t: float, v: float):
        A = np.array([
            [-self.R / self.L, -self.KE / self.L],
            [self.KT / self.J, -self.D / self.J],
        ])

        b = np.array([
            v / self.L,
            -self.TL(t) / self.J,
        ])

        return A, b

    def _get_state_space_model_jacobian(self, t: float, v: float):
        dA = np.zeros((1, 2, 2))
        db = np.array([
            [1 / self.L],
            [0],
        ])
        return dA, db

    def _calculate_next_state(self, v: float, t1: float, t2: float):
        x1 = np.array([self.state_current, self.state_angular_frequency])

        A1, b1 = self._get_state_space_model(t1, self.state_voltage)
        A2, b2 = self._get_state_space_model(t2, v)

        return trap(x1, t2 - t1, A1, b1, A2, b2)

    def get_current(self, v: float, t1: float, t2: float) -> float:
        i, _ = self._calculate_next_state(v, t1, t2)
        return i

    def get_jacobian(self, v: float, t1: float, t2: float) -> float:
        A2, b2 = self._get_state_space_model(t2, v)
        dA, db = self._get_state_space_model_jacobian(t2, v)

        return trap_jac(
            self._calculate_next_state(v, t1, t2),
            t2 - t1,
            A2,
            dA,
            db,
        )[0, 0]

    def update(self, v_i: np.ndarray, t1: float, t2: float):
        v = v_i[0]
        i, omega = self._calculate_next_state(v, t1, t2)

        self.state_current = i
        self.state_voltage = v
        self.state_angular_frequency = omega

    @property
    def state(self):
        return self.state_current, self.state_voltage, self.state_angular_frequency

    @state.setter
    def state(self, val):
        self.state_current, self.state_voltage, self.state_angular_frequency = val
