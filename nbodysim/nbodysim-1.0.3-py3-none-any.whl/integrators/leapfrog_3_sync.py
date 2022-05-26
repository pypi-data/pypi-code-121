import warnings

from nbodysim.integrator import Integrator
from nbodysim import nmath as nm

class Leapfrog2Int(Integrator):
    """
    Class defining an integrator via the Integer 3-Step Leapfrog 2-Step Method
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

        if adaptive:
            warnings.warn(f"Synchronised Leapfrog can't use adaptive timestep. "
                          f"Integrator will run with the constant delta provided ({delta})")
            adaptive = False

        # execute initialisation from superclass
        super().__init__(nbody, steps, delta, tolerance = tolerance, adaptive = adaptive, adaptive_constant= adaptive_constant, delta_lim= delta_lim, store_properties = store_properties)

        # save acceleration for next iteration.
        # Only require 1 expensive acceleration calculation per step
        self.acc_t = self.nbody.get_acceleration()

    def integration_step(self, t, delta):
        """
        Integration step for the Integer 3-Step Leapfrog method.
        x_t = x_{t-1} + v_{t-1}*Δt + 0.5*a_{t-1}*Δt^2
        v_t = v_{t-1} + 0.5*(a_t + a_{t-1}*Δt
        :param t: the step at which the calculation is made
        """

        # perform Integer 3-Step Leapfrog step
        new_positions = self.position_orbit[:, t - 1, :] \
                        + delta * self.velocity_orbit[:, t - 1, :] \
                        + 0.5 * self.acc_t * delta**2
        acc_tt = self.nbody.get_acceleration(positions = new_positions)
        new_velocities = self.velocity_orbit[:, t - 1, :] \
                         + 0.5 * (self.acc_t + acc_tt) * delta

        return new_positions, new_velocities, acc_tt
