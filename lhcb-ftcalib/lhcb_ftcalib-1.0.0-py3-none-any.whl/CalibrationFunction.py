import numpy as np
from abc import ABC, abstractmethod


class CalibrationFunction(ABC):
    r"""
    Calibration function abstract base type. All calibration classes should inherit from this type.
    Calibration functions receive calibration parameters in the following order

    params :math:`= (p^+_0,\cdots, p^+_n, p^-_0,\cdots,p^-_n)`
    """

    def __init__(self, npar, link):
        self.npar = npar
        self.link = link
        self.basis = None  # Function specific basis representation

    def __eq__(self, other):
        equal = True
        equal &= self.npar == other.npar
        equal &= self.link == other.link
        equal &= len(self.basis) == len(other.basis)
        if equal:
            for b in range(len(self.basis)):
                equal &= np.array_equal(self.basis[b], other.basis[b])
        return equal

    @abstractmethod
    def print_basis(self):
        """ Pretty printer for the calibration basis """
        print("no basis")

    @abstractmethod
    def init_basis(self, eta, weight=None):
        """ Initializer for the calibration function basis.
            Must be called before a calibration function is evaluated

            :param eta: Mistags
            :type eta: numpy.ndarray
            :param weight: Event weights
            :type weight: numpy.ndarray
        """
        pass

    @abstractmethod
    def eval(self, params, eta, dec):
        """ Evaluate the calibration function

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        print("no basis")

    @abstractmethod
    def eval_averaged(self, params, eta):
        r""" Evaluate the calibration function and ignore differences of
            flavour specific calibrations

            :param params: Mean calibration function parameters :math:`[p_0,\cdots,p_n]`
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        pass

    @abstractmethod
    def eval_plotting(self, params, eta, dec):
        """ Compute the combined lineshape of the flavour specific calibration components (for plotting).

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibrated mistags
            :return type: numpy.ndarray
        """
        pass

    @abstractmethod
    def derivative(self, partial, params, eta, dec):
        """ Evaluate the partial derivative w.r.t. one of the calibration parameters.

            :param partial: :math:`n`-th calibration parameter
            :type partial: int
            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibration function partial derivative
            :return type: numpy.ndarray
        """
        pass

    @abstractmethod
    def derivative_averaged(self, partial, params, eta):
        """ Evaluate the partial derivative w.r.t. one of the average calibration parameters.

            :param partial: :math:`n`-th calibration parameter
            :type partial: int
            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: Calibration function partial derivative
            :return type: numpy.ndarray
        """
        pass

    def gradient(self, params, eta, dec):
        """ Evaluate the calibration function gradient w.r.t. to the set of calibration parameters

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: List of all calibration function partial derivatives
            :return type: numpy.ndarray
        """
        return np.array([self.derivative(i, params, eta, dec) for i in range(self.npar * 2)])

    def gradient_averaged(self, params, eta):
        """ Evaluate the calibration function gradient w.r.t. to the set of averaged calibration parameters

            :param params: Calibration function parameters
            :type params: list
            :param eta: Mistags
            :type eta: numpy.ndarray
            :param dec: Tagging decisions
            :type dec: numpy.ndarray
            :return: List of all calibration function partial derivatives
            :return type: numpy.ndarray
        """
        return np.array([self.derivative_averaged(i, params, eta) for i in range(self.npar)])
