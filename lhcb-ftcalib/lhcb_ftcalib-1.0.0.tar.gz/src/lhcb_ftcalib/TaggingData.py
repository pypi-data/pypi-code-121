import numpy as np
import pandas as pd
import iminuit
import functools

from .printing import raise_error, raise_warning
from .resolution_model import mixing_asymmetry


class FTCWarning:
    def __init__(self, warntype, msg):
        self.warntype = warntype
        self.msg = msg

    def __str__(self):
        return f"\033[33m\033[1m[{self.warntype}]\033[0m {self.msg}"


class TaggingData:
    r"""
    TaggingData
    Type for computing and keeping track of tagging data and performance

    :param eta_data: Uncalibrated mistags
    :type eta_data: list
    :param dec_data: Uncalibrated tagging decisions
    :type dec_data: list
    :param ID: B meson particle IDs
    :type ID: list
    :param tau: Decay time in picoseconds
    :type tau: list
    :param tauerr: Decay time uncertainty in picoseconds
    :type tauerr: list
    :param weights: Per-event weights
    :type weights: list
    """

    def __init__(self, eta_data, dec_data, ID, tau, tauerr, weights, selection):
        def get_absid(ID):
            ids = np.unique(np.abs(ID))
            ids = list(ids[ids != 0])
            raise_error(len(ids) > 0, f"There are no nonzero particle IDs in the ID branch {ids}")
            raise_error(len(ids) == 1, f"There are too many particle IDs in the ID branch: {ids}")
            raise_warning(ids[0] in (511, 521, 531), f"Particle ID {ids[0]} does not belong to a Bu, Bd or Bs meson")
            return ids[0]

        self._absID = get_absid(np.array(ID))
        self._full_data = pd.DataFrame({
            "eta" : eta_data,
            "dec" : dec_data,
            "decay_flav" : ID // self._absID,
            "selected"   : selection }
        )
        self._full_data.decay_flav = self._full_data.decay_flav.astype(np.int32)
        if tau is not None:
            self._full_data["tau"] = tau
            self._has_tau = True
        else:
            self._has_tau = False

        if tauerr is not None:
            self._full_data["tau_err"] = tauerr
            self._has_tauerr = True
        else:
            self._has_tauerr = False

        if weights is None:
            self._full_data.eval("weight = 1", inplace=True)
        else:
            self._full_data["weight"] = weights

        self._full_data.eval("""overflow   = eta > 0.5
                                underflow  = eta < 0
                                tagged     = (dec != 0)
                                tagged_sel = tagged & selected
                                prod_flav  = decay_flav""", inplace=True)

        # Initialize tagging data subset
        self._tagdata = self._full_data[self._full_data.tagged_sel].copy()  # Copy needed, otherwise view
        self._tagdata.reset_index(inplace=True, drop=False)

        self._tagdata.eval("""correct_tags = (dec == prod_flav)
                              wrong_tags   = ~correct_tags""", inplace=True)

        self._is_calibrated = False

    def is_calibrated(self):
        """ Returns True if calibrated statistics are available """
        return self._is_calibrated

    @functools.cached_property
    def N(self):
        """ Total number of events """
        return len(self._full_data)

    @functools.cached_property
    def Ns(self):
        """ Number of selected events """
        return self._full_data.selected.sum()

    @functools.cached_property
    def Nt(self):
        r""" Number of tagged events :math:`N_t = N_\mathrm{tagged} - N_\mathrm{overflow}`.
            Events with mistag > 0.5 are overflow events and are not tagged by convention.
        """
        return self._full_data.tagged.sum() - (self._full_data.eta > 0.5).sum()

    @functools.cached_property
    def Nts(self):
        """ Number of tagged events in selection without overflow """
        return len(self._tagdata) - self._tagdata.overflow.sum()

    @functools.cached_property
    def Nw(self):
        """ Sum of all event weights """
        return np.sum(self._full_data.weight)

    @functools.cached_property
    def Neff(self):
        r""" Effective number of events
            :math:`N_\mathrm{eff}=(\sum_i w_i)^2 / \sum_i w_i^2`
        """
        return self.Nw**2 / np.sum(self._full_data.weight**2)

    @functools.cached_property
    def Nwt(self):
        """ Sum of all event weights of tagged events without overflow event weights """
        return self._full_data.weight[self._full_data.tagged].sum() - self._full_data.weight[self._full_data.overflow].sum()

    @functools.cached_property
    def Nws(self):
        """ Sum of all event weights of selected events """
        return np.sum(self._full_data.weight[self._full_data.selected])

    @functools.cached_property
    def Neffs(self):
        r""" Effective number of events in selection
            :math:`(\sum_i w_i)^2 / \sum_i w_i^2`
        """
        return self.Nws**2 / np.sum(self._full_data.weight[self._full_data.selected]**2)

    @functools.cached_property
    def Nwts(self):
        """ Sum of all event weights of tagged events in selection """
        return np.sum(self._tagdata.weight)

    @functools.cached_property
    def Noverflow(self):
        """ Number of events with raw mistag > 0.5 """
        return self._tagdata.overflow.sum()

    @functools.cached_property
    def cal_Noverflow(self):
        """ Number of events with raw mistag > 0.5 """
        return self._tagdata.cal_overflow.sum()

    @functools.cached_property
    def cal_Nt(self):
        r""" Number of tagged events after the calibration :math:`N_t = N_\mathrm{tagged} - N_\mathrm{overflow}`.
            Events with mistag > 0.5 are overflow events and are not tagged by convention.
        """
        return self._tagdata.ctagged.sum() - self._tagdata.cal_overflow[self._tagdata.ctagged].sum()

    @functools.cached_property
    def cal_Nts(self):
        """ Number of tagged events after calibration in selection without overflow """
        return self._tagdata.ctagged_sel.sum() - self._tagdata.cal_overflow[self._tagdata.ctagged_sel].sum()

    @functools.cached_property
    def cal_Nwt(self):
        """ Sum of all event weights of tagged and calibrated events without overflow event weights """
        N  = self._full_data.weight[self._full_data.ctagged].sum()
        N -= self._full_data.weight[self._full_data.ctagged & self._full_data.cal_overflow].sum()
        return N

    @functools.cached_property
    def cal_Nwts(self):
        """ Sum of all event weights of tagged and calibrated events in selection """
        N  = self._tagdata.weight[self._tagdata.ctagged_sel].sum()
        # N -= self._tagdata.weight[self._tagdata.cal_overflow].sum()
        return N

    @functools.cached_property
    def avg_eta(self):
        r""" Mean mistag
            :math:`\langle\eta\rangle = \displaystyle\frac{\sum_i w_i \eta_i}{\sum_i w_i}`
            whereby the sums run over all tagged and selected events and :math:`w_i` are the event weights.
        """
        return np.average(self._tagdata.eta, weights=self._tagdata.weight)

    def _init_timeinfo(self, mode, DM, DG, resolution_model):
        # Computes flavour impurity for each event. If B oscillation probability
        # is > 50%, production flavour is assumed to be the opposite
        if mode == "Bu":
            self._full_data.eval("osc_dilution = 0", inplace=True)
            self._tagdata.eval("osc_dilution = 0", inplace=True)
            Amix = None
        else:
            Amix = mixing_asymmetry(self._full_data.tau,
                                    DM     = DM,
                                    DG     = DG,
                                    tauerr = self._full_data.tau_err if "tau_err" in self._full_data else None,
                                    a      = 0,
                                    res    = resolution_model)
            self._full_data.loc[:, "osc_dilution"] = 0.5 * (1.0 - np.abs(Amix))
            self._tagdata.loc[:, "osc_dilution"] = np.array(self._full_data.loc[self._full_data.tagged_sel, "osc_dilution"])

        # Update production asymmetry given mixing asymmetry
        # and measures of "tag correctness"
        if mode != "Bu":
            self._full_data.loc[np.sign(Amix) == -1, "prod_flav"] *= -1

            self._tagdata["prod_flav"] = np.array(self._full_data.loc[self._full_data.tagged_sel, "prod_flav"])

            self._tagdata.correct_tags = self._tagdata.dec == self._tagdata.prod_flav
            self._tagdata.wrong_tags   = ~self._tagdata.correct_tags

    def _compute_calibrated_statistics(self, func, minimizer):
        warnings = []
        if not minimizer.accurate:
            warnings.append(FTCWarning("MinimizerWarning", "Minimization did not converge!"))

        if isinstance(minimizer, iminuit.Minuit):
            self.params.set_calibration_flavour([minimizer.values[n] for n in minimizer.parameters], minimizer.covariance.tolist())
        else:
            self.params.set_calibration_flavour(minimizer.values, minimizer.covariance)

        self._full_data.eval("omega = 0.5", inplace=True)
        self.func_ref = func

        # Convert to delta parameter convention, then evaluate using p's only
        self._full_data.loc[self._full_data.tagged, "omega"] = self.func_ref.eval_averaged(self.params.params_average,
                                                                                           eta = self._full_data.eta[self._full_data.tagged])
        self._full_data.eval("cal_overflow = omega > 0.5", inplace=True)
        nOverflow  = self._full_data.cal_overflow.sum()
        nUnderflow = (self._full_data.omega < 0).sum()
        if nOverflow > 0:
            warnings.append(FTCWarning("OverflowWarning", f"{nOverflow} calibrated mistag values > 0.5"))
        if nUnderflow > 0:
            warnings.append(FTCWarning("UnderflowWarning", f"{nUnderflow} calibrated mistag values < 0"))

        # self._full_data.loc[self._full_data.cal_overflow > 0.5, "cdec"] = 0

        self._full_data.eval("ctagged = (omega < 0.5)", inplace=True)
        self._full_data.eval("cdec = dec", inplace=True)
        self._full_data.loc[~self._full_data.ctagged, "cdec"] = 0
        self._full_data.eval("ctagged_sel = ctagged & selected", inplace=True)

        self._tagdata["omega"]        = np.array(self._full_data.omega[self._full_data.tagged_sel])
        self._tagdata["cdec"]         = np.array(self._full_data.cdec[self._full_data.tagged_sel])
        self._tagdata["ctagged"]      = np.array(self._full_data.ctagged[self._full_data.tagged_sel])
        self._tagdata["ctagged_sel"]  = np.array(self._full_data.ctagged_sel[self._full_data.tagged_sel])
        self._tagdata["cal_overflow"] = np.array(self._full_data.cal_overflow[self._full_data.tagged_sel])

        self.tagging_efficiency.cache_clear()
        self.dilution_squared.cache_clear()
        self.mistag_rate.cache_clear()
        self.tagging_power.cache_clear()
        self.effective_mistag.cache_clear()

        # del self.cal_Noverflow
        # del self.cal_Nt
        # del self.cal_Nts
        # del self.cal_Nwt
        # del self.cal_Nwts

        self._is_calibrated = True

        return warnings

    @functools.lru_cache(maxsize=4)
    def tagging_efficiency(self, calibrated, inselection=True):
        r"""
        Computes the fraction of tagged events
        :math:`\epsilon_{\mathrm{tag}}=\displaystyle\frac{N_t}{N}\pm\sqrt{\frac{N_t (N - N_t)}{N_\mathrm{eff}}}`

        :param calibrated: Whether to use calibrated statistics
        :type calibrated: bool
        :param inselection: Whether to only use events in selection
        :type inselection: bool

        :return: tuple(Tagging efficiency, Tagging efficiency uncertainty)
        :return type: tuple
        """
        if calibrated:
            if not self._is_calibrated:
                return None, None
            if inselection:
                N, Nt, Neff = self.Nws, self.cal_Nwts, self.Neffs
            else:
                N, Nt, Neff = self.Nw, self.cal_Nwt, self.Neff
        else:
            if inselection:
                N, Nt, Neff = self.Nws, self.Nwts, self.Neffs
            else:
                N, Nt, Neff = self.Nw, self.Nwt, self.Neff

        rate     = Nt / N
        untagged = N - Nt
        return rate, np.sqrt(Nt * untagged / Neff) / N

    @functools.lru_cache
    def dilution_squared(self, calibrated, inselection=True):
        r""" Returns the mean squared flavour tagging dilution, i.e. the tagging power of tagged events.

        :param calibrated: Whether to use calibrated statistics
        :type calibrated: bool
        :param inselection: Whether to only use events in selection
        :type inselection: bool
        :return: tuple(:math:`\langle\mathcal{D}^2\rangle`, :math:`\sigma(\langle\mathcal{D}^2\rangle)`, :math:`\sigma^{\mathrm{cal}}(\langle\mathcal{D}^2\rangle)`)
        :return type: tuple

        The expectation value of a power of the flavour tagging dilution is computed
        :math:`\langle\mathcal{D}^n\rangle = \displaystyle\frac{1}{N_{wts}}\sum_{\substack{i, \mathrm{tagged}\\\mathrm{selected}}}^N w_i(1-2\omega(\eta_i,\vec p))^n`

        whereby
        :math:`\displaystyle N_{wts} =\sum_{\substack{i, \mathrm{tagged}\\\mathrm{selected}}}^Nw_i`

        :math:`\displaystyle\sigma(\langle\mathcal{D}^2\rangle)=\sqrt{\frac{\langle\mathcal{D}^4\rangle-\langle\mathcal{D}^2\rangle^2}{N_{wts}-1}}`

        with :math:`\displaystyle\nabla_{\vec{p}}\langle\mathcal{D}^2\rangle= \frac{-4}{N_{wts}}\sum_{\substack{i, \mathrm{tagged}\\\mathrm{selected}}}^N \displaystyle \nabla_{\vec{p}} \omega(\eta_i, \vec p) (1-2\omega(\eta_i)) w_i`,

        where :math:`\omega` is the calibration function and :math:`\vec p` are its parameters follows the mean squared dilution error

        :math:`\sigma^{\mathrm{cal}}(\langle\mathcal{D}^2\rangle)=\sqrt{\nabla_{\vec{p}}\langle\mathcal{D}^2\rangle\cdot C \cdot\nabla_{\vec{p}}\langle\mathcal{D}^2\rangle^\top}`
        """

        if calibrated:
            if inselection:
                D = np.array(1 - 2 * self._tagdata.omega)
                mean_D_sq = np.sum(D**2 * self._tagdata.weight) / self.cal_Nwts
                mean_D_4  = np.sum(D**4 * self._tagdata.weight) / self.cal_Nwts

                grad_calib = self.func_ref.gradient_averaged(self.params.params_average, self._tagdata.eta)
                grad_mean_D_sq = -4 * np.sum(grad_calib * D * np.array(self._tagdata.weight), axis=1) / self.cal_Nwts
                cal_error = np.sqrt(grad_mean_D_sq @ self.params.covariance_average @ grad_mean_D_sq.T)
            else:
                D = np.array(1 - 2 * self._full_data[self._full_data.tagged].omega)
                mean_D_sq = np.sum(D**2 * self._full_data[self._full_data.tagged].weight) / self.cal_Nwt
                mean_D_4  = np.sum(D**4 * self._full_data[self._full_data.tagged].weight) / self.cal_Nwt

                grad_calib = self.func_ref.gradient_averaged(self.params.params_average, self._full_data[self._full_data.tagged].eta)
                grad_mean_D_sq = -4 * np.sum(grad_calib * D * np.array(self._full_data[self._full_data.tagged].weight), axis=1) / self.cal_Nwt
                cal_error = np.sqrt(grad_mean_D_sq @ self.params.covariance_average @ grad_mean_D_sq.T)
        else:
            if inselection:
                D = np.array(1 - 2 * self._tagdata.eta)
                mean_D_sq = np.sum(D**2 * self._tagdata.weight) / self.Nwts
                mean_D_4  = np.sum(D**4 * self._tagdata.weight) / self.Nwts
            else:
                D = np.array(1 - 2 * self._full_data[self._full_data.tagged].eta)
                mean_D_sq = np.sum(D**2 * self._full_data[self._full_data.tagged].weight) / self.Nwt
                mean_D_4  = np.sum(D**4 * self._full_data[self._full_data.tagged].weight) / self.Nwt
            cal_error = None

        return mean_D_sq, np.sqrt((mean_D_4 - mean_D_sq**2) / (self.Nwt - 1)), cal_error

    @functools.lru_cache(maxsize=4)
    def tagging_power(self, calibrated, inselection=True):
        r"""
        Returns the effective tagging efficiency
        :math:`\epsilon_{\mathrm{tag,eff}}=\displaystyle\epsilon_\mathrm{tag}\langle\mathcal{D}^2\rangle`

        :param calibrated: Whether to use calibrated statistics
        :type calibrated: bool
        :param inselection: Whether to only use events in selection
        :type inselection: bool

        :return: tuple(:math:`\epsilon_{\mathrm{tag,eff}},\sigma(\epsilon_{\mathrm{tag,eff}})`)
        :return type: tuple
        """
        D_sq, D_sq_err, D_sq_calerr = self.dilution_squared(calibrated, inselection)
        tageff, tageff_err = self.tagging_efficiency(calibrated, inselection)

        if calibrated:
            return D_sq * tageff, np.sqrt(tageff**2 * D_sq_err**2 + D_sq**2 * tageff_err**2), tageff * D_sq_calerr 
        else:
            return D_sq * tageff, np.sqrt(tageff**2 * D_sq_err**2 + D_sq**2 * tageff_err**2)

    @functools.lru_cache(maxsize=4)
    def mistag_rate(self, calibrated, inselection=True):
        r""" Returns Mean mistag rate of selected statistics with binomial uncertainty

            :math:`\langle\omega\rangle=\displaystyle\frac{N_\mathrm{wrong}}{N_\mathrm{wrong}+N_\mathrm{correct}}\pm\frac{1}{N_{wts}}\sqrt{\frac{N_\mathrm{correct}N_\mathrm{wrong}}{N_{wts}}}`

            whereby :math:`N_\mathrm{correct}`(:math:`N_\mathrm{wrong}`) is the sum of weights of events in selection where the tag decision does (not)
            match the predicted production flavour and :math:`N_{wts}` is the sum of weights of all tagged events in selection.

            :param calibrated: Whether to use calibrated mistag and decisions
            :type calibrated: bool
            :param inselection: Whether to only use events in selection
            :type inselection: bool
            :return: Mistag rate and uncertainty
            :rtype: tuple
        """
        if calibrated:
            if not self._is_calibrated:
                return None, None

            if inselection:
                Nright = self._tagdata.weight[self._tagdata.ctagged_sel & self._tagdata.correct_tags].sum()
                Nwrong = self._tagdata.weight[self._tagdata.ctagged_sel & self._tagdata.wrong_tags].sum()
                Nweighted = self.cal_Nwts
            else:
                return -999, -999  # WIP
        else:
            if inselection:
                Nright = self._tagdata.weight[self._tagdata.correct_tags].sum()
                Nwrong = self._tagdata.weight[self._tagdata.wrong_tags].sum()
                Nweighted = self.Nwts
            else:
                return -999, -999  # WIP

        return Nwrong / (Nwrong + Nright), np.sqrt(Nright * Nwrong / Nweighted) / Nweighted

    @functools.lru_cache(maxsize=4)
    def effective_mistag(self, calibrated, inselection=True):
        r""" Returns the effective mistag :math:`\omega^{\text{eff}}`

             From :math:`\langle\mathcal{D}^2\rangle=(1-2\omega^{\text{eff}})^2`

             follows

             :math:`\omega^{\text{eff}} = \displaystyle\frac{1}{2}\left(1-\sqrt{\langle\mathcal{D}^2\rangle}\right)
             \pm\frac{\sigma(\langle\mathcal{D}^2\rangle)}{4\sqrt{\langle\mathcal{D}^2\rangle}}
             \pm\frac{\sigma^\mathrm{cal}(\langle\mathcal{D}^2\rangle)}{4\sqrt{\langle\mathcal{D}^2\rangle}}`

             :param calibrated: Whether to use calibrated statistics
             :type calibrated: bool
             :param inselection: Whether to only use events in selection
             :type inselection: bool

             :return: Tuple of effective mistag, effective mistag uncertatiny, effective mistag calibration uncvertainty
             :return type: tuple
        """

        D_sq, D_sq_err, D_sq_calerr = self.dilution_squared(calibrated, inselection)

        if calibrated:
            return 0.5 * (1 - np.sqrt(D_sq)), D_sq_err / (4 * np.sqrt(D_sq)), D_sq_calerr / (4 * np.sqrt(D_sq))
        else:
            return 0.5 * (1 - np.sqrt(D_sq)), D_sq_err / (4 * np.sqrt(D_sq))
