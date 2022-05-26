import numpy as np

from nbodysim.integrator import Integrator
from nbodysim.integrator.euler_cromer import EulerCromer
from nbodysim import nmath as nm

class Leapfrog2(Integrator):
    """
    Class defining an integrator via the 2-Step Leapfrog Method
    """
    def __init__(self, nbody, steps, delta, tolerance = 1e-6, adaptive = False, adaptive_constant = 1, delta_lim =10 ** -5, store_properties = False):
        """
        :param nbody: NBody instance which we integrate
        :param steps: the number of steps to integrate for
        :param delta: timestep to use for the integrator. Smaller timesteps lead to more accurate orbits.
        :param tolerance: allowed absolute error for determining conservation of calculated quantities
        :param adaptive: if True, the Integrator will use an adaptive timestep (instead of a fixed one)
        :param adaptive_constant: constant used when calculating adaptive timestep. Smaller adaptive_constant leads to more accurate orbits.
        """

        # execute initialisation from superclass
        super().__init__(nbody, steps, delta, tolerance = tolerance, adaptive = adaptive, adaptive_constant= adaptive_constant, delta_lim = delta_lim, store_properties = store_properties)

        # execute mini Euler-Cromer to accurately calculate the velocity at half timestep
        half_steps = 10e2
        half_delta = self.delta/(2*half_steps) # will use half_steps steps, so calculate the delta accordingly

        half_integrator = EulerCromer(self.nbody, half_steps, half_delta, self.tolerance)

        half_integrator.get_orbits()

        # initialise half velocity orbit
        self.velocity_orbit[:,0,:] = self.nbody.velocities

    def integration_step(self, t, delta):
        """
        Integration step for the 2-Step Leapfrog method.
        v_{1/2} = v_0 + a_0*Δt
        v_{t + 1/2} = v_{t - 1/2} + a_{t-1}*Δt
        x_t = x_{t-1} + v_{t + 1/2}*Δt
        :param t: the step at which the calculation is made
        """

        acc_t = self.nbody.get_acceleration()

        new_velocities = self.velocity_orbit[:, t - 1, :] + delta * acc_t
        new_positions = self.position_orbit[:, t - 1, :] + delta * new_velocities

        return new_positions, new_velocities, None
