from apacepy.time_series import IncidenceTimeSeries, SumIncidence


class TimeMonitor:

    def __init__(self,
                 delta_t,
                 epidemic_started=False,
                 incidence_marks_start_of_epidemic=True,
                 n_deltats_in_warm_up_period=0,
                 n_deltats_in_survey_periods=1):
        """
        :param delta_t
        :param epidemic_started: set to True if the epidemic is considered started from the beigning
        :param incidence_marks_start_of_epidemic:
                True to assume that an incident case marks the start of the epidemic and
                False to assume that observed prevalence marks the start of the epidemic
        :param n_deltats_in_warm_up_period: (int) number of deltaTs in warm-up period
        :param n_deltats_in_survey_periods: number of deltaTs in a survey period
        """

        self.deltaT = delta_t
        self.simPeriod = 0  # current index of simulation period
        self.surveyPeriod = None  # current index of survey period

        self.incdMarksEpidemic = incidence_marks_start_of_epidemic
        self.nDeltaTsInSurveyPeriods = int(n_deltats_in_survey_periods)
        self.defaultIfEpidemicStarted = epidemic_started
        self.epidemicStarted = False
        self.simTimesAndSimPeriods = []  # list of [simulation times, simulation periods]
        self.surveyTimesAndSurveyPeriods = []  # list of [survey times, survey periods]

        self.simTimeIndexWhenEpidemicStarted = None
        self.nDeltaTsInWarmUpPeriod = n_deltats_in_warm_up_period
        self.simTimePassedWarmUp = False
        self.epiTimePassedWarmUp = False

        self.reset()

    def reset(self):
        self.simPeriod = 0
        self.surveyPeriod = None
        self.simTimePassedWarmUp = False
        self.epiTimePassedWarmUp = False
        self.simTimeIndexWhenEpidemicStarted = None
        self.simTimesAndSimPeriods.clear()
        self.surveyTimesAndSurveyPeriods.clear()

        # find current survey period
        # if the start of the epidemic depends on the first non-zero observation of a time-series,
        # we let the observation period be None for now
        self.epidemicStarted = self.defaultIfEpidemicStarted
        if self.epidemicStarted:
            # if at time 0 epidemic has already started, we assume that it implies that the size of
            # compartments at time 0 was observable.
            self.incdMarksEpidemic = False
            self.surveyPeriod = 0  # denoting the survey period before now
            self.simTimeIndexWhenEpidemicStarted = 0

            # if the duration of warm-up period is zero, then the warm-up period has already ended.
            if self.nDeltaTsInWarmUpPeriod == 0:
                self.simTimePassedWarmUp = True
                self.epiTimePassedWarmUp = True
        else:
            self.surveyPeriod = None
            self.simTimeIndexWhenEpidemicStarted = None

    def record_sim_time_period(self, sim_time_index):
        """ records the simulation time and simulation period. """

        self.simTimesAndSimPeriods.append([sim_time_index*self.deltaT, self.simPeriod])
        self.simPeriod += 1

    def record_survey_time(self, sim_time_index):

        # record true current epidemic time
        # (it is None if the first nonzero observations for outcomes
        # that mark the start of the epidemic has not been obtained)
        epi_time_index = self.get_epidemic_time_index(sim_time_index=sim_time_index)

        if self.epidemicStarted:

            self.surveyPeriod += 1

            if self.incdMarksEpidemic:
                # if we observe an incidence during period [t1, t2], we assume
                # that the epidemic has started at time t1.
                epi_time = (epi_time_index - self.nDeltaTsInSurveyPeriods) * self.deltaT
                #self.surveyTimesAndSurveyPeriods[-1][0] = epi_time
                self.surveyTimesAndSurveyPeriods.append([epi_time, self.surveyPeriod])

            else:  # if observing prevalence marks the start of the epidemic
                epi_time = epi_time_index * self.deltaT
                self.surveyTimesAndSurveyPeriods.append([epi_time, self.surveyPeriod])
        else:
            self.surveyTimesAndSurveyPeriods.append([None, None])

    def announce_start_of_epidemic(self, sim_time_index):

        # find if this marked the start of the epidemic
        if not self.epidemicStarted:

            self.epidemicStarted = True
            self.surveyPeriod = 0

            if self.incdMarksEpidemic:
                # if we observe an incidence during period [t1, t2], we assume
                # that the epidemic has started at time t1.
                self.simTimeIndexWhenEpidemicStarted = max(sim_time_index - self.nDeltaTsInSurveyPeriods, 0)
            else:
                self.simTimeIndexWhenEpidemicStarted = sim_time_index

    def get_epidemic_time_index(self, sim_time_index):
        """ :returns current epidemic time index (None if epidemic has not yet started) """

        if self.surveyPeriod is None:
            return None
        else:
            return sim_time_index - self.simTimeIndexWhenEpidemicStarted

    def get_epidemic_time(self, sim_time_index):
        """:returns the current epidemic time (None if epidemic has not yet started)"""

        if self.surveyPeriod is None:
            return None
        else:
            return self.get_epidemic_time_index(sim_time_index=sim_time_index) * self.deltaT

    def get_if_sim_time_passed_warm_up_period(self, sim_time_index):
        """ :returns True if the simulation time has passed th warm-up period """

        if self.simTimePassedWarmUp:
            return True
        else:
            if sim_time_index >= self.nDeltaTsInWarmUpPeriod:
                self.simTimePassedWarmUp = True
                return True
            else:
                return False

    def get_if_epi_time_passed_warm_up_period(self, sim_time_index):
        """ :returns True if the epidemic time has passed th warm-up period """

        if self.epiTimePassedWarmUp:
            return True
        else:
            # if epidemic has not started yet
            if self.surveyPeriod is None:
                return False
            else:
                t = self.get_epidemic_time_index(sim_time_index)
                if t >= self.nDeltaTsInWarmUpPeriod:
                    self.epiTimePassedWarmUp = True
                    return True
                else:
                    return False


class EpiHistory:
    """ to collect the history of a simulated epidemic"""

    def __init__(self, compartments,
                 chance_nodes=(), queue_compartments=(),
                 list_of_sum_time_series=(), list_of_ratio_time_series=(),
                 features=(), conditions=()):

        self.compartments = compartments
        self.chanceNodes = chance_nodes
        self.queueCompartments = queue_compartments
        self.nodesWithSurveillance = []

        # order sum-time series so that that incidence sum time-series are first
        # this is to make sure that when epidemic is detected, the surveillance on other
        # time-series are recorded correctly
        self.sumTimeSeries = []
        without_detection_ability = []
        for s in list_of_sum_time_series:
            if isinstance(s, SumIncidence) \
                    and s.surveillance is not None \
                    and s.surveillance.firstNoneZeroObsMarksStartOfEpidemic:
                self.sumTimeSeries.append(s)
            else:
                without_detection_ability.append(s)

        self.sumTimeSeries.extend(without_detection_ability)

        self.ratioTimeSeries = list_of_ratio_time_series
        self.features = features
        self.conditions = conditions
        self.timeMonitor = None

        # find if any output is being surveyed
        self.ifAnySurveillance = False  # if any output is being surveyed
        for s in self.sumTimeSeries:
            if s.surveillance:
                self.ifAnySurveillance = True
                break
        if not self.ifAnySurveillance:
            for r in self.ratioTimeSeries:
                if r.ifSurveyed:
                    self.ifAnySurveillance = True
                    break

    def reset(self, if_clear_series):

        for s in self.sumTimeSeries:
            s.reset()
        for r in self.ratioTimeSeries:
            r.reset()
        for f in self.features:
            f.reset()
        for c in self.conditions:
            c.reset()

        if if_clear_series:
            self.sumTimeSeries.clear()
            self.ratioTimeSeries.clear()
            self.features.clear()
            self.conditions.clear()

        self.timeMonitor.reset()

    def populate(self, delta_t, n_deltats_in_survey_periods, n_deltats_in_warm_up_period):

        # find the compartments that are collecting surveillance
        self.nodesWithSurveillance = []
        for n in self.compartments:
            if n.history is not None and n.history.if_collecting_any_surveillance():
                self.nodesWithSurveillance.append(n)
        for n in self.chanceNodes:
            if n.history is not None and n.history.if_collecting_any_surveillance():
                self.nodesWithSurveillance.append(n)
        for n in self.queueCompartments:
            if n.history is not None and n.history.if_collecting_any_surveillance():
                self.nodesWithSurveillance.append(n)

        # check if the start of epidemic is conditional on the first non-zero observation of a time-series
        # if not, we assume that the epidemic has started
        epi_started = True
        for s in self.sumTimeSeries:
            if s.firstNonZeroObsMarksStartOfEpidemic:
                epi_started = False
                break

        self.timeMonitor = TimeMonitor(
            delta_t=delta_t,
            epidemic_started=epi_started,
            incidence_marks_start_of_epidemic=True,  # for now we are assuming that only
            # observing incidence time-series marks the start of an epidemic
            n_deltats_in_survey_periods=n_deltats_in_survey_periods,
            n_deltats_in_warm_up_period=n_deltats_in_warm_up_period
        )

        # assign the time monitor to sum time-series with surveillance
        for s in self.sumTimeSeries:
            s.timeMonitor = self.timeMonitor
            if s.surveillance is not None:
                s.surveillance.timeMonitor = self.timeMonitor

    def record_sim_outputs(self, sim_time_index):
        """ record simulation outputs (to be called at the beginning of each simulation output period)
        :returns True if no feasibility condition is violated (and False otherwise)
        """

        self.timeMonitor.record_sim_time_period(sim_time_index=sim_time_index)
        epi_time = self.timeMonitor.get_epidemic_time(sim_time_index=sim_time_index)

        # record history of each compartment
        for c in self.compartments:
            c.record_history()
        for c in self.chanceNodes:
            c.record_history()
        for c in self.queueCompartments:
            c.record_history()

        # record history of summation time-series and check if feasibility conditions are violated.
        feasible_epi = True
        for s in self.sumTimeSeries:
            feasible = s.record_sim_output(epi_time=epi_time)
            if not feasible:
                feasible_epi = False
        for r in self.ratioTimeSeries:
            feasible = r.record_sim_output(epi_time=epi_time)
            if not feasible:
                feasible_epi = False

        return feasible_epi

    def update_incd_of_sum_time_series(self, sim_time_index):
        """ updates the incidence of incidence summation time series
        (to be called at each simulation time step) """

        # record history of summation time series
        for s in self.sumTimeSeries:
            s.update_incd(sim_time_index)

    def record_surveillance(self, sim_time_index, delta_t, noise_rng):
        """ records the surveillance of outcomes, features, and conditions
        (to be called at each observation period) """

        if_epi_started = self.timeMonitor.epidemicStarted
        if_warm_up_passed = self.timeMonitor.get_if_epi_time_passed_warm_up_period(sim_time_index=sim_time_index)

        # compartments, chance nodes, queue compartments with surveillance
        for c in self.nodesWithSurveillance:
            c.history.record_surveillance(if_epidemic_started=if_epi_started)

        # update surveillance (and will update whether epidemic has started)
        for s in self.sumTimeSeries:
            s.record_surveillance(sim_time_index=sim_time_index)

        for r in self.ratioTimeSeries:
            r.record_surveillance(if_epidemic_started=if_epi_started,
                                  noise_rng=noise_rng,
                                  warmup_ended=if_warm_up_passed)

        # update survey period and epidemic time
        self.timeMonitor.record_survey_time(sim_time_index=sim_time_index)
        epi_time = self.timeMonitor.get_epidemic_time(sim_time_index=sim_time_index)

        # update features
        for f in self.features:
            f.update(epi_time=epi_time)
        # update conditions
        for c in self.conditions:
            c.update()

    def calculate_lnl(self):
        """
        :returns (lnl, message) where lnl is the log likelihood of this time-series and
                                    message is the message provided when calculating lnl. """

        lnl = 0
        message = ''
        for r in self.ratioTimeSeries:
            if r.calibRatios is not None:
                v, m = r.calculate_lnl()
                lnl += v
                message += r.name + '-' + str(m) + '|'
        return lnl, message

    def get_dic_of_projected_outcomes(self):
        """
        :return: (dictionary) with the names of sum time-series as keys
                and the outcomes projected after warmup as values
        """

        dic = dict()
        for s in self.sumTimeSeries:
            if isinstance(s, SumIncidence):

                # cumulative incidence after simulation warm-up
                if s.collectCumAfterSimWarmUp:
                    dic[s.name + ' (after simulation warm-up)'] = s.cumIncdAfterWarmUp

                # cumulative incidence after epidemic warm-up
                surv = s.surveillance
                if surv is not None and surv.collectCumulativeAfterWarmUp:
                    dic[s.name + ' (after epidemic warm-up)'] = surv.cumIncdAfterWarmUp

        for r in self.ratioTimeSeries:
            if r.stat is not None:
                dic[r.name + ' (average incidence after epidemic warm-up)'] = r.stat.get_projected_ave_incd()

        return dic

    def clean_memory(self):

        self.timeMonitor.simTimesAndSimPeriods.clear()
        self.timeMonitor.surveyTimesAndSurveyPeriods.clear()
        for s in self.sumTimeSeries:
            s.reset()


class CompartmentSimHistory:
    """ class to collect the history of a compartment """

    def __init__(self, collect_prev=False, collect_incd=False, collect_cum_incd=False):
        """
        :param collect_prev: (bool) set to True to collect prevalence
        :param collect_incd: (bool) set to True to collect incidence
        :param collect_cum_incd: (bool) set to True to collect cumulative incidence
        """

        self.prevSeries = None      # prevalence time-series
        self.incdSeries = None      # incidence time-series
        self.cumIncdSeries = None   # cumulative incidence time-series
        self.cumIncd = 0            # cumulative incidence

        self.surveyedPrevSeries = None  # surveyed prevalence time-series
        self.surveyedIncdSeries = None   # surveyed incidence time series
        self.surveyedCumIncdSeries = None   # surveyed cumulative incidence time-series

        if collect_prev:
            self.prevSeries = []
        if collect_incd:
            self.incdSeries = IncidenceTimeSeries()
        if collect_cum_incd:
            self.cumIncdSeries = []
            self.cumIncd = 0

    def reset(self):

        self.cumIncd = 0
        if self.prevSeries is not None:
            self.prevSeries.clear()
        if self.incdSeries is not None:
            self.incdSeries.reset()
        if self.cumIncdSeries is not None:
            self.cumIncdSeries.clear()

        if self.surveyedPrevSeries is not None:
            self.surveyedPrevSeries.reset()
        if self.surveyedIncdSeries is not None:
            self.surveyedIncdSeries.reset()
        if self.surveyedCumIncdSeries is not None:
            self.surveyedCumIncdSeries.reset()

    def update_incd(self, n):
        """ update incidence of this simulation output period
        :param n: new incidence
        """

        if self.incdSeries is not None:
            self.incdSeries.update_incd(added_value=n)

        if self.surveyedIncdSeries is not None:
            self.surveyedIncdSeries.update_incd(added_value=n)

        if self.cumIncdSeries is not None:
            self.cumIncd += n

    def record_sim_output(self, prev):
        """ record the current prevalence, incidence, and cumulative incidence
            (to be called at the beginning of each simulation output period)
        :param prev: current prevalence
        """

        if self.prevSeries is not None:
            self.prevSeries.append(prev)

        if self.incdSeries is not None:
            self.incdSeries.record()

        if self.cumIncdSeries is not None:
            self.cumIncdSeries.append(self.cumIncd)

    def record_surveillance(self, if_epidemic_started):
        """ records the surveillance of outcomes (to be called at each observation period) """

        if self.surveyedPrevSeries is not None:
            self.surveyedPrevSeries.record(if_epidemic_started=if_epidemic_started)

        if self.surveyedIncdSeries is not None:
            self.surveyedIncdSeries.record(if_epidemic_started=if_epidemic_started)

        if self.surveyedCumIncdSeries is not None:
            self.surveyedCumIncdSeries.record(if_epidemic_started=if_epidemic_started)

    def if_collecting_any_surveillance(self):

        result = False
        if self.surveyedPrevSeries is not None:
            result = True
        elif self.surveyedIncdSeries is not None:
            result = True
        elif self.surveyedCumIncdSeries is not None:
            result = True

        return result
