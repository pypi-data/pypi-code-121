""" Uncertain values.
"""
import itertools as it
import numpy as np
from numpy import inf
from scipy.stats import skew
import matplotlib.pyplot as plt


class UncertainValue:
    """ Uncertain values.

    Class used to define uncertain real numbers. Each uncertain number
    is described with a nominal value, upper and lower bounds as well as a
    probability distribution between these bounds. To keep track of the
    uncertainties, random samples are taking according to the defined
    probability distribution. Uncertainty propagation is calculted using
    Monte-Carlo methods.

    Attributes:
        nominal_value (float or int): Value you'd assign to your variable if no
            uncertainty would to be considered
        lower_bound (float or int): smallest possible value. Default value is
            nominal_value. If the uncertain number has no lower bound, set this
            variable to -inf.
        upper_bound (float or int): largest possible value. Default value is
            nominal value. If the uncertain number has no upper bound, set this
            variable to inf.
        prob_distribution (string): probability distribution type f the
            uncertainty. Possible input values are 'normal', 'discrete' and
            'uniform' (default value). Other ossible values are 'constant' (if
            the number is a fixed number with lower_bound = nominal_value =
            upper_bound) and 'custom' (results from doing calculations with
            other types of distribution).
        distribution_param (list): parameters needed to describe the given
            probability distribution type. For the 'normal' distribution type,
            the parameters are '[mean, standard deviation]'. For 'uniform', no
            parameters are needed. For a 'discrete' distribution, the
            parameters are either a list of possible values [val1, val2, ...]
            or a list of lists with possible values and the probability of each
            value [[val1, prob1], [val2, prob2], ...].
        n_samples (int): number of samples to be used for the calculation of
            the probability distribution. Default value is 100 000.
        samples (list or numpy.ndarray): List/array with samples.
    """

    def __init__(self, nominal_value, lower_bound=None, upper_bound=None,
                 prob_distribution='uniform', distribution_param=None,
                 n_samples=100000, samples=None):
        # # Assign values to self
        self.nominal_value = nominal_value
        self.n_samples = int(n_samples)
        self.distribution_param = distribution_param

        # Bounds definition according to input
        if lower_bound is None and upper_bound is None \
                and prob_distribution != 'discrete':
            self.lower_bound = nominal_value
            self.upper_bound = nominal_value
        elif lower_bound is None and upper_bound is None \
                and prob_distribution == 'discrete':
            if len(np.array(distribution_param[0]).shape) == 0:
                self.distribution_param = np.array([distribution_param]).T
            elif len(np.array(distribution_param[0]).shape) == 1:
                self.distribution_param = np.array(distribution_param)
            self.lower_bound = min(self.distribution_param[:, 0])
            self.upper_bound = max(self.distribution_param[:, 0])
        elif lower_bound is not None and upper_bound is not None:
            self.lower_bound = lower_bound
            self.upper_bound = upper_bound

        # Probability distribution
        # TODO: define definition- should a truncated normal function be
        #     defined as "normal", "custom" or "normal truncated"?.
        if (self.lower_bound == self.upper_bound
                and prob_distribution != 'discrete') or \
                prob_distribution == 'constant':
            self.prob_distribution = 'constant'
            self.n_samples = 1
        elif prob_distribution == 'normal' and lower_bound == -float('Inf') \
                and upper_bound == float('Inf'):
            self.prob_distribution = 'normal'
        elif prob_distribution == 'discrete':
            self.prob_distribution = 'discrete'
        elif prob_distribution == 'normal':
            self.prob_distribution = 'normal'
        elif prob_distribution == 'uniform':
            self.prob_distribution = 'uniform'
        elif prob_distribution == 'custom':
            self.prob_distribution = 'custom'
        else:
            raise ValueError("Probability distribution type not recognized")

        # Samples
        if samples is None:
            self.samples = self.__generate_samples(
                self.lower_bound, self.upper_bound,
                self.prob_distribution, distribution_param,
                self.n_samples)
        elif samples is not None:
            if isinstance(samples, (list, np.ndarray)):
                self.prob_distribution = 'custom'
                self.samples = samples
                self.n_samples = len(samples)
            else:
                raise ValueError('Wrong format of samples. They should be '
                                 + 'provided in a list or array.')

        # Compute statistical properties
        self.statistical_parameter()

        # # Check input data consistency
        if self.lower_bound > self.upper_bound:
            raise ValueError("Lower bound (" + str(self.lower_bound)
                             + ") is larger than upper bound ("
                             + str(self.upper_bound) + ".")

        if not self.lower_bound <= self.nominal_value <= self.upper_bound:
            raise ValueError("Nominal value (" + str(self.nominal_value)
                             + ") is not between bounds ("
                             + str(self.lower_bound) + ", "
                             + str(self.upper_bound) + ").")

    # # Redefine mathematical operations
    def __neg__(self):
        negative = UncertainValue(
            -self.nominal_value,
            -self.upper_bound,
            -self.lower_bound)
        negative.samples = -self.samples
        negative.statistical_parameter()
        return negative

    def __add__(self, other):
        if isinstance(other, (float, int)):
            other = UncertainValue(other)

        nominal_value = self.nominal_value + other.nominal_value
        lower_bound = self.lower_bound + other.lower_bound
        upper_bound = self.upper_bound + other.upper_bound
        result = UncertainValue(nominal_value, lower_bound, upper_bound,
                                'custom')
        result.samples = self.samples+other.samples
        result.statistical_parameter()
        return result

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, (float, int)):
            other = UncertainValue(other)

        nominal_value = self.nominal_value - other.nominal_value
        lower_bound = self.lower_bound - other.upper_bound
        upper_bound = self.upper_bound - other.lower_bound
        result = UncertainValue(nominal_value, lower_bound, upper_bound,
                                'custom')
        result.samples = self.samples-other.samples
        result.statistical_parameter()
        return result

    def __rsub__(self, other):
        return -self+other

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            other = UncertainValue(other)

        nominal_value = self.nominal_value*other.nominal_value
        bounds = [
            self.lower_bound*other.lower_bound,
            self.lower_bound*other.upper_bound,
            self.upper_bound*other.lower_bound,
            self.upper_bound*other.upper_bound
        ]
        lower_bound = min(bounds)
        upper_bound = max(bounds)
        result = UncertainValue(nominal_value, lower_bound, upper_bound,
                                'custom')
        result.samples = self.samples*other.samples
        result.statistical_parameter()
        return result

    def __rmul__(self, other):
        return self*other

    def __truediv__(self, other):
        if isinstance(other, (float, int)):
            other = UncertainValue(other)

        nominal_value = self.nominal_value/other.nominal_value
        bounds = [
            self.lower_bound/other.lower_bound,
            self.lower_bound/other.upper_bound,
            self.upper_bound/other.lower_bound,
            self.upper_bound/other.upper_bound
        ]

        lower_bound = min(bounds)
        upper_bound = max(bounds)
        if other.lower_bound < 0 < other.upper_bound:
            lower_bound = -inf
            upper_bound = inf

        prob_distribution = 'custom'
        result = UncertainValue(nominal_value, lower_bound, upper_bound,
                                prob_distribution)
        result.samples = self.samples/other.samples
        result.statistical_parameter()
        return result

    def __rtruediv__(self, other):
        if isinstance(other, (float, int)):
            other = UncertainValue(other)
        return other/self

    def __pow__(self, other):
        if isinstance(other, (float, int)):
            other = UncertainValue(other)

        nominal_value = self.nominal_value**other.nominal_value
        # Type check
        if self.lower_bound > 0 \
           or (other.lower_bound == 0 and other.upper_bound == 0):
            # Result equals 1
            bounds = [i[0]**i[1] for i in list(it.product(
                [self.lower_bound, self.upper_bound],
                [other.lower_bound, other.upper_bound]))]
            result = UncertainValue(nominal_value, None, None, 'custom')
            result.lower_bound = min(bounds)
            result.upper_bound = max(bounds)
            result.prob_distribution = 'custom'
        else:
            raise ValueError('Uncertain calculation of exponentiation with '
                             + 'negative basis not implemented')
        result.samples = self.samples**other.samples
        result.n_samples = len(result.samples)
        result.statistical_parameter()
        return result

    def __rpow__(self, other):
        if isinstance(other, (float, int)):
            other = UncertainValue(other)
        return other**self

    # Trigonometric functions
    def sin(self):
        """ Calculate the sine of the uncertain value.

        Function is used as well when calling numpy.sin().

        """
        # Nominal value
        nominal_value = np.sin(self.nominal_value)
        # Bounds
        bounds = [self.upper_bound, self.lower_bound]
        delta = self.upper_bound - self.lower_bound
        if 2 * np.pi <= delta:
            lower_bound = -1.
            upper_bound = 1.
        elif (self.upper_bound - np.pi / 2) % (2 * np.pi) <= delta:
            lower_bound = min(np.sin(bounds))
            upper_bound = 1.
        elif (self.upper_bound + np.pi / 2) % (2 * np.pi) <= delta:
            lower_bound = -1.
            upper_bound = max(np.sin(bounds))
        else:
            lower_bound = min(np.sin(bounds))
            upper_bound = max(np.sin(bounds))
        # Samples
        samples = np.sin(self.samples)
        # Results
        result = UncertainValue(nominal_value, lower_bound, upper_bound,
                                samples=samples)
        return result

    def cos(self):
        """ Calculate the cosine of the uncertain value.

        Function is used as well when calling numpy.cos().

        """
        # Nominal value
        nominal_value = np.cos(self.nominal_value)
        # Bounds
        bounds = [self.upper_bound, self.lower_bound]
        delta = self.upper_bound - self.lower_bound
        if 2 * np.pi <= delta:
            lower_bound = -1.
            upper_bound = 1.
        elif self.upper_bound % (2 * np.pi) <= delta:
            lower_bound = min(np.cos(bounds))
            upper_bound = 1.
        elif (self.upper_bound + np.pi) % (2 * np.pi) <= delta:
            lower_bound = -1.
            upper_bound = max(np.cos(bounds))
        else:
            lower_bound = min(np.cos(bounds))
            upper_bound = max(np.cos(bounds))
        # Samples
        samples = np.cos(self.samples)
        # Results
        result = UncertainValue(nominal_value, lower_bound, upper_bound,
                                samples=samples)
        return result

    def tan(self):
        """ Calculate the tangens of the uncertain value.

        Function is used as well when calling numpy.tan().

        """
        # Nominal value
        nominal_value = np.tan(self.nominal_value)
        # Bounds
        bounds = [self.upper_bound, self.lower_bound]
        delta = self.upper_bound - self.lower_bound
        if np.pi <= delta:
            lower_bound = -np.inf
            upper_bound = np.inf
        elif (self.upper_bound - np.pi / 2) % np.pi <= delta:
            lower_bound = -np.inf
            upper_bound = np.inf
        else:
            lower_bound = min(np.tan(bounds))
            upper_bound = max(np.tan(bounds))
        # Samples
        samples = np.tan(self.samples)
        # Results
        result = UncertainValue(nominal_value, lower_bound, upper_bound,
                                samples=samples)
        return result

    # TODO: Redefine comparision ?

    # Other functions
    def describe(self):
        """ This function is used to display the information describing an
            uncertain value: nominal value, lower bound, upper bound,
            probability distribution type and number of samples.
        """
        desc_string = \
            "\nThis variable is an uncertain value. "\
            + "It has the following properties:" \
            + "\n" \
            + "\n\t- Nominal value: " + str(self.nominal_value) \
            + "\n" \
            + "\n\t- Mean: " + str(self.mean)\
            + "\n\t- Median: " + str(self.median)\
            + "\n\t- Variance: " + str(self.var)\
            + "\n\t- Standard deviation: " + str(self.std)\
            + "\n\t- Skewness: " + str(self.skewness)\
            + "\n" \
            + "\n\t- Lower bound: " + str(self.lower_bound)\
            + "\n\t- Percentile 5: " + str(self.p05)\
            + "\n\t- Q1: " + str(self.q1)\
            + "\n\t- Q3: " + str(self.q3)\
            + "\n\t- Percentile 95: " + str(self.p95)\
            + "\n\t- Upper bound: " + str(self.upper_bound)\
            + "\n" \
            + "\n\t- Probability distribution type: " \
            + str(self.prob_distribution) \
            + "\n\t- Number of samples: " + str(self.n_samples)\
            + "\n"
        return desc_string

    def plot_distribution(self, label=None, new_figure=False, title=None,
                          plot_type='pdf', alpha=1, density=True, save=False,
                          fname='dist.png'):
        """ Plot the (cumulative) probability distribution.

        Plots the probability distribution (PDF) or cumulative probability
        distribution (CDF) of an uncertain number.

        Args:
            label (string): String used to label the histogram. Default value
                is None (probability distribution is not labeled).
            new_figure (bool): If True, the value is plotted in a new window.
                Defaut value is False.
            title (string): Plot title. Default value is None.
            plot_type (string): Type of plot. Can be either 'pdf' (probability
                distribution, default value) or 'cdf' (cumulative distribution)
            alpha (int): TODO. Default value is 1.
            density (bool): TODO. Default value is True.
            save (bool): If True, the figure is saved as a file. Default value
                is False.
            fname (str): Name of the file in which the figure is saved. Default
                name is 'dist.png'.

        Raises:
            ValueError: With unknown plot type.

        """
        if new_figure or not plt.get_fignums():
            plt.figure()
            plt.xlabel('Value [-]')
            if plot_type == 'pdf':
                ylabel = 'Probability density [-]'
            elif plot_type == 'cdf':
                ylabel = 'Probability [-]'
            plt.ylabel(ylabel)
            plt.title(title)

        if plot_type == 'pdf':
            histtype = 'bar'
            cum = False
        elif plot_type == 'cdf':
            histtype = 'step'
            cum = True
        else:
            raise ValueError('Unknown plot type.')

        if label is None:
            plt.hist(self.samples, bins=100, density=density,
                     histtype=histtype, cumulative=cum, alpha=alpha)
        elif label is not None:
            plt.hist(self.samples, bins=100, density=density, label=label,
                     histtype=histtype, cumulative=cum, alpha=alpha)
            plt.legend()

        plt.show(block=False)

        if save:
            plt.savefig(fname)

    # Private methods
    def __generate_samples(self, lower_bound, upper_bound, prob_distribution,
                           distribution_param, n_samples):
        """ Generates the samples of the uncertain number
        """
        if prob_distribution == 'uniform':
            output_samples = np.random.uniform(lower_bound, upper_bound,
                                               n_samples)
        elif prob_distribution == 'constant':
            output_samples = np.array(lower_bound)
        elif prob_distribution == 'normal':
            mean = distribution_param[0]
            deviation = distribution_param[1]
            samples = []
            while len(samples) <= n_samples:
                new_samples = [x for x in
                               np.random.normal(mean, deviation, n_samples)
                               if lower_bound <= x <= upper_bound]
                samples = np.append(samples, new_samples)
            output_samples = samples[:n_samples]
        elif prob_distribution == 'discrete':
            distribution_param = np.array(distribution_param)
            if len(np.array(distribution_param[0]).shape) == 0:
                output_samples = np.random.choice(distribution_param,
                                                  n_samples)
            elif len(np.array(distribution_param[0]).shape) == 1:
                output_samples = np.random.choice(
                    distribution_param[:, 0],
                    n_samples,
                    p=distribution_param[:, 1])
            else:
                raise ValueError('Unknown parameters')
        elif prob_distribution == 'custom':
            if distribution_param is None:
                distribution_param = [0]
            output_samples = np.random.choice(distribution_param, n_samples)
        else:
            raise ValueError('Unknown distribution')
        return output_samples

    def statistical_parameter(self):
        """ Computes statistical parameters (mean, variance,...) of the
            uncertain number using the given samples.
        """
        self.mean = np.mean(self.samples)
        self.var = np.var(self.samples)
        self.std = np.std(self.samples)
        self.skewness = skew(self.samples)

        self.median = np.median(self.samples)
        self.q1 = np.percentile(self.samples, 25)
        self.q3 = np.percentile(self.samples, 75)
        self.p05 = np.percentile(self.samples, 5)
        self.p95 = np.percentile(self.samples, 95)

    def percentile(self, percentile):
        return np.percentile(self.samples, percentile)


# Functions to work with uncertain values
def probability_in_interval(uncertain_value, interval):
    """ Calculates the probability of an uncertain value to be in an interval.

    Args:
        uncertain_value (UncertainValue): Uncertain value for which the
            probability is calculated.
        interval (array): Interval U defined by a lower and upper bound
            [u_min, u_max].

    Returns:
        float: Probability.

    """
    samples = uncertain_value.samples
    lower_bound = interval[0]
    upper_bound = interval[1]
    return sum((lower_bound < samples) & (samples < upper_bound)) \
        / len(samples)


def from_data(data_list):
    """ Generates an UncertainValue object from a list with numbers.

    A normal distribution is assumed.

    Args:
        data_list (list or numpy.ndarray): List with real numbers.

    Returns:
        UncertainValue: Uncertain number with the same mean and standard
            deviation as the input data_list.
    """
    return UncertainValue(np.average(data_list), -np.inf, np.inf, 'normal',
                          [np.average(data_list), np.std(data_list)])
