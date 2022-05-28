import json
import pandas as pd
import numpy as np

from .Tagger import TaggerBase
from .PolynomialCalibration import PolynomialCalibration
from .NSplineCalibration import NSplineCalibration
from .BSplineCalibration import BSplineCalibration
from .combination import combine_taggers, _correlation
from .printing import (info, section_header, printbold, raise_warning, print_tagger_correlation,
                       print_tagger_performances, print_tagger_statistics, warning,
                       raise_error)
from .plotting import draw_inputcalibration_curve
from . import link_functions as links
from .CalParameters import CalParameters


class TargetTaggerCollection:
    r""" class TaggerCollection List type for grouping target taggers. Supports iteration.

        :param \*taggers: Tagger instance
        :type \*taggers: Tagger
    """

    def __init__(self, *taggers):
        self._taggers = [*taggers]
        self._index = -1
        if self._taggers:
            self._validate()

    def __str__(self):
        return "TargetTaggerCollection [" + ','.join([t.name for t in self._taggers]) + "]"

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self._taggers)

    def __iter__(self):
        return self

    def __next__(self):
        if self._index == len(self._taggers) - 1:
            self._index = -1
            raise StopIteration
        self._index += 1
        return self._taggers[self._index]

    def __getitem__(self, t):
        if isinstance(t, (int, slice)):
            return self._taggers[t]
        else:
            for j, tagger in enumerate(self._taggers):
                if tagger.name == t:
                    return self._taggers[j]
        raise IndexError

    def _validate(self):
        assert all([isinstance(tagger, TargetTagger) for tagger in self._taggers]), "TaggerCollection can only store TargetTagger instances"
        assert len(set([tagger.name for tagger in self._taggers])) == len(self._taggers), "Tagger names are not unique"

    def add_taggers(self, *tagger):
        """ Adds tagger(s) to the TargetTaggerCollection instance """
        self._taggers += [*tagger]
        self._validate()

    def create_tagger(self, *args, **kwargs):
        """ Adds a TargetTagger instance to the TargetTaggerCollection instance
            by passing the arguments to the TargetTagger() constructor.
        """
        self._taggers.append(TargetTagger(*args, **kwargs))
        self._validate()

    def load_calibrations(self, filename, tagger_mapping=None, style="flavour"):
        """ Load calibrations from a file

            :param filename: Filename of the calibration file
            :type filename: str
            :param tagger_mapping: Optional dictionary of a mapping of tagger names in this list vs corresponding entry names in the calibration file. By default, the same naming is assumed (!)
            :type tagger_mapping: dict
            :param style: Which parameter style to use
            :type style: str ("delta", "flavour")
        """
        if tagger_mapping is None:
            tagger_mapping = { t.name : t.name for t in self._taggers }
        else:
            assert len(tagger_mapping) == len(self)

        for tagger in self._taggers:
            info(f"Loading {tagger_mapping[tagger.name]} calibrations for {tagger.name}")
            tagger.load(filename, tagger_mapping[tagger.name], style)

    def apply(self, quiet=False, ignore_delta=True):
        """ Applies the previously loaded calibrations to a taggers

            :param quiet: Whether to print performance summary tables
            :type quiet: bool
        """

        if not quiet:
            print_tagger_correlation(self, "fire",       selected=True)
            print_tagger_correlation(self, "dec",        selected=True)
            print_tagger_correlation(self, "dec_weight", selected=True)
            print_tagger_statistics(self, calibrated=False, selected=False)
            print_tagger_performances(self, calibrated=False, selected=False)

        for tagger in self._taggers:
            info(f"Applying calibration for {tagger.name}")
            tagger.apply(ignore_delta)

        if not quiet:
            print_tagger_statistics(self, calibrated=True, selected=False)
            print_tagger_performances(self, calibrated=True, selected=False)

    def get_dataframe(self, calibrated=True):
        """ Returns a dataframe of the calibrated mistags and tagging decisions

            :return: Calibrated data
            :return type: pandas.DataFrame
        """
        df = pd.DataFrame()
        if calibrated:
            for tagger in self._taggers:
                assert tagger.is_calibrated()
                df[tagger.name + "_CDEC"]  = np.array(tagger.stats._full_data.cdec.copy(), dtype=np.int32)
                df[tagger.name + "_OMEGA"] = np.array(tagger.stats._full_data.omega.copy())
        else:
            for tagger in self._taggers:
                df[tagger.name + "_DEC"] = np.array(tagger.stats._full_data.dec.copy(), dtype=np.int32)
                df[tagger.name + "_ETA"] = np.array(tagger.stats._full_data.eta.copy())

        return df

    def plot_inputcalibration_curves(self, **kwargs):
        r""" Plots input calibration curves of a set of taggers, like the EPM
            does when a calibration is applied.  Plots the loaded calbration curve
            (uncertainties are loaded but ignored while applying the calibration)
            and the targeted mistag data.

            :param \**kwargs: Arguments to pass to draw_inputcalibration_curve
        """
        for tagger in self._taggers:
            print("Info: pdf file", draw_inputcalibration_curve(tagger, **kwargs), "has been created")

    def combine_taggers(self, name, calibrated):
        """ Computes the combination of multiple taggers
            and returns it in the form of a new Tagger object

            :param name: Name of the tagger combination
            :type name: str
            :param calibrated: Whether to use calibrated tagger data for combination (recommended)
            :type calibrated: bool
            :return: Tagger combination
            :rtype: Tagger
        """
        taggernames = [t.name for t in self._taggers]
        section_header("TAGGER COMBINATION")
        printbold("Combining taggers " + " ".join(taggernames) + f" into {name}")
        printbold("Checking compatibility")

        # Sanity checks
        raise_warning(name not in taggernames, "Name of combination is already in use")
        if calibrated:
            indeed_calibrated = [t.is_calibrated() is not None for t in self._taggers]  # Do not forbid combination of calibrated and uncalibrated taggers
            raise_warning(all(indeed_calibrated), "None, or not all provided taggers have been calibrated")

        printbold("Running combination...")
        # Collect data
        if calibrated:
            decs   = np.array([ np.array(tagger.cstats.all_dec if cal else tagger.stats.all_dec) for tagger, cal in zip(self._taggers, indeed_calibrated) ]).T
            omegas = np.array([ np.array(tagger.cstats.all_eta if cal else tagger.stats.all_eta) for tagger, cal in zip(self._taggers, indeed_calibrated) ]).T
        else:
            decs   = np.array([ np.array(tagger.stats.all_dec) for tagger in self._taggers ]).T
            omegas = np.array([ np.array(tagger.stats.all_eta) for tagger in self._taggers ]).T

        d_combined, omega_combined = combine_taggers(decs, omegas)

        # Construct Tagger object
        combination = TargetTagger(name     = name,
                                   eta_data = omega_combined,
                                   dec_data = d_combined,
                                   weight = self._taggers[0].stats.all_weights)
        printbold(f"New tagger combination {combination.name} has been created")
        return combination

    def correlation(self, corrtype="dec_weight", selected=True, calibrated=False):
        r""" Compute different kinds of tagger correlations. The data points are weighted by their per-event weight.
            The weighted correlation coefficient between two observables X and Y with weights W is defined as

            :math:`\displaystyle\mathrm{corr}(X, Y, W) = \frac{\mathrm{cov}(X, Y, W)}{\mathrm{cov}(X, X, W) \mathrm{cov}(Y, Y, W)}`

            whereby

            :math:`\mathrm{cov}(X, Y, W) = \displaystyle\sum_i w_i (x_i-\overline{X}) (y_i - \overline{Y}) / \sum_iw_i`

            and

            :math:`\overline{X} = \sum_i w_ix_i / \sum_i w_i`

            One can choose between 4 different correlation types:

            * corrtype="fire" : Correlation of tagger decisions irrespective of decision sign
                :math:`x_i=|d_{x,i}|, y_i=|d_{y,i}|` and :math:`W` is the event weight

            * corrtype="dec" : Correlation of tagger decisions taking sign of decision into account
                :math:`x_i=d_{x,i}, y_i=d_{y,i}` and :math:`W` is the event weight

            * corrtype="dec_weight" : Correlation of tagger decisions taking sign of decision into account and weighted by tagging dilution
                :math:`x_i=d_{x,i}(1-2\eta_{x,i}), y_i=d_{y,i}(1-2\eta_{y,i}),` and :math:`W` is the event weight

            * corrtype="both_fire" : Correlation of tagger decisions if both have fired taking sign of decision into account
                :math:`x_i=d_{x,i}, y_i=d_{y,i}` and :math:`W` is the event weight

            :param corr: Type of correlation
            :type corr: string
            :param selected: Whether to only use events in selection
            :type selected: bool
            :param calibrated: Whether to use calibrated statistics. (Only relevant for correlation types with mistag, not part of automatic print-out)
            :type calibrated: bool
            :return: Correlation matrix
            :rtype: pandas.DataFrame
        """

        return _correlation(self, corrtype=corrtype, selected=selected, calibrated=calibrated)


class TargetTagger(TaggerBase):
    """ A variation of the tagger object which loads a calibration
        from file and applies it to some data. Like the "Tagger",
        it contains two sets of TaggingData (BasicTaggingData) for
        before and after the calibration.

        Note: Specifying the B id, calibration mode,
        decay time and its uncertainty as well as the resolution model is
        optional and only needed in order to estimate the raw mistag if this performance
        number is needed and if it makes sense to compute it from the B ids in the tuple.

        :param name: Name of this target tagger. Ideally, try to use the same as for the calibrated tagger
        :type name: str
        :param eta: Targeted mistag data
        :type eta: list
        :param dec: Targeted tagging decisions
        :type dec: list
        :param ID: B meson IDs (Not needed)
        :type ID: list
        :param mode: Calibration mode (Not needed)
        :type mode: str
        :param tau: Decay times in ps (Not needed)
        :type tau: list
        :param tauerr: Decay time uncertainties in ps (Not needed)
        :type tauerr: list
        :param weight: Weight variable (needed for tagging statistics information)
        :type weight: list
    """

    class __LoadedMinimizer:
        def __init__(self):
            self.values = None
            self.errors = None
            self.covariance = None
            self.accurate = True  # At this point we trust the calibration file

    def __init__(self, name, eta_data, dec_data, B_ID=None, mode=None, tau_ps=None, tauerr_ps=None, weight=None, resolution_model=None):
        raise_error(not (mode in ("Bd", "Bs") and tau_ps is None), f"If a calibration mode \"{mode}\" is specified for a target tagger, the decay time needs to be provided")
        raise_error(not (mode is None and any([a is not None for a in [tau_ps, tauerr_ps, resolution_model]])),
                    "If decay time related info is provided for a target tagger, the mode must be set to Bd or Bs")

        if tau_ps is not None and B_ID is None:
            warning("Need B ID to interpret decay time info. Ignoring tau branch.")

        super().__init__(name              = name,
                         eta_data          = eta_data,
                         dec_data          = dec_data,
                         B_ID              = B_ID if B_ID is not None else np.ones(len(eta_data)),
                         mode              = "Bu" if mode is None else mode,
                         tau_ps            = tau_ps if B_ID is not None else None,
                         tauerr_ps         = tauerr_ps if B_ID is not None else None,
                         weight            = weight,
                         selection         = np.ones(len(eta_data), dtype=bool),  # All events are selected when taggers are applied
                         resolution_model  = resolution_model,
                         analytic_gradient = False)
        self.info        = None
        self.func        = None  # TaggerBase sets func by default
        self._calibrated = False
        self._has_b_id   = B_ID is not None
        self.minimizer   = self.__LoadedMinimizer()

    def apply(self, ignore_delta=True):
        """ Apply the previously loaded calibration to this tagger

            :param ignore_delta: If false, delta calibration parameters will be used when calibration is applied
            :type ignore_delta: bool
        """
        assert self._calibrated
        self.stats._compute_calibrated_statistics(self.func, self.minimizer)
        self._calibrated = True

    def get_dataframe(self, calibrated=True):
        """ Returns a dataframe of the calibrated mistags and tagging decisions

            :return: dataframe with calibrated tagging decisions and mistags
            :return type: pandas.DataFrame
            :raises: AssertionError if calibration has not yet been applied
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

    def load(self, filename, tagger_name, style="flavour"):
        """ Load a calibration entry from a calibration file

            :param filename: Filename of the calibration file
            :type filename: str
            :param tagger_name: Entry name of the calibration data you would like to load
            :type tagger_name: str
            :param style: Which parameter style to use
            :type style: str ("delta", "flavour")
        """
        with open(filename, "r") as F:
            calib = json.loads(F.read())

        # Reconstruct calibration function
        assert tagger_name in calib, "Tagger " + tagger_name + " not contained in calibration file"
        self.info = calib[tagger_name]

        assert style in ["flavour", "delta"], "Calibrations in " + style + "style not supported. Please use 'flavour' or 'delta' style."

        if "PolynomialCalibration" in self.info:
            fun_info = self.info["PolynomialCalibration"]
            self.func = PolynomialCalibration(int(fun_info["degree"]), get_link_by_name(fun_info["link"]))
            basis = self.info["PolynomialCalibration"]["basis"]
            basis = [np.array(vec) for vec in basis]
            self.func.set_basis(basis)
        elif "NSplineCalibration" in self.info:
            fun_info = self.info["NSplineCalibration"]
            self.func = NSplineCalibration(int(fun_info["degree"]) - 2, get_link_by_name(fun_info["link"]))
            basis = self.info["NSplineCalibration"]["basis"]
            basis = [np.array(vec) for vec in basis]
            self.func.set_basis(basis=fun_info["basis"], nodes=fun_info["nodes"])
        elif "BSplineCalibration" in self.info:
            fun_info = self.info["BSplineCalibration"]
            self.func = BSplineCalibration(int(fun_info["degree"]), get_link_by_name(fun_info["link"]))
            self.func.set_basis(fun_info["nodes"])
        else:
            raise RuntimeError("Unknown calibration function")

        self.stats.params = CalParameters(npar=self.func.npar)
        params = np.array(self.info["calibration"][style + "_style"]["params"])

        noms_loaded   = [float(v) for v in params[:, 1]]
        cov_loaded = self.info["calibration"][style + "_style"]["cov"]
        cov_loaded = np.array([float(e) for row in cov_loaded for e in row]).reshape((2 * self.func.npar, 2 * self.func.npar))

        if style == "delta":
            self.stats.params.set_calibration_delta(noms_loaded, cov_loaded)
        elif style == "flavour":
            self.stats.params.set_calibration_flavour(noms_loaded, cov_loaded)

        self.stats.avg_eta = float(self.info["calibration"]["avg_eta"])  # Always use avg_eta from calibrations
        self.minimizer.values = self.stats.params.params_flavour
        self.minimizer.errors = self.stats.params.errors_flavour
        self.minimizer.covariance = self.stats.params.covariance_flavour

        self.DeltaM     = self.info["osc"]["DeltaM"]
        self.DeltaGamma = self.info["osc"]["DeltaGamma"]
        self.Aprod      = self.info["osc"]["Aprod"]

        self._calibrated = True


def get_link_by_name(link):
    return {
        "mistag"   : links.mistag,
        "logit"    : links.logit,
        "rlogit"   : links.rlogit,
        "probit"   : links.probit,
        "rprobit"  : links.rprobit,
        "cauchit"  : links.cauchit,
        "rcauchit" : links.rcauchit,
    }[link]
