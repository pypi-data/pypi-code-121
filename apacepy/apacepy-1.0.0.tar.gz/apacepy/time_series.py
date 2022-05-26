from math import sqrt

from apacepy.calibration_support import get_lnl_of_a_time_series, FeasibleConditions
from apacepy.econ_eval import CostHealthOverDeltaT


class IncidenceTimeSeries:
    """ incidence time series """

    def __init__(self):

        self.timeSeries = []
        self.cumIncdSinceLastRecording = None  # sum of incidence since the last recording

    def update_incd(self, added_value):
        """ updates incidence of this period """

        if added_value is not None:
            if self.cumIncdSinceLastRecording is None:
                self.cumIncdSinceLastRecording = 0
            self.cumIncdSinceLastRecording += added_value

    def record(self):
        """ records the incidence over the past period """

        if self.cumIncdSinceLastRecording is not None:
            self.timeSeries.append(self.cumIncdSinceLastRecording)
            self.cumIncdSinceLastRecording = 0
        else:
            self.timeSeries.append(None)

    def reset(self):
        self.cumIncdSinceLastRecording = None
        self.timeSeries.clear()


class _SumTimeSeries:
    """ master class to calculate the sum of incidence, prevalence, and cumulative incidence for multiple
    compartments """

    def __init__(self, name, compartments, first_nonzero_obs_marks_start_of_epidemic=False):
        self.name = name

        assert isinstance(compartments, list), 'compartments should be a list.'

        self.compartments = compartments
        self.feasibleConditions = None
        self.firstNonZeroObsMarksStartOfEpidemic = first_nonzero_obs_marks_start_of_epidemic
        self.surveillance = None
        self.healthCostOverDeltaT = None
        self.timeMonitor = None

    def add_feasible_conditions(self, feasible_conditions):
        """
        :param feasible_conditions: (FeasibleConditions)
        """

        assert isinstance(feasible_conditions, FeasibleConditions)
        self.feasibleConditions = feasible_conditions

    def update_incd(self, sim_time_index):
        pass

    def record_sim_output(self, epi_time):
        pass

    def add_and_get_surveillance(self):
        pass

    def record_surveillance(self, sim_time_index):
        pass

    def get_sim_time_series(self):
        pass

    def get_surveyed_time_series(self):
        return self.surveillance.surveyedTimeSeries

    def get_type(self):
        pass

    def reset(self):
        pass


class SumIncidence(_SumTimeSeries):
    """ to calculate the sum of incidence for multiple compartments """

    def __init__(self, name, compartments, if_surveyed=False,
                 first_nonzero_obs_marks_start_of_epidemic=False,
                 collect_cumulative_after_warm_up=None):
        """
        :param name: (string) name of this sum of incidence
        :param compartments: (string) compartments to sum to calculate the total incidence
        :param if_surveyed: (bool) set to True to survey this output
                (and to export the observations into the trajectory csv file).
        :param first_nonzero_obs_marks_start_of_epidemic: (bool) set to True if the first non-zero observation
                marks the start of the spread
        :param collect_cumulative_after_warm_up: (string)
                    's' to collect total incidence after when the simulation time passes the warm-up period
                    'e' to collect total incidence after when the epidemic time passes the warm-up period
        """

        if collect_cumulative_after_warm_up not in (None, 's', 'e'):
            raise ValueError("Invalid value for collect_cumulative_after_warm_up (should be None, 's', or 'e').")

        _SumTimeSeries.__init__(self,
                                name=name,
                                compartments=compartments,
                                first_nonzero_obs_marks_start_of_epidemic=first_nonzero_obs_marks_start_of_epidemic)

        # set up surveillance
        if if_surveyed or first_nonzero_obs_marks_start_of_epidemic:

            # if cumulative surveyed observations after warm-up should be collected
            collect = True if collect_cumulative_after_warm_up == 'e' else False

            self.surveillance = SurveyedIncidence(first_nonzero_obs_marks_start_of_epidemic=
                                                  first_nonzero_obs_marks_start_of_epidemic,
                                                  collect_cumulative_after_warm_up=collect)

        # if collect cumulative of the surveyed incidence
        if collect_cumulative_after_warm_up == 'e' and self.surveillance is None:
            raise ValueError('To collect cumulative surveyed incidence after the warm-up period, '
                             'the sum incidence needs to be surveyed.')

        # set up collecting simulated cumulative observations after the warm up
        self.collectCumAfterSimWarmUp = False
        if collect_cumulative_after_warm_up == 's':
            self.collectCumAfterSimWarmUp = True
            self.cumIncdAfterWarmUp = 0

        self.timeSeries = IncidenceTimeSeries()

    def reset(self):
        self.cumIncdAfterWarmUp = 0
        if self.surveillance is not None:
            self.surveillance.reset()
        self.timeSeries.reset()

    def update_incd(self, sim_time_index):
        """ updates incidence of this simulation period """

        incd = 0
        for c in self.compartments:
            incd += c.n_past_delta_t_incoming

        self.timeSeries.update_incd(added_value=incd)

        if self.surveillance is not None:
            self.surveillance.update_incd(added_value=incd)

        if self.healthCostOverDeltaT is not None:
            self.healthCostOverDeltaT.update(prevalence=0, incidence=incd)

        if self.collectCumAfterSimWarmUp and self.timeMonitor.get_if_sim_time_passed_warm_up_period(sim_time_index):
            self.cumIncdAfterWarmUp += incd

    def record_sim_output(self, epi_time):
        """ record simulation outputs (to be called at the beginning of each simulation output period)
        :param epi_time: (float) epidemic time
        :returns True if no feasibility condition is violated (and False otherwise)
        """

        # check feasibility
        if_feasible = True
        if self.feasibleConditions:
            if_feasible = self.feasibleConditions.check_if_acceptable(
                value=self.timeSeries.cumIncdSinceLastRecording,
                time=epi_time)

        # record
        self.timeSeries.record()

        return if_feasible

    def add_and_get_surveillance(self):
        """ add a surveillance if not already exists and returns it """

        if self.surveillance is None:
            self.surveillance = SurveyedIncidence()
        return self.surveillance

    def record_surveillance(self, sim_time_index):
        """ records the surveillance of outcomes (to be called at each observation period) """

        if self.surveillance:
            self.surveillance.record(sim_time_index=sim_time_index)

    def get_sim_time_series(self):
        return self.timeSeries.timeSeries

    def get_type(self):
        return 'incd'

    def setup_econ_outcome(self, par_health_per_new_member=None, par_cost_per_new_member=None):
        """ to specify which cost and health outcomes to collect
        :param par_health_per_new_member: (Parameter) of the change in health per new member
        :param par_cost_per_new_member: (Parameter) of the cost incurred per per new member
        """

        self.healthCostOverDeltaT = CostHealthOverDeltaT(
            par_health_per_new_member=par_health_per_new_member,
            par_cost_per_new_member=par_cost_per_new_member)


class SumPrevalence(_SumTimeSeries):
    """ to calculate the sum of prevalence for multiple compartments """

    def __init__(self, name, compartments, if_surveyed=False, first_nonzero_obs_marks_start_of_epidemic=False):
        """
        :param name: (string) name of this sum of prevalence
        :param compartments: (string) compartments to sum to calculate the total prevalence
        :param if_surveyed: (bool) set to True to survey this output
        :param first_nonzero_obs_marks_start_of_epidemic: (bool) set to True if the first non-zero observation
                marks the start of the spread
        """
        _SumTimeSeries.__init__(self,
                                name=name,
                                compartments=compartments,
                                first_nonzero_obs_marks_start_of_epidemic=first_nonzero_obs_marks_start_of_epidemic)

        if if_surveyed or first_nonzero_obs_marks_start_of_epidemic:
            self.surveillance = SurveyedPrevalence(first_nonzero_obs_marks_start_of_epidemic=
                                                   first_nonzero_obs_marks_start_of_epidemic)

        self.timeSeries = []

    def reset(self):
        if self.surveillance is not None:
            self.surveillance.reset()
        self.timeSeries.clear()

    def record_sim_output(self, epi_time):
        """ record simulation outputs (to be called at the beginning of each simulation output period)
        :param epi_time: (float) epidemic time
        :returns True if no feasibility condition is violated (and False otherwise)
        """

        prev = 0
        for c in self.compartments:
            prev += c.size

        self.timeSeries.append(prev)

        # check feasibility
        if_feasible = True
        if self.feasibleConditions:
            if_feasible = self.feasibleConditions.check_if_acceptable(value=prev, time=epi_time)

        return if_feasible

    def add_and_get_surveillance(self):
        """ add a surveillance if not already exists and returns it """

        if self.surveillance is None:
            self.surveillance = SurveyedPrevalence()
        return self.surveillance

    def record_surveillance(self, sim_time_index):
        """ records the surveillance of outcomes (to be called at each observation period) """

        if self.surveillance:
            self.surveillance.record(sim_time_index=sim_time_index,
                                     value=self.timeSeries[-1])

    def get_sim_time_series(self):
        return self.timeSeries

    def get_type(self):
        return 'prev'


class SumCumulativeIncidence(_SumTimeSeries):
    """ to calculate the sum of cumulative incidence for multiple compartments """

    def __init__(self, name, compartments, if_surveyed=False, first_nonzero_obs_marks_start_of_epidemic=False):
        """
        :param name: (string) name of this sum of cumulative incidence
        :param compartments: (string) compartments to sum to calculate the total cumulative incidence
        :param if_surveyed: (bool) set to True to survey this output
        :param first_nonzero_obs_marks_start_of_epidemic: (bool) set to True if the first non-zero observation
                marks the start of the spread
        """
        _SumTimeSeries.__init__(self,
                                name=name,
                                compartments=compartments,
                                first_nonzero_obs_marks_start_of_epidemic=first_nonzero_obs_marks_start_of_epidemic)

        if if_surveyed or first_nonzero_obs_marks_start_of_epidemic:
            self.surveillance = SurveyedCumIncidence(first_nonzero_obs_marks_start_of_epidemic=
                                                     first_nonzero_obs_marks_start_of_epidemic)

        self.cumIncd = 0  # cumulative incidence since the start of the simulation
        self.timeSeries = []

    def reset(self):
        if self.surveillance is not None:
            self.surveillance.reset()
        self.cumIncd = 0
        self.timeSeries.clear()

    def update_incd(self, sim_time_index):
        """ update incidence of this period """

        incd = 0
        for c in self.compartments:
            incd += c.n_past_delta_t_incoming

        self.cumIncd += incd

    def record_sim_output(self, epi_time):
        """ record simulation outputs (to be called at the beginning of each simulation output period)
        :param epi_time: (float) epidemic time
        :returns True if no feasibility condition is violated (and False otherwise)
        """

        self.timeSeries.append(self.cumIncd)

        # check feasibility
        if_feasible = True
        if self.feasibleConditions:
            if_feasible = self.feasibleConditions.check_if_acceptable(value=self.cumIncd, time=epi_time)

        return if_feasible

    def add_and_get_surveillance(self):
        """ add a surveillance if not already exists and returns it """

        if self.surveillance is None:
            self.surveillance = SurveyedCumIncidence()
        return self.surveillance

    def record_surveillance(self, sim_time_index):
        """ records the surveillance of outcomes (to be called at each observation period) """

        if self.surveillance:
            self.surveillance.record(sim_time_index=sim_time_index,
                                     value=self.cumIncd)

    def get_sim_time_series(self):
        return self.timeSeries

    def get_type(self):
        return 'cum-incd'


class _SurveyedTimeSeries:

    def __init__(self, first_nonzero_obs_marks_start_of_epidemic=False):

        self.firstNoneZeroObsMarksStartOfEpidemic = first_nonzero_obs_marks_start_of_epidemic
        self.firstNoneZeroObsObtained = False   # used only if the first non-zero observation
                                                # marks the start of the epidemic

        # this stores the observed values after the epidemic is detected
        # it will hold None for survey periods when the epidemic is not detected yet
        self.surveyedTimeSeries = []
        self.timeMonitor = None

    def _reset(self):
        self.firstNoneZeroObsObtained = False
        self.surveyedTimeSeries.clear()

    def update_incd(self, added_value):
        pass

    def record(self, sim_time_index, value=None):
        pass

    def _record_and_find_if_epidemic_started(self, sim_time_index, last_recording):

        # find if epidemic has started
        if self.timeMonitor.epidemicStarted:
            self.surveyedTimeSeries.append(last_recording)
        else:
            # check if the first non-zero observation has obtained (if so, this marks the start of the epidemic).
            if self.firstNoneZeroObsMarksStartOfEpidemic:
                if not self.firstNoneZeroObsObtained:
                    if last_recording is not None and last_recording > 0:
                        # first non-zero observation obtained
                        self.firstNoneZeroObsObtained = True
                        # announce the start of the epidemic
                        self.timeMonitor.announce_start_of_epidemic(sim_time_index=sim_time_index)

                if self.firstNoneZeroObsObtained:
                    self.surveyedTimeSeries.append(last_recording)
                else:
                    # add None for observation periods when the epidemic is not detected yet
                    self.surveyedTimeSeries.append(None)
            else:
                # add None for observation periods when the epidemic is not detected yet
                self.surveyedTimeSeries.append(None)


class SurveyedIncidence(_SurveyedTimeSeries):
    """ class to collect surveillance on an incidence time-series """

    def __init__(self, first_nonzero_obs_marks_start_of_epidemic=False,
                 collect_cumulative_after_warm_up=False):
        """
        :param first_nonzero_obs_marks_start_of_epidemic: (bool) set to True if the first non-zero observation
                marks the start of the spread
        :param collect_cumulative_after_warm_up: (bool) if collects total incidence after the warm-up period
        """

        _SurveyedTimeSeries.__init__(self,
                                     first_nonzero_obs_marks_start_of_epidemic=
                                     first_nonzero_obs_marks_start_of_epidemic)

        # to collect incidence during surveillance periods (it gets updated only at surveillance periods)
        self.simIncidence = IncidenceTimeSeries()

        self.collectCumulativeAfterWarmUp = collect_cumulative_after_warm_up
        if collect_cumulative_after_warm_up:
            self.cumIncdAfterWarmUp = 0  # cumulative incidence since the end of the warm-up period

    def reset(self):
        self._reset()
        self.cumIncdAfterWarmUp = 0
        self.simIncidence.reset()

    def update_incd(self, added_value):
        """ updates the incidence during the past recording period """
        self.simIncidence.update_incd(added_value=added_value)

    def record(self, sim_time_index, value=None):
        """ record the incidence during the past observation period
        :param sim_time_index: (int) current simulation time index
        :param value: [won't be used]
        """

        # record incidence
        self.simIncidence.record()

        # record surveillance and find if the epidemic hast started
        self._record_and_find_if_epidemic_started(
            sim_time_index=sim_time_index,
            last_recording=self.simIncidence.timeSeries[-1])

        # accumulate the total incidence if past warm-up
        if self.collectCumulativeAfterWarmUp \
                and self.timeMonitor.get_if_epi_time_passed_warm_up_period(sim_time_index=sim_time_index):
            self.cumIncdAfterWarmUp += self.surveyedTimeSeries[-1]


class SurveyedPrevalence(_SurveyedTimeSeries):

    def __init__(self, first_nonzero_obs_marks_start_of_epidemic=False):
        """
        :param first_nonzero_obs_marks_start_of_epidemic: (bool) set to True if the first non-zero observation
               marks the start of the spread
        """
        _SurveyedTimeSeries.__init__(self,
                                     first_nonzero_obs_marks_start_of_epidemic=
                                     first_nonzero_obs_marks_start_of_epidemic)

    def reset(self):
        self._reset()

    def record(self,  sim_time_index, value=None):
        """ record the prevalence at current surveillance period
        :param sim_time_index: (int) current simulation time index
        :param value: (float) current prevalence
        """

        # record surveillance and find if the epidemic hast started
        # assume that to observe size of a compartment we don't need for the epidemic to be detected.
        self._record_and_find_if_epidemic_started(sim_time_index=sim_time_index,
                                                  last_recording=value)


class SurveyedCumIncidence(_SurveyedTimeSeries):

    def __init__(self, first_nonzero_obs_marks_start_of_epidemic=False):

        _SurveyedTimeSeries.__init__(self,
                                     first_nonzero_obs_marks_start_of_epidemic=
                                     first_nonzero_obs_marks_start_of_epidemic)

    def reset(self):
        self._reset()

    def record(self, sim_time_index, value=None):
        """ record the cumulative incidence at current surveillance period
        :param sim_time_index: (int) current simulation time index
        :param value: current cumulative incidence
        """

        # record surveillance and find if the epidemic hast started
        self._record_and_find_if_epidemic_started(sim_time_index=sim_time_index,
                                                  last_recording=value)


class RatioTimeSeries:
    """ master class to calculate the ratio of incidence, prevalence, and cumulative incidence """

    def __init__(self, name,
                 numerator_compartment_prev=None, numerator_compartment_incd=None, numerator_compartment_cum_incd=None,
                 denominator_compartment_prev=None, denominator_compartment_incd=None,
                 denominator_compartment_cum_incd=None,
                 numerator_sum_time_series=None, denominator_sum_time_series=None,
                 collect_stat_after_warm_up=False,
                 if_surveyed=False, survey_size_param=None):

        if numerator_sum_time_series is not None:
            assert isinstance(numerator_sum_time_series, _SumTimeSeries), \
                "To define ratio time-series '{}', numerator_sum_time_series should be a sum time-series.".format(name)
        if denominator_sum_time_series is not None:
            assert isinstance(denominator_sum_time_series, _SumTimeSeries), \
                "To define ratio time-series '{}', denominator_sum_time_series should be a sum time-series.".format(name)

        if collect_stat_after_warm_up:
            if_surveyed = True

        self.name = name
        self.simTimeSeries = []  # to store ratios during simulation periods
        self.surveyedTimeSeries = []  # to store ratio during survey periods
        self.surveyedTimeSeriesWithoutNoise = []  # this is for calibration

        # the time-series of summation time-series (SumIncidence, SumPrevalence, or SumCumulativeIncidence)
        self.numerSimTimeSeries = None  # for numerator
        self.denomSimTimeSeries = None  # for denominator

        # the time-series of surveyed summation time-series
        # (SurveyedIncidence, SurveyedPrevalence, SurveyedCumIncidence)
        self.numerSurveyedTimeSeries = None
        self.denomSurveyedTimeSeries = None

        # survey
        self.ifSurveyed = if_surveyed
        self.surveySizeParam = survey_size_param
        self.feasibleConditions = None

        # calibration
        self.calibRatios = None
        self.calibSurveySizes = None
        self.calibVariances = None

        # get simulation time-series, surveyed time-series, and the type of numerator
        self.numerSimTimeSeries, self.numerSurveyedTimeSeries, numer_type = self._get_time_series_and_type(
            compart_prev=numerator_compartment_prev,
            compart_incd=numerator_compartment_incd,
            compart_cum_incd=numerator_compartment_cum_incd,
            sum_time_series=numerator_sum_time_series,
            if_surveyed=if_surveyed)

        # get simulation time-series, surveyed time-series, and the type of denominator
        self.denomSimTimeSeries, self.denomSurveyedTimeSeries, denom_type = self._get_time_series_and_type(
            compart_prev=denominator_compartment_prev,
            compart_incd=denominator_compartment_incd,
            compart_cum_incd=denominator_compartment_cum_incd,
            sum_time_series=denominator_sum_time_series,
            if_surveyed=if_surveyed)

        # find the type of this ratio time-series
        self.type = numer_type + '/' + denom_type
        if self.type in ('prev/incd', 'prev/cum-incd', 'cum-incd/incd'):
            raise ValueError('Ratio statistics of type {} is not defined.'.format(self.type))

        # collecting stats after the end of warm-up period
        self.stat = None
        if collect_stat_after_warm_up:
            self.stat = CollectStatForRatioTimeSeries(ratio_type=self.type)

    def reset(self):
        self.simTimeSeries.clear()
        self.surveyedTimeSeries.clear()
        self.surveyedTimeSeriesWithoutNoise.clear()
        if self.stat is not None:
            self.stat.reset()

    @staticmethod
    def _get_time_series_and_type(compart_prev=None, compart_incd=None, compart_cum_incd=None,
                                  sum_time_series=None, if_surveyed=False):
        """
        :param compart_prev: compartment representing prevalence
        :param compart_incd: compartment representing incidence
        :param compart_cum_incd: compartment representing cumulative incidence
        :param sum_time_series: summation time-series (SumPrevalence, SumIncidence, SumCumulativeIncidence)
        :param if_surveyed: (bool) if the compartment or sum time-series should be surveyed
        :return: (simulation time-series, survey time-series, type of time-series);
                type could be 'prev', 'incd', or 'cum-incd'
        """

        sim_time_series = None
        surveyed_time_series = None
        time_series_type = None

        # if summation time-series is provided
        if sum_time_series is not None:

            # get simulation time-series
            sim_time_series = sum_time_series.get_sim_time_series()

            # get type
            time_series_type = sum_time_series.get_type()

            # add surveillance if needed and not already added
            if if_surveyed:
                surveyed_time_series = sum_time_series.add_and_get_surveillance().surveyedTimeSeries

        else:  # use compartment history
            if compart_prev is not None:
                time_series_type = 'prev'
                compart = compart_prev
            elif compart_incd is not None:
                time_series_type = 'incd'
                compart = compart_incd
            elif compart_cum_incd is not None:
                time_series_type = 'cum-incd'
                compart = compart_cum_incd
            else:
                raise ValueError('Either sum time-series or a compartment with time-series should be provided.')

            # add simulation time-series if not already added
            sim_time_series = compart.add_and_get_time_series(time_series_type=time_series_type)

            # add surveillance if needed and not already added
            if if_surveyed:
                raise ValueError("Surveillance on compartments is not defined. "
                                 "To use the compartment '{}' in a ratio time-series with surveillance, "
                                 "pass a sum time-series defined on this compartment "
                                 "when instantiating the ratio time-series.".format(compart.name))

        return sim_time_series, surveyed_time_series, time_series_type

    def add_feasible_conditions(self, feasible_conditions):
        """ add feasible conditions
        :param feasible_conditions: (FeasibleCondition)
        """

        assert isinstance(feasible_conditions, FeasibleConditions)
        self.feasibleConditions = feasible_conditions

    def add_calibration_targets(self, ratios, survey_sizes=None, variances=None):
        """ adds calibration targets with survey size to calculate error
        :param ratios: (list) of observed ratios
        :param survey_sizes: (list) of survey sizes
        :param variances: (list) of variances
        """

        # at least one element should be not None
        assert not all(r is None for r in ratios), 'At least one observed ratios should have a value.'

        self.calibRatios = ratios
        self.calibSurveySizes = survey_sizes
        self.calibVariances = variances

    def calculate_lnl(self):
        """
        :returns the ln(likelihood) of the observed ratios for this trajectory """

        # if self.type in ('incd/incd', 'incd/prev'):
        #     sim_ratios = self.surveyedTimeSeriesWithoutNoise[n_obs_before_calibration + 1:]
        # else:
        #     sim_ratios = self.surveyedTimeSeriesWithoutNoise[n_obs_before_calibration:]

        sim_ratios = self.surveyedTimeSeriesWithoutNoise[1:]
        return get_lnl_of_a_time_series(observed_ratios=self.calibRatios,
                                        sim_ratios=sim_ratios,
                                        observed_ns=self.calibSurveySizes,
                                        observed_vars=self.calibVariances,
                                        sim_ns=self.denomSurveyedTimeSeries)

    def record_sim_output(self, epi_time):
        """ record simulation outputs (to be called at the beginning of each simulation output period)
        :returns True if no feasibility condition is violated (and False otherwise)
        """

        # get numerator value if it is recorded
        try:
            numerator_value = self.numerSimTimeSeries[-1]
        except IndexError:
            numerator_value = None

        # get denominator value
        # (note that for incd/prev',
        # we get the value at the beginning of the last simulation period)
        if self.type == 'incd/prev':
            try:
                denom_value = self.denomSimTimeSeries[-2]
            except IndexError:
                denom_value = None
        else:
            try:
                denom_value = self.denomSimTimeSeries[-1]
            except IndexError:
                raise IndexError('For ratio time-series "{}", make sure '
                                 'the denominator is included in the argument list_of_sum_time_series '
                                 'when populating the model.'.format(self.name))

        # calculate the ratio
        if denom_value is None or numerator_value is None or denom_value == 0:
            ratio = None
        else:
            ratio = numerator_value / denom_value

        # check feasibility
        if_feasible = True
        if self.feasibleConditions is not None:
            if_feasible = self.feasibleConditions.check_if_acceptable(value=ratio, time=epi_time)

        # record the ratio
        self.simTimeSeries.append(ratio)

        return if_feasible

    def record_surveillance(self, if_epidemic_started, noise_rng=None, warmup_ended=True):
        """ records the surveillance of ratio (to be called at each observation period) """

        if not self.ifSurveyed:
            return

        # if epidemic hast not yet started, surveillance is not available
        if not if_epidemic_started:
            self.surveyedTimeSeries.append(None)
            self.surveyedTimeSeriesWithoutNoise.append(None)
            return

        # get numerator value if it is recorded
        try:
            numer_value = self.numerSurveyedTimeSeries[-1]
        except IndexError:
            numer_value = None

        # get denominator value if it is recorded
        try:
            if self.type == 'incd/prev':
                denom_value = self.denomSurveyedTimeSeries[-2]
            else:
                denom_value = self.denomSurveyedTimeSeries[-1]
        except IndexError:
            denom_value = None

        # calculate the ratio
        if denom_value is None or numer_value is None or denom_value == 0:
            ratio = None
            ratio_with_noise = None
        else:
            ratio = numer_value / denom_value
            # add noise if needed
            ratio_with_noise = ratio
            if self.surveySizeParam is not None:
                sd_dev = sqrt(ratio * (1 - ratio))
                ratio_with_noise += noise_rng.normal(loc=0, scale=sd_dev / sqrt(self.surveySizeParam.value))

        self.surveyedTimeSeriesWithoutNoise.append(ratio)
        self.surveyedTimeSeries.append(ratio_with_noise)

        # record stats after the warmup
        if self.stat is not None and warmup_ended:
            self.stat.update(ratio=ratio)

    def get_value(self):
        """ :returns the last value recorded """

        if len(self.surveyedTimeSeries) < 1:
            return None
        else:
            return self.surveyedTimeSeries[-1]


class CollectStatForRatioTimeSeries:

    def __init__(self, ratio_type):

        if ratio_type in ('incd/incd', 'incd/prev'):
            self.projectingAveIncd = False
            self.sumOfRatiosAfterWarmup = 0
            self.nOfRatiosAfterWarmUp = 0
        else:
            raise ValueError('Projecting outcomes after the warm-up period is only available for'
                             " ratio time-series of type 'incidence over incidence' or 'incidence over prevalence'.")

    def reset(self):
        self.sumOfRatiosAfterWarmup = 0
        self.nOfRatiosAfterWarmUp = 0

    def update(self, ratio):

        if ratio is not None:
            self.sumOfRatiosAfterWarmup += ratio
            self.nOfRatiosAfterWarmUp += 1

    def get_projected_ave_incd(self):

        return self.sumOfRatiosAfterWarmup/self.nOfRatiosAfterWarmUp
