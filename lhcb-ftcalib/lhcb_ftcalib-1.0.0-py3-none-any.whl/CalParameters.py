import numpy as np


class CalParameters:
    r""" Calibration parameter class

        This class computes different representations of a set of given calibration parameters :math:`\vec{\Theta}`:

        :param npar: Number of parameters per flavour
        :type npar: int
    """
    def __init__(self, npar):
        size = 2 * npar
        self.npar = npar
        self.params_flavour = np.zeros(size)  #: Nominal values (flavour representation)
        self.params_delta   = np.zeros(size)  #: Nominal values (delta representation)
        self.params_average = np.zeros(npar)  #: Nominal values (averaged representation)

        self.errors_flavour = np.zeros(size)  #: Parameter error (flavour representation)
        self.errors_delta   = np.zeros(size)  #: Parameter error (delta representation)
        self.errors_average = np.zeros(npar)  #: Parameter error (averaged representation)

        self.covariance_flavour = np.zeros((size, size))  #: Parameter covariance (flavour representation)
        self.covariance_delta   = np.zeros((size, size))  #: Parameter covariance (delta representation)
        self.covariance_average = np.zeros((npar, npar))  #: Parameter covariance (averaged representation)

        self._flavour2delta = np.block([[0.5*np.eye(npar), 0.5*np.eye(npar)], [np.eye(npar), -np.eye(npar)]])
        self._delta2flavour = np.block([[np.eye(npar), 0.5*np.eye(npar)], [np.eye(npar), -0.5*np.eye(npar)]])

        self.names_flavour = [f"p{i}+" for i in range(npar)] + [f"p{i}-" for i in range(npar)]  #: Parameter names (flavour representation)
        self.names_delta   = [f"p{i}" for i in range(npar)] + [f"Δp{i}" for i in range(npar)]   #: Parameter names (delta representation)
        self.names_average = [f"p{i}" for i in range(npar)]                                     #: Parameter names (averaged representation)

        self.names_latex_flavour = [fr"p_{i}^+" for i in range(npar)] + [fr"p_{i}^-" for i in range(npar)]    #: Parameter names latex (flavour representation)
        self.names_latex_delta   = [fr"p_{i}" for i in range(npar)] + [fr"\Delta p{i}" for i in range(npar)]  #: Parameter names latex (delta representation)
        self.names_latex_average = [fr"p_{i}" for i in range(npar)]                                           #: Parameter names latex (averaged representation)

    def set_calibration_flavour(self, params_flavour, covariance_flavour):
        """
        Initializes parameters for a given calibration in the flavour representation

        :param params_flavour: Nominal values
        :type params_flavour: numpy.ndarray
        :param covariance_flavour: Covariance matrix
        :type covariance_flavour: numpy.ndarray
        """
        self.params_flavour     = np.array(params_flavour)
        self.covariance_flavour = np.array(covariance_flavour)
        self.errors_flavour     = np.sqrt(np.diag(self.covariance_flavour))

        self.params_delta     = self._flavour2delta @ self.params_flavour
        self.covariance_delta = self._flavour2delta @ self.covariance_flavour @ self._flavour2delta.T
        self.errors_delta     = np.sqrt(np.diag(self.covariance_delta))

        self.params_average     = self.params_delta[:self.npar]
        self.covariance_average = self.covariance_delta[:self.npar, :self.npar]
        self.errors_average     = np.sqrt(np.diag(self.covariance_average))

    def set_calibration_delta(self, params_delta, covariance_delta):
        """ Initializes parameters for a given calibration in the delta representation

        :param params_flavour: Nominal values
        :type params_flavour: numpy.ndarray
        :param covariance_flavour: Covariance matrix
        :type covariance_flavour: numpy.ndarray
        """
        self.params_delta     = np.array(params_delta)
        self.covariance_delta = np.array(covariance_delta)
        self.errors_delta     = np.sqrt(np.diag(self.covariance_delta))

        self.params_flavour     = self._delta2flavour @ self.params_delta
        self.covariance_flavour = self._delta2flavour @ self.covariance_delta @ self._delta2flavour.T
        self.errors_flavour     = np.sqrt(np.diag(self.covariance_flavour))

        self.params_average     = self.params_delta[:self.npar]
        self.covariance_average = self.covariance_delta[:self.npar, :self.npar]
        self.errors_average     = np.sqrt(np.diag(self.covariance_average))

    def __len__(self):
        return self.npar
