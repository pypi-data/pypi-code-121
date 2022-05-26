import numpy as np

from nbodysim.integrators.integrator import Integrator
from nbodysim import nmath as nm

class Leapfrog3(Integrator):
    """
    Class defining an integrator via the 3-Step Leapfrog 2-Step Method
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

        # save acceleration for next iteration.
        # Only require 1 expensive acceleration calculation per step
        self.acc_t = self.nbody.get_acceleration()

    def integration_step(self, t, delta):
        """
        Integration step for the Integer 3-Step Leapfrog method.
        v_{t + 1/2} = v_t + 0.5*a_t*Δt
        x_{t + 1} = x_t + v_{t + 1/2}*Δt
        v_{t + 1} = v_{t + 1/2} + 0.5*a_{t + 1}*Δt
        :param t: the step at which the calculation is made
        :return the new positions and velocities, alongside the acceleration for step t+1
        """

        new_half_velocities = self.velocity_orbit[:, t - 1, :] + self.acc_t * delta * 0.5
        new_positions = self.position_orbit[:, t - 1, :] + new_half_velocities * delta
        acc_tt = self.nbody.get_acceleration(positions=new_positions)
        new_velocities = new_half_velocities + acc_tt * delta * 0.5

        return new_positions, new_velocities, acc_tt