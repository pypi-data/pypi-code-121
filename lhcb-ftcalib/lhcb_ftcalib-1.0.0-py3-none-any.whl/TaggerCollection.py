import numpy as np
import pandas as pd

from .plotting import draw_calibration_curve
from .combination import combine_taggers, _correlation
from .printing import (print_tagger_correlation, print_tagger_performances, print_tagger_statistics,
                       blue_header, section_header, printbold, raise_warning,
                       raise_error, print_calibration_parameters)
from .Tagger import Tagger


class TaggerCollection:
    r""" class TaggerCollection
        Lists type for grouping taggers.

        :param \*taggers: Tagger instance
        :type \*taggers: Tagger
    """

    def __init__(self, *taggers):
        self._taggers = [*taggers]
        self._index = -1
        if self._taggers:
            self._validate()

    def __str__(self):
        return "TaggerCollection [" + ','.join([t.name for t in self._taggers]) + "]"

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
        # Taggers cannot come from different datasets and their names mist be unique
        assert all([isinstance(tagger, Tagger) for tagger in self._taggers]), "TaggerCollection can only store Tagger instances"
        assert len(set([tagger.name for tagger in self._taggers])) == len(self._taggers), "Tagger names are not unique"
        assert len(set([tagger.stats.N for tagger in self._taggers])) == 1, "Data of Taggers have inconsistent lenghts"

    def set_calibration(self, func):
        """ Sets a calibration function for all taggers

            :param func: Calibration function
            :type func: CalibrationFunction
        """
        for tagger in self._taggers:
            tagger.set_calibration(func)

    def add_taggers(self, *tagger):
        """ Adds tagger(s) to the TagCollection instance """
        self._taggers += [*tagger]
        self._validate()

    def create_tagger(self, *args, **kwargs):
        """ Adds a tagger to the TaggerCollection instance
            by passing the arguments to the Tagger() constructor.
        """
        self._taggers.append(Tagger(*args, **kwargs))
        self._validate()

    def calibrate(self, corr=True, stats=True, perf=True, params=True, basis=True, quiet=False):
        """ Loops over taggers, calibrates taggers and prints tagging information
            both before and after the calibrations and prints a summary of warning at the end.

            :param corr: If false, correlation coefficients are not printed
            :type corr: bool
            :param stats: If false, tagged event statistics are not printed
            :type stats: bool
            :param perf: If false, tagging performances are not printed
            :type perf: bool
            :param params: If false, tagging result is not printed
            :type params: bool
            :param basis: If false, does not print basis representation
            :type basis: bool
            :param quiet: If True all outputs except warnings are silenced
            :type quiet: bool
        """
        # Sanity checks
        raise_warning(len(set([t.name for t in self._taggers])) == len(self._taggers), "ERROR: Tagger names not unique")

        if quiet:
            corr = False
            stats = False
            perf = False
            params = False
            basis = False

        if corr:
            print_tagger_correlation(self, "fire",       selected=True)
            print_tagger_correlation(self, "dec",        selected=True)
            print_tagger_correlation(self, "dec_weight", selected=True)
            print_tagger_correlation(self, "both_fire", selected=True)  # expensive
        if stats:
            print_tagger_statistics(self, calibrated=False)
        if perf:
            print_tagger_performances(self, calibrated=False)

        for tagger in self._taggers:
            if basis:
                printbold(f"Basis representation for {tagger.name}")
                tagger.func.print_basis()

        if not quiet:
            blue_header("Running calibrations")
        warnings = {}
        for tagger in self._taggers:
            warnings[tagger.name] = tagger.calibrate()

        if params:
            print_calibration_parameters(self)
        if stats:
            print_tagger_statistics(self, calibrated=True)
        if perf:
            print_tagger_performances(self, calibrated=True)

        # Print warning summary
        print("\n\033[33m\033[1m ■■■ Warning summary ■■■\033[0m")
        for tagname, warning in warnings.items():
            if len(warning) > 0:
                print(f"\033[34m{tagname} Tagger\033[0m")
                for warn in warning:
                    print(warn)

    def get_dataframe(self, calibrated=True):
        """ Returns a dataframe of the calibrated mistags and tagging decisions

            :param calibrated: If true, calibrated decisions and mistags are written
            :type calibrated: bool

            :return: Calibrated data
            :return type: pandas.DataFrame
        """
        df = pd.DataFrame()
        if calibrated:
            for tagger in self._taggers:
                assert tagger.is_calibrated()
                df[tagger.name + "_CDEC"]  = np.array(tagger.stats._full_data.cdec.copy(), dtype=np.int32)
                df[tagger.name + "_OMEGA"] = np.array(tagger.stats._full_data.omega.copy())
        else:  # Only makes sense if user writes an uncalibrated combination to file
            for tagger in self._taggers:
                df[tagger.name + "_DEC"] = np.array(tagger.stats._full_data.dec.copy(), dtype=np.int32)
                df[tagger.name + "_ETA"] = np.array(tagger.stats._full_data.eta.copy())
        return df

    def plot_calibration_curves(self, **kwargs):
        r""" Plots calibration curves of a set of taggers

            :param \**kwargs: Arguments to pass to draw_calibration_curve
        """
        section_header("Plotting")
        for tagger in self._taggers:
            print("Info: pdf file", draw_calibration_curve(tagger, **kwargs), "has been created")

    def combine_taggers(self, name, calibrated, next_selection=None):
        """ Computes the combination of multiple taggers
            and returns it in the form of a new Tagger object

            :param name: Name of the tagger combination
            :type name: str
            :param calibrated: Whether to use calibrated tagger data for combination (recommended)
            :type calibrated: bool
            :param next_selection: Event selection to use for calibrating combination (default: No selection)
            :type next_selection: list
            :return: Tagger combination
            :rtype: Tagger
        """
        taggernames = [t.name for t in self._taggers]
        section_header("TAGGER COMBINATION")
        printbold("Combining taggers " + " ".join(taggernames) + f" into {name}")
        printbold("Checking compatibility")

        # Sanity checks
        for tagger in self._taggers:
            raise_error(tagger.stats._full_data.decay_flav.equals(self._taggers[0].stats._full_data.decay_flav), "Taggers must refer to the same pp collision, otherwise combination is nonsense")
        raise_warning(name not in taggernames, "Name of combination is already in use")
        if calibrated:
            indeed_calibrated = [t.is_calibrated() for t in self._taggers]  # Do not forbid combination of calibrated and uncalibrated taggers
            raise_warning(all(indeed_calibrated), "None, or not all provided taggers have been calibrated")

        printbold("Running combination...")
        # Collect data
        if calibrated:
            decs   = np.array([ np.array(tagger.stats._full_data.cdec  if cal else tagger.stats._full_data.dec) for tagger, cal in zip(self._taggers, indeed_calibrated) ]).T
            omegas = np.array([ np.array(tagger.stats._full_data.omega if cal else tagger.stats._full_data.eta) for tagger, cal in zip(self._taggers, indeed_calibrated) ]).T
        else:
            decs   = np.array([ np.array(tagger.stats._full_data.dec) for tagger in self._taggers ]).T
            omegas = np.array([ np.array(tagger.stats._full_data.eta) for tagger in self._taggers ]).T

        d_combined, omega_combined = combine_taggers(decs, omegas)

        # Find decay time info
        tau = None
        tauerr = None

        for tagger in self._taggers:
            if tagger.stats._has_tau:
                tau = tagger.stats._full_data.tau
            if tagger.stats._has_tauerr:
                tauerr = tagger.stats._full_data.tau_err

        # Construct Tagger object
        combination = Tagger(name      = name,
                             eta_data  = omega_combined,
                             dec_data  = d_combined,
                             B_ID      = self._taggers[0].stats._full_data.decay_flav,
                             mode      = self._taggers[0].mode,
                             tau_ps    = tau,
                             tauerr_ps = tauerr,
                             weight    = self._taggers[0].stats._full_data.weight,
                             selection = next_selection)
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

    def destroy(self):
        """ Frees most of the allocated memory.
            Collection is ill-defined afterwards.
        """
        for tagger in self._taggers:
            tagger.destroy()
