from nbodysim.integrator import Integrator
from nbodysim import nmath as nm

class Euler(Integrator):
    """
    Class defining a non-symplectic integrator, via the Euler Method
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

    def integration_step(self, t, delta):
        """
        Integration step for the Euler method.
        v_t = v_{t-1} + a_{t-1}*Δt
        x_t = x_{t-1} + v_{t-1}*Δt
        :param t: the step at which the calculation is made
        """

        acc_t = self.nbody.get_acceleration()

        new_velocities = self.velocity_orbit[:, t-1, :] + delta * acc_t
        new_positions = self.position_orbit[:,t-1,:] + delta * self.velocity_orbit[:,t-1,:]

        return new_positions, new_velocities, None


