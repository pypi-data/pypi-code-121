import numpy as np
import iminuit
import pandas as pd
from packaging import version
from copy import deepcopy

from .printing import raise_error, warning, info, printbold
from .PolynomialCalibration import PolynomialCalibration
from .TaggingData import TaggingData
from . import link_functions
from . import constants
from .CalParameters import CalParameters


class TaggerBase:
    r""" Purely virtual Tagger base class """

    def __init__(self, name, eta_data, dec_data, B_ID, mode, tau_ps=None, tauerr_ps=None,
                 weight=None, selection=None, resolution_model=None, analytic_gradient=False):
        # Consistency checks
        raise_error(len(eta_data) == len(dec_data) == len(B_ID), "Tagging data must have matching dimensions")

        if selection is None:
            selection = pd.Series(np.full(len(dec_data), True))

        # Variables needed for minimization
        self.name      = name  #: Name of tagger
        self.mode      = mode  #: Calibration mode (one of "Bd", "Bu", "Bs")
        self.minimizer = None  #: iminuit minimizer
        self.func      = PolynomialCalibration(npar=2, link=link_functions.mistag)  #: Calibration function
        self.stats     = TaggingData(eta_data  = eta_data,
                                     dec_data  = dec_data,
                                     ID        = B_ID,
                                     tau       = tau_ps,
                                     tauerr    = tauerr_ps,
                                     weights   = weight,
                                     selection = selection)  #: Tagger statistics
        self.func.init_basis(self.stats._tagdata.eta, weight=self.stats._tagdata.weight)
        self._analytic_gradient = analytic_gradient
        self.resolution_model = resolution_model  #: Decay time resolution model
        self._calibrated = False

        if self.mode == "Bd":
            self.DeltaM     = constants.DeltaM_d  #: B oscillation frequency :math:`\Delta m`
            self.DeltaGamma = constants.DeltaGamma_d  #: Decay width difference of B mass eigenstates :math:`\Delta\Gamma`
            self.Aprod      = 0  #: Production asymmetry (WIP)
        elif self.mode == "Bs":
            self.DeltaM     = constants.DeltaM_s
            self.DeltaGamma = constants.DeltaGamma_s
            self.Aprod      = 0
        elif self.mode == "Bu":
            self.DeltaM     = None
            self.DeltaGamma = None
            self.Aprod      = 0

        if self.mode in ("Bd", "Bs"):
            raise_error(tau_ps is not None, f"Decay time needed for mode {self.mode}")

            if self.resolution_model is not None:
                self.resolution_model.DM = self.DeltaM
                self.resolution_model.DG = self.DeltaGamma
                self.resolution_model.a  = 0

        # Flip production flavour is oscillation is likely
        self.stats._init_timeinfo(self.mode, self.DeltaM, self.DeltaGamma, self.resolution_model)
        self._has_b_id = True

    def destroy(self):
        """ Frees most of the allocated memory.
            Tagger is ill-defined afterwards.
        """
        del self.stats

    def is_calibrated(self):
        """ Returns true if calibration was performed

            :return type: bool
        """
        return self._calibrated

    def get_dataframe(self, calibrated=True):
        raise RuntimeError("This method needs to be provided in a derived class")

    def __eq__(self, other):
        # Needed for cached_property
        # Tagger names have to be unique
        return f"{self.name}{self._calibrated}{self.stats.Nt}" == f"{other.name}{other._calibrated}{other.stats.Nt}"

    def __hash__(self):
        # Needed for cached_property
        return hash(f"{self.name}{self._calibrated}{self.stats.Nt}")


class Tagger(TaggerBase):
    r""" LHCb Tagger object

    :param name: Custom name of the tagger
    :type name: str
    :param eta_data: Uncalibrated mistag data
    :type eta_data: list
    :param dec_data: Uncalibrated tagging decisions
    :type dec_data: list
    :param B_ID: B meson ids
    :type B_ID: list
    :param mode: Which mode to use for calibration (Bd, Bu, Bs)
    :type mode: str
    :param tau_ps: Decay time in picoseconds
    :type tau_ps: list
    :param tauerr_ps: Decay time uncertainty in picoseconds
    :type tauerr_ps: list
    :param weight: Per-Event weight
    :type weight: list
    :param selection: List of booleans, True = selected
    :type selection: list
    :param resolution_model: Decay time resolution model (default=Gaussian resolution)
    :type resolution_model: ResolutionModel
    :param analytic_gradient: Whether to use the analytical gradient implementation
    :type analytic_gradient: bool

    :raises ValueError: if input data lists are not of the same length
    :raises ValueError: if decay time data is not given and calibration mode is Bd or Bs
    """

    def __init__(self, name, eta_data, dec_data, B_ID, mode, tau_ps=None, tauerr_ps=None, weight=None, selection=None, resolution_model=None, analytic_gradient=False):
        raise_error(mode in ("Bu", "Bd", "Bs"), "Unknown calibration mode")
        super().__init__(name              = name,
                         eta_data          = eta_data,
                         dec_data          = dec_data,
                         B_ID              = B_ID,
                         mode              = mode,
                         tau_ps            = tau_ps,
                         tauerr_ps         = tauerr_ps,
                         weight            = weight,
                         selection         = selection,
                         resolution_model  = resolution_model,
                         analytic_gradient = analytic_gradient)
        self.__init_minimizer()

    def __init_minimizer(self):
        """ Initializes the flavour tagging likelihood and the minimizer """
        self.stats.params = CalParameters(self.func.npar)
        self.minimizer = iminuit.Minuit(self.__nll if self.mode == "Bu" else self.__nll_oscil,
                                        tuple(np.zeros(2 * self.func.npar)),
                                        name      = self.stats.params.names_flavour,
                                        grad      = self.__nll_oscil_grad if self._analytic_gradient else None)
        self.minimizer.errordef = iminuit.Minuit.LIKELIHOOD
        self.minimizer.print_level = 2
        self.minimizer.strategy = 0

    def set_calibration(self, func):
        """ Override default calibration function

            :param func: Calibration function
            :type func: CalibrationFunction
        """
        self.func = deepcopy(func)
        self.func.init_basis(self.stats._tagdata.eta, weight=self.stats._tagdata.weight)
        self.__init_minimizer()

    def calibrate(self):
        """ Runs configured flavour tagging calibration and adds calibrated mistag information to TaggingData """
        iminuit_version = iminuit.__version__
        printbold(20 * "-" + f" {self.name} calibration " + 20 * "-")
        info("iminuit version", iminuit_version)
        assert version.parse(iminuit_version) >= version.parse("2.3.0"), "iminuit >= 2.3.0 required"

        info("Starting minimization for", self.name)
        info(f"Selection keeps {self.stats.Ns}({self.stats.Nws} weighted) out of {self.stats.N}({self.stats.Nw}) events ({100*np.round(self.stats.Ns/self.stats.N, 4)}%)")
        self.minimizer.migrad()
        self.minimizer.hesse()
        if self.minimizer.valid:
            info("Minimum found")
            if self.minimizer.accurate:
                info("Covariance matrix accurate")
            else:
                warning("Covariance matrix -NOT- accurate")
        else:
            raise_error(False, "Minimization did not converge")

        warnings = self.stats._compute_calibrated_statistics(self.func, self.minimizer)

        self._calibrated = True
        print()

        return warnings

    def get_dataframe(self, calibrated=True):
        """ Returns a dataframe of the calibrated mistags and tagging decisions

            :param calibrated: Return dataframe of calibrated mistags and tag decisions
            :type calibrated: bool
            :raises: AssertionError if tagger has not been calibrated and calibrated=True
            :return: dataframe with mistag and tagging decision
            :return type: pandas.DataFrame
        """
        if calibrated:
            assert self._calibrated
            return pd.DataFrame({
                self.name + "_CDEC"  : np.array(self.stats._full_data.cdec.copy(), dtype=np.int32),
                self.name + "_OMEGA" : np.array(self.stats._full_data.omega.copy())
            })
        else:
            return pd.DataFrame({
                self.name + "_DEC" : np.array(self.stats._full_data.dec.copy(), dtype=np.int32),
                self.name + "_ETA" : np.array(self.stats._full_data.eta.copy())
            })

    def __nll(self, params):
        """ Likelihood for B+ modes without oscillation """
        data = self.stats._tagdata  # This is not a copy
        omega = self.func.eval(params, data.eta, data.prod_flav)

        log_likelihood  = np.sum(data.weight[data.correct_tags] * np.log(np.maximum(1 - omega[data.correct_tags], 1e-5)))  # Correct tags
        log_likelihood += np.sum(data.weight[data.wrong_tags]   * np.log(np.maximum(    omega[data.wrong_tags],   1e-5)))  # Incorrect tags

        return -log_likelihood

    def __nll_oscil(self, params):
        """ Likelihood for Bd and Bs modes with oscillation """
        data = self.stats._tagdata  # This is not a copy
        omega_given = self.func.eval(params, data.eta,      data.prod_flav)  # Omega based on predicted production flavour
        omega_oscil = self.func.eval(params, data.eta, -1 * data.prod_flav)  # Omega for opposite prod flavour

        correct_terms  = (1.0 - data.osc_dilution[data.correct_tags]) * (1.0 - omega_given[data.correct_tags])  # No mixing (tag == prod flav == decay flav)
        correct_terms +=        data.osc_dilution[data.correct_tags]  * omega_oscil[data.correct_tags]          # mixing    (tag == prod flav != decay flav)

        wrong_terms    = (1.0 - data.osc_dilution[data.wrong_tags]) * omega_given[data.wrong_tags]          # No mixing (tag != prod flav == decay flav)
        wrong_terms   +=        data.osc_dilution[data.wrong_tags]  * (1.0 - omega_oscil[data.wrong_tags])  # mixing    (tag != prod flav != decay flav)

        # log_likelihood  = np.sum(data.weight[data.correct_tags] * np.log(np.maximum(correct_terms, 1e-5)))
        # log_likelihood += np.sum(data.weight[data.wrong_tags] * np.log(np.maximum(wrong_terms, 1e-5)))

        log_likelihood  = np.sum(data.weight[data.correct_tags] * np.log(correct_terms))
        log_likelihood += np.sum(data.weight[data.wrong_tags] * np.log(wrong_terms))

        return -log_likelihood

    def __nll_oscil_grad(self, params):
        """ Likelihood gradient """
        data = self.stats._tagdata  # This is not a copy

        omega_given = self.func.eval(params, data.eta,      data.prod_flav)
        omega_oscil = self.func.eval(params, data.eta, -1 * data.prod_flav)
        correct_tags = data.correct_tags
        wrong_tags   = data.wrong_tags

        osc_dilution_correct = data.osc_dilution[correct_tags]
        osc_dilution_wrong   = data.osc_dilution[wrong_tags]

        denom_correct  = (1.0 - osc_dilution_correct) * (1.0 - omega_given[correct_tags])
        denom_correct +=        osc_dilution_correct  *        omega_oscil[correct_tags]
        denom_wrong    = (1.0 - osc_dilution_wrong)   *        omega_given[wrong_tags]
        denom_wrong   +=        osc_dilution_wrong    * (1.0 - omega_oscil[wrong_tags])

        grad = np.zeros(self.func.npar * 2)

        for i in range(self.func.npar * 2):
            correct_terms  =      osc_dilution_correct  * self.func.derivative(i, params, data.eta[correct_tags], -1 * data.decay_flav[correct_tags])
            correct_terms -= (1 - osc_dilution_correct) * self.func.derivative(i, params, data.eta[correct_tags],      data.decay_flav[correct_tags])

            wrong_terms  = (1 - osc_dilution_wrong) * self.func.derivative(i, params, data.eta[wrong_tags],      data.decay_flav[wrong_tags])
            wrong_terms -=      osc_dilution_wrong  * self.func.derivative(i, params, data.eta[wrong_tags], -1 * data.decay_flav[wrong_tags])

            grad[i]  = np.sum(data.weight[correct_tags] * correct_terms / denom_correct)
            grad[i] += np.sum(data.weight[wrong_tags] * wrong_terms / denom_wrong)

        return -grad
