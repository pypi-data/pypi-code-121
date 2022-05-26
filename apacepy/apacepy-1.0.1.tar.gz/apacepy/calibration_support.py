from math import sqrt

from scipy.stats import binom, norm

LNL_CALCULATED = 'LnL CALC'   # lnl calculated.
NO_SIM_RATIOS = 'NO SIM RATIOS'    # no simulation ratios provided.
NO_OBS_RATIOS = 'NO OBS RATIOS'    # no observed ratios provided.
NUM_SIM_RATIOS_LESS_THAN_OBS_RATIOS = 'N SIM < N OBS'   # number of simulation ratios are less than observed ratios.
LNL_INF = 'LnL -INF'  # lnl is -inf
NO_LNL_CALCULATED = 'LnL NOT CALC'   # lnl could not be calculated.


class FeasibleConditions:
    """ to determine if time-series of an epidemic outcomes falls within a feasible range. """

    def __init__(self, feasible_min=None, feasible_max=None, min_threshold_to_hit=None, period=None):
        """
        :param period: (tuple (t_min, t_max)) the period where the feasible conditions should be checked
        """
        self.feasibleMin = feasible_min
        self.feasibleMax = feasible_max
        self.minThresholdToHit = min_threshold_to_hit
        self.period = period

        self.ifMinThresholdHasReached = True
        if min_threshold_to_hit is not None:
            self.ifMinThresholdHasReached = False

    def check_if_acceptable(self, value, time):

        if value is None:
            return True

        # if feasible conditions should be checked only during the specified period
        if self.period is not None:

            if time is not None:
                # if time has passed the upper bound the minimum value is not yet reached, return False
                if time > self.period[1] and not self.ifMinThresholdHasReached:
                    return False
                elif not (self.period[0] <= time <= self.period[1]):
                    return True

            else: # if time is not recorded yet
                return True

        if self.minThresholdToHit is not None:
            if value >= self.minThresholdToHit:
                self.ifMinThresholdHasReached = True

        if self.feasibleMin is not None:
            if value < self.feasibleMin:
                return False

        if self.feasibleMax is not None:
            if value > self.feasibleMax:
                return False

        return True


def get_lnl_of_a_time_series(observed_ratios, sim_ratios, observed_ns=None, observed_vars=None, sim_ns=None):
    """
    :param observed_ratios: (list) of observed ratios
    :param sim_ratios: (list) of simulated ratios
    :param observed_ns: (list) of sizes of surveillance (denominators of the observed ratios)
    :param observed_vars: (list) of observed variances
    :param sim_ns: (list) of denominators from the simulated ratios
    :return: (mean lnl, explanation)
            mean log likelihood of observed ratios if simulation ratios represent reality
            (lnl_1 + lnl_2 + ... + lnl_N) / N, where N is the number of likelihoods that were calculated.

    assumptions:
        1. Either observed_ns, observed_vars, or sim_ns should be provided.
        2. If observed_vars is provided, it will be used to calculate likelihood using normal distribution,
            if observed_ns or sim_ns is provided, it will be used to calculate likelihoods
            using binomial distribution.
        3. If len(sim_ratios) < len(observed_ratios), it returns -inf

    """

    assert observed_ns is not None or observed_vars is not None or sim_ns is not None, \
        'Either observed_ns, observed_vars, or sim_ns should be provided.'

    if len(sim_ratios) == 0:
        return float('-inf'), NO_SIM_RATIOS
    elif len(observed_ratios) == 0:
        return float('-inf'), NO_OBS_RATIOS
    elif len(sim_ratios) < len(observed_ratios):
        return float('-inf'), NUM_SIM_RATIOS_LESS_THAN_OBS_RATIOS

    # how many likelihoods to calculate
    n = min(len(observed_ratios), len(sim_ratios))
    lnl = 0
    n_eff = 0  # number of likelihoods that were calculated
    for i in range(n):

        obs_ratio = observed_ratios[i]
        sim_ratio = sim_ratios[i]

        if obs_ratio is None or sim_ratio is None:
            continue
        else:
            # if likelihood is calculated using normal distribution
            if observed_vars is not None:
                lnl += norm.logpdf(x=obs_ratio, loc=sim_ratio, scale=observed_vars[i])
                n_eff += 1

            # if likelihood is calculated using binomial distribution
            elif observed_ns is not None or sim_ns is not None:
                if observed_ns is not None:
                    size = observed_ns[i]
                else:
                    size = sim_ns[i]

                lnl += binom.logpmf(k=int(obs_ratio*size), n=size, p=sim_ratio, loc=0)
                n_eff += 1

            else:
                raise ValueError('Either observed_ns, observed_vars, or sim_ns should be provided.')

    if n_eff == 0:
        return float('-inf'), NO_LNL_CALCULATED
    elif lnl == float('-inf'):
        return lnl, LNL_INF
    else:
        return lnl/n_eff, LNL_CALCULATED


def get_survey_size(mean, l, u, multiplier=1, alpha=0.05, interval_type='c'):
    """ calculates the survey size based on mean, lower bound, and upper bound
    :param mean:
    :param l:
    :param u:
    :param multiplier:
    :param alpha:
    :param interval_type: what the interval (l, u) specify:
        'c' for confidence interval and 'p' for percentile interval
    """
    if mean is None:
        return None

    mean *= multiplier
    l *= multiplier
    u *= multiplier

    if mean < 0 or mean > 1:
        raise ValueError('Mean should be between 0 and 1.')

    # z
    z = norm.ppf(1 - alpha / 2)

    if interval_type == 'c':
        # variance
        var = mean*(1-mean)
        # half-width
        hw = (u - l) / 2
        # n
        return int(var * pow(z / hw, 2))

    elif interval_type == 'p':
        # approximating the st dev
        st_dev = (u-l) / (2 * z)
        # n
        return int(sqrt(mean*(1-mean))/st_dev)
    else:
        raise ValueError('Incorrect value for interval_type.')




