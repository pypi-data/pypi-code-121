import numpy as np
import scipy
from scipy import integrate


class TemporalSIModel:
    """
    Susceptible-Infected deterministic model of disease spread for a temporal network with dynamic adjacency matrices.
    """
    def __init__(self, params, y_init, end_time, temporal_network, approximate=False):
        """

        :param params: dictionary. MUST include 'beta' value.
        :param y_init: NumPy 1d array of initial infection probabilities, normalized to sum to 1. Ex. [1/3, 1/3, 1/3]
        :param end_time: float or int of last snapshots end time
        :param temporal_network: TemporalNetwork object
        :param approximate: False (default). If True, ODE will ignore saturation and infect beyond size of network.
        """
        self.params = params
        self.y_init = y_init
        self.y_current = self.y_init
        self.result = []
        self.end_time = end_time
        self.start_time = 0
        self.approximate = approximate
        self.networks = temporal_network.get_time_network_map()  # dictionary of switch times to adjacency matrices
        self.switch_times = sorted(list(self.networks.keys()))
        self.current_switch_time_index = 0
        self.current_switch_time = self.switch_times[0]
        self.N = len(y_init)

    def odes_si(self, y, t):
        try:
            beta = self.params['beta']
        except KeyError:
            return Exception("Must include params argument with 'beta' key and associated value between [0,1].")
        except TypeError:
            return Exception("params argument must be a dict with key 'beta' and value")
        derivatives = np.zeros(len(y))
        A = self.networks[self.current_switch_time]
        for i in range(self.N):
            derivatives[i] = (1 - y[i]) * beta * np.sum(A[i] @ y)
            if self.approximate:
                derivatives[i] = (1) * beta * np.sum(A[i] @ y)
        return derivatives

    def solve_model(self, total_time_steps=300, return_p_vecs = False, custom_t_inc = None):
        """

        :param total_time_steps: int, time steps to solve, higher number means higher resolution
        :param return_p_vecs: bool, will return all node infectious probability states for all time steps
        :param custom_t_inc: custom time increments to solve for. Default None.
        :return:
        """
        time_series_result = []
        node_probabilities = [[] for n in range(self.N)]
        steps_per_interval = max(int(np.round(total_time_steps/len(self.switch_times), 0)),20)
        p_states = [self.y_current]
        for switchtime in self.switch_times:
            self.current_switch_time = switchtime
            if custom_t_inc is None:
                solve_for_timesteps = np.linspace(self.start_time, switchtime, steps_per_interval)
            else:
                solve_for_timesteps = np.arange(self.start_time, switchtime, custom_t_inc)
            switchtime_solution = scipy.integrate.odeint(self.odes_si,
                                                         y0=self.y_current,
                                                         t=solve_for_timesteps)
            time_series_result.extend(solve_for_timesteps)
            for i in range(self.N):
                node_probabilities[i].extend(list(switchtime_solution[:, i]))
            new_initial_p_vec = [switchtime_solution[:,i][-1] for i in range(self.N)]
            self.start_time = switchtime
            self.y_current = new_initial_p_vec
            p_states.append(self.y_current)
        if return_p_vecs:
            return time_series_result, np.array(node_probabilities), p_states
        return time_series_result, np.array(node_probabilities)

    def smooth_solution(self, solution, resolution=200):
        """
        The point of this method is to standardize the results from the ODE solution into standard
        time increments so that different time series can be compared to one another at the same time points.

        :param solution: return value tuple from TemporalSIModel.solve_model()
        :param resolution: int, 200 (default) length of solution time series to be returned.
        :return: tuple, time series vector and infected number of nodes per time step
        """
        time_vector = solution[0]
        infected_vector = np.sum(solution[1], axis=0)
        total_time = np.sum(np.diff(np.array(list(self.networks.keys())))) + list(self.networks.keys())[0]
        digitized = np.digitize(np.array(time_vector), np.linspace(0, total_time, resolution))
        time_stamp_means = [np.array(time_vector)[digitized == i].mean() for i in
                     range(1, len(np.linspace(0, total_time, resolution)))]
        infected_timeseries_means = [np.array(infected_vector)[digitized == i].mean() for i in
                         range(1, len(np.linspace(0, total_time, resolution)))]
        # interpolate the nans with backfill:
        for i, d in enumerate(time_stamp_means):
            if np.isnan(d):
                time_stamp_means[i] = time_stamp_means[i - 1]
        for i, d in enumerate(infected_timeseries_means):
            if np.isnan(d):
                infected_timeseries_means[i] = infected_timeseries_means[i - 1]
        return time_stamp_means, infected_timeseries_means