import time

import numpy as np
from deampy.discrete_event_sim import SimulationCalendar
from deampy.parameters import _Parameter, MatrixOfParams
from numpy import iinfo, int32
from numpy.random import RandomState

from apacepy.control import DecisionMaker
from apacepy.econ_eval import CostHealthOverEpidemic
from apacepy.history import EpiHistory
from apacepy.inputs import ModelSettings, EpiParameters
from apacepy.model_objects import Compartment, ChanceNode, QueueCompartment
from apacepy.sim_events import UpdateCompartments, RecordSimHistory, \
    RecordObservedHistory, CollectCostHealth, MakeDecisions, EndOfSim
from apacepy.support import export_trajectories
from apacepy.time_series import _SumTimeSeries, RatioTimeSeries
from apacepy.transmission import FOIModel


class EpiModel:
    def __init__(self, id, settings):
        """
        :param id: (int) id of this epidemic model
        :param settings: (ModelSettings) model settings
        """

        assert isinstance(settings, ModelSettings)

        self.id = id
        self.seed = None
        self.rng = None
        self.nTrajsDiscarded = 0
        self.noiseRNG = None
        self.settings = settings
        self.simCal = SimulationCalendar()
        self.compartments = None
        self.chanceNodes = None
        self.queueCompartments = None
        self.params = None
        self.parBaseContactMatrix = None
        self.FOIModel = None
        self.decisionMaker = None
        self.ifEradicated = False

        self.epiHistory = None
        self.ifAFeasibleTraj = True
        self.lnl = None, ''     # (log of likelihood of this trajectory, explanation)

        self.econEval = None
        self.runTime = None  # simulation run time

    def populate(self, compartments, parameters, param_base_contact_matrix=None,
                 chance_nodes=None, queue_compartments=None,
                 list_of_sum_time_series=None, list_of_ratio_time_series=None,
                 interventions=None, features=None, conditions=None):
        """
        :param compartments: (list) of compartment
        :param parameters: (EpiParameters) model parameters
        :param param_base_contact_matrix: (Parameter) the parameter representing the base contact matrix
        :param chance_nodes: (list) of chance nodes
        :param queue_compartments: (list) of queue compartments
        :param list_of_sum_time_series: (list) of summation time series defined on compartments
        :param list_of_ratio_time_series: (list) of ratio time series
        :param interventions: (list) of interventions
        :param features: (list) of Features
        :param conditions: (list) of Conditions
        """
        assert isinstance(parameters, EpiParameters)
        assert isinstance(parameters.dictOfParams, dict), \
            'parameters should be stored in a dictionary.'

        # asserting the type of chance nodes
        if chance_nodes is None:
            chance_nodes = []
        else:
            assert all(isinstance(c, ChanceNode) for c in chance_nodes), \
                'One of the chance nodes provided is not a chance node.'
        # asserting the type of queue compartments
        if queue_compartments is None:
            queue_compartments = []
        else:
            assert all(isinstance(c, QueueCompartment) for c in queue_compartments), \
                'One of the queue compartments provided is a queue compartment.'
        # asserting the type of sum time-series
        if list_of_sum_time_series is None:
            list_of_sum_time_series = []
        else:
            assert all(isinstance(c, _SumTimeSeries) for c in list_of_sum_time_series), \
                'One of the sum time-series provided is not a sum time-series.'
        # asserting the type of ratio time-series
        if list_of_ratio_time_series is None:
            list_of_ratio_time_series = []
        else:
            assert all(isinstance(c, RatioTimeSeries) for c in list_of_ratio_time_series), \
                'One of the ratio time-series provided is not a ratio time-series.'

        if interventions is None:
            interventions = []
        if features is None:
            features = []
        if conditions is None:
            conditions = []

        self.compartments = compartments
        self.params = parameters
        self.chanceNodes = chance_nodes
        self.queueCompartments = queue_compartments

        # initialize input
        self.settings.initialize()

        # if base contact matrix is not provided, we assume it is a 1 by 1 matrix with its entity to be 1.
        if param_base_contact_matrix is None:
            self.parBaseContactMatrix = MatrixOfParams(matrix_of_params_or_values=[[1]])
        else:
            assert isinstance(param_base_contact_matrix, _Parameter)
            self.parBaseContactMatrix = param_base_contact_matrix

        # epidemic history
        self.epiHistory = EpiHistory(compartments=compartments,
                                     chance_nodes=chance_nodes,
                                     queue_compartments=queue_compartments,
                                     list_of_sum_time_series=list_of_sum_time_series,
                                     list_of_ratio_time_series=list_of_ratio_time_series,
                                     features=features,
                                     conditions=conditions)
        # initialize history
        self.epiHistory.populate(delta_t=self.settings.deltaT,
                                 n_deltats_in_survey_periods=self.settings.nDeltaTsInObsPeriod,
                                 n_deltats_in_warm_up_period=self.settings.nDeltaTsInWarmUpPeriod)

        # decision maker
        self.decisionMaker = DecisionMaker(interventions=interventions, epi_history=self.epiHistory)

        # economic evaluation collector
        if self.settings.collectEconEval:
            self.econEval = CostHealthOverEpidemic(
                compartments=self.compartments,
                sum_time_series=self.epiHistory.sumTimeSeries,
                interventions=self.decisionMaker.interventions,
                delta_t_discount_rate=self.settings.deltaT*self.settings.annualDiscountRate)

        # set the delta_t of econ eval collectors assigned to sum time-series
        for s in self.epiHistory.sumTimeSeries:
            if s.healthCostOverDeltaT:
                s.healthCostOverDeltaT.deltaT = self.settings.deltaT

        # find time-dependent parameters
        self.params.list_time_dependent_params()

        # force of infection model
        foi_comparts = [c for c in self.compartments if isinstance(c, Compartment)]
        foi_comparts.extend(self.queueCompartments)

        self.FOIModel = FOIModel(par_base_contact_matrix=self.parBaseContactMatrix,
                                 compartments=foi_comparts)

    def reset(self):

        self.simCal.reset()
        for c in self.compartments:
            c.reset()
        for c in self.chanceNodes:
            c.reset()
        for c in self.queueCompartments:
            c.reset()
        self.params.reset()
        self.decisionMaker.reset()
        self.ifEradicated = False
        self.epiHistory.reset(if_clear_series=False)
        self.ifAFeasibleTraj = True
        self.lnl = None, ''
        if self.econEval is not None:
            self.econEval.reset()

    def __clean_memory_after_calibration_run(self):

        self.rng = None
        self.noiseRNG = None
        self.simCal.reset()
        for c in self.compartments:
            c.reset()
        for c in self.chanceNodes:
            c.reset()
        for c in self.queueCompartments:
            c.reset()
        self.decisionMaker.reset()
        self.epiHistory.reset(if_clear_series=True)
        if self.econEval is not None:
            self.econEval.reset()

    def __initialize(self):
        """ initialize the epidemic model """

        # reset (to clean up everything from the last simulation)
        self.reset()

        delta_t = self.settings.deltaT

        # sample all parameters
        self.params.sample_parameters(rng=self.rng, time=self.simCal.time*delta_t)

        # initialize compartments, chance nodes, and queue compartments
        for c in self.compartments:
            c.initialize(delta_t=delta_t)
        for c in self.chanceNodes:
            c.initialize(delta_t=delta_t)
        for c in self.queueCompartments:
            c.initialize(delta_t=delta_t)

        # schedule simulation events to record history and update compartments
        self.simCal.add_event(event=RecordSimHistory(time=0, epi_model=self))
        self.simCal.add_event(event=RecordObservedHistory(time=0, epi_model=self))
        if self.epiHistory.timeMonitor.epidemicStarted:
            self.simCal.add_event(event=MakeDecisions(time=self.settings.nDeltaTsToStartDecisionMaking, epi_model=self))
            self.simCal.add_event(event=EndOfSim(time=self.settings.nDeltaTsInSimulation, epi_model=self))

        if self.econEval is not None:
            self.simCal.add_event(event=CollectCostHealth(time=0, epi_model=self))
        self.simCal.add_event(event=UpdateCompartments(time=0, epi_model=self))

        # initialize interventions
        self.decisionMaker.initialize(delta_t=self.settings.deltaT, time_monitor=self.epiHistory.timeMonitor)

    def simulate(self, seed=None):
        """ simulate the epidemic model 
        :param seed: (int) random number seed
        """

        self.runTime = time.time()
        self.seed = self.id if seed is None else seed
        self.rng = RandomState(seed=self.seed)
        self.noiseRNG = RandomState(self.rng.randint(0, iinfo(int32).max))

        self.__initialize()

        while self.simCal.n_events() > 0:
            self.simCal.get_next_event().process()

        self.runTime = time.time() - self.runTime
        
    def simulate_until_a_feasible_traj(self, seed=None, max_tries=100):
        """ simulate until a feasible trajectory is found """
        
        rng = RandomState(seed=self.id if seed is None else seed)
        feasible_found = False
        self.nTrajsDiscarded = 0
        while not feasible_found and self.nTrajsDiscarded < max_tries:

            seed = rng.randint(0, iinfo(int32).max)
            self.simulate(seed)
            
            if self.ifAFeasibleTraj:
                feasible_found = True
            else:
                self.nTrajsDiscarded += 1

            if self.nTrajsDiscarded >= max_tries:
                self.ifAFeasibleTraj = False

    def process_end_of_sim(self):
        """ process the end of the simulation """

        if self.ifAFeasibleTraj and self.settings.calcLikelihood:
            for s in self.epiHistory.sumTimeSeries:
                if s.feasibleConditions:
                    if not s.feasibleConditions.ifMinThresholdHasReached:
                        self.ifAFeasibleTraj = False
            for r in self.epiHistory.ratioTimeSeries:
                if r.feasibleConditions:
                    if not r.feasibleConditions.ifMinThresholdHasReached:
                        self.ifAFeasibleTraj = False

        # update the utilization time of each intervention
        sim_time_index = self.simCal.time
        epi_time_index = self.epiHistory.timeMonitor.get_epidemic_time_index(
            sim_time_index=sim_time_index)
        for i in self.decisionMaker.interventions:
            i.update_time_in_use(sim_time_index=sim_time_index, epi_time_index=epi_time_index)

        # collect econ measures if epidemic has started
        if self.econEval is not None:
            t_index_epi_started = self.epiHistory.timeMonitor.simTimeIndexWhenEpidemicStarted
            if t_index_epi_started is not None:
                self.econEval.process_end_of_sim(
                    n_delta_t_warm_up=t_index_epi_started+self.settings.nDeltaTsInWarmUpPeriod,
                    n_delta_t_decision_period=self.settings.nDeltaTsInObsPeriod,
                    n_delta_ts_before_first_decision=self.settings.nDeltaTsToStartDecisionMaking)

        if self.settings.calcLikelihood:
            self.__calculate_likelihood()
            # self.__clean_memory_after_calibration_run()

        # clean the calendar
        self.simCal.clear_calendar()

    def update_compartments(self):
        """ updates compartment sizes
        """

        delta_t = self.settings.deltaT
        sim_time_index = self.simCal.time
        epi_time_index = self.epiHistory.timeMonitor.get_epidemic_time_index(sim_time_index=sim_time_index)
        epi_time = sim_time_index * delta_t if epi_time_index is not None else None

        # update time dependent parameters
        self.params.update_time_dependent_params(rng=self.rng, time=epi_time)

        # update transmission rates
        self.FOIModel.update_transmission_rates(interventions_in_effect=self.decisionMaker.interventionsInEffect)

        # reset past delta_t information
        for c in self.compartments:
            c.n_past_delta_t_incoming = 0
        for c in self.chanceNodes:
            c.n_past_delta_t_incoming = 0
        for c in self.queueCompartments:
            c.n_past_delta_t_incoming = 0
            c.update_capacity()

        # push members of normal compartments forward
        self._push_members_forward(nodes=self.compartments)

        continue_processing = True
        while continue_processing:
            continue_processing = False

            # process chance nodes
            if len(self.chanceNodes) > 0:
                self._push_members_forward(nodes=self.chanceNodes)
            # process queue compartments
            if len(self.queueCompartments) > 0:
                self._push_members_forward(nodes=self.queueCompartments)

            # find if there is any chance node with size > 0
            if len(self.chanceNodes) > 0:
                for c in self.chanceNodes:
                    if c.size > 0:
                        continue_processing = True
                        break
            # find if there is any chance node with size > 0
            if not continue_processing and len(self.queueCompartments) > 0:
                for c in self.queueCompartments:
                    if c.size > 0 and c.capacity.realTimeCapacity > 0:
                        continue_processing = True
                        break

        # update the incidence of summation time series
        self.epiHistory.update_incd_of_sum_time_series(sim_time_index=sim_time_index)

        # find if the disease is eradicated
        if self.settings.checkEradicationConditions:
            self._find_if_eradicated()

        # schedule the next time to update the compartments
        if not self.ifEradicated:
            self.simCal.add_event(
                event=UpdateCompartments(time=self.simCal.time + 1, epi_model=self))
        else:
            # schedule record sim history if it is not already schedule for next time index
            if (self.simCal.time + 1) % self.settings.nDeltaTsInSimOutputPeriod != 0:
                self.simCal.add_event(
                    event=RecordSimHistory(time=self.simCal.time + 1,  epi_model=self))

            # schedule record observed history if it is not already schedule for next time index
            if (self.simCal.time + 1) % self.settings.nDeltaTsInObsPeriod != 0:
                self.simCal.add_event(
                    event=RecordObservedHistory(time=self.simCal.time + 1,  epi_model=self))

            self.simCal.add_event(
                event=EndOfSim(time=self.simCal.time + 1, epi_model=self))

    def record_sim_outputs(self):
        """ records the simulation history up to now """

        # record simulation history
        if_feasible = self.epiHistory.record_sim_outputs(sim_time_index=self.simCal.time)

        # if not calibrating the model, the trajectory is feasible always
        if not self.settings.calcLikelihood:
            if_feasible = True

        self.decisionMaker.record_decision_during_this_sim_outputs()

        # terminates only when the goal is to calibrate the model
        if self.settings.calcLikelihood and not if_feasible:
            self.ifAFeasibleTraj = False
            if self.simCal.time < self.settings.nDeltaTsInSimulation and not self.ifEradicated:
                self.simCal.add_event(
                    event=EndOfSim(
                        time=self.simCal.time,
                        epi_model=self))

        # schedule the next record simulation history event
        elif not self.ifEradicated:
            self.simCal.add_event(
                event=RecordSimHistory(
                    time=self.simCal.time + self.settings.nDeltaTsInSimOutputPeriod,
                    epi_model=self))

    def record_surveillance(self):
        """ record the observed history up to now """

        # record observed history
        self.epiHistory.record_surveillance(sim_time_index=self.simCal.time,
                                            delta_t=self.settings.deltaT,
                                            noise_rng=self.noiseRNG)

        # store decision
        self.decisionMaker.record_decision_during_past_obs_period()

        # schedule a decision-making
        # if incidence marks the start of the epidemic and the first incident case is observed
        if self.epiHistory.timeMonitor.incdMarksEpidemic and self.epiHistory.timeMonitor.surveyPeriod == 1:
            if not self.ifEradicated:
                self.simCal.add_event(event=MakeDecisions(
                    time=self.settings.nDeltaTsToStartDecisionMaking + self.simCal.time,
                    epi_model=self))
                self.simCal.add_event(event=EndOfSim(
                    time=self.settings.nDeltaTsInSimulation + self.simCal.time,
                    epi_model=self))

        # schedule the next event to update observed history
        if not self.ifEradicated:
            self.simCal.add_event(
                event=RecordObservedHistory(
                    time=self.simCal.time + self.settings.nDeltaTsInObsPeriod,
                    epi_model=self))

    def collect_cost_health(self):
        """ collect cost and health outcomes """

        # if warm-up period has passed
        self.econEval.collect_cost_health(delta_t=self.settings.deltaT)

        # schedule the next time to update the compartments
        if not self.ifEradicated:
            self.simCal.add_event(
                event=CollectCostHealth(time=self.simCal.time + 1, epi_model=self))

    def make_decisions(self):

        # make a decision
        a_decision_made = self.decisionMaker.make_a_decision(sim_time_index=self.simCal.time)

        # schedule the next event to make decisions
        if not self.ifEradicated:
            self.simCal.add_event(
                event=MakeDecisions(
                    time=self.simCal.time + self.settings.nDeltaTsInObsPeriod,
                    epi_model=self))

    def _push_members_forward(self, nodes):

        # find number of outgoing members from each compartment
        for c in nodes:
            c.sample_outgoing(rng=self.rng)

        # update the size of each compartment
        for c in self.compartments:
            c.receive_delta_t_incoming()
        for c in self.chanceNodes:
            c.receive_delta_t_incoming()
        for c in self.queueCompartments:
            c.receive_delta_t_incoming()

    def _find_if_eradicated(self):
        """ finds if the disease is eradicated """

        if self.settings.checkEradicationConditions:
            if_erad = True
            for c in self.compartments:
                if c.ifEmptyToEradicate and c.size > 0:
                    if_erad = False
                    break

            if if_erad:
                for c in self.queueCompartments:
                    if c.ifEmptyToEradicate and c.size > 0:
                        if_erad = False
                        break

            self.ifEradicated = if_erad
        else:
            self.ifEradicated = False

    def __calculate_likelihood(self):

        if self.ifAFeasibleTraj:
            lnl, message = self.epiHistory.calculate_lnl()
            if message in ('', None):
                message = 'Feasible trajectory'
            self.lnl = lnl, message
        else:
            self.lnl = float('-inf'), 'Infeasible trajectory'

    def export_trajectories(self, folder=None, delete_existing_files=True):
        """ exports the current simulated epidemic into csv files """

        export_trajectories(
            id=self.id,
            seed=self.seed,
            epi_history=self.epiHistory,
            decision_maker=self.decisionMaker,
            folder_trajectories=self.settings.folderToSaveTrajs if folder is None else folder,
            delete_existing_files=delete_existing_files)

    def get_total_discounted_cost_and_health(self):
        """
        return: a dictionary of discounted cost and discounted health after the warm-up period
        """
        summary = 'Economic evaluation is off.'
        if self.econEval:
            summary = {'Discounted cost': self.econEval.totalDiscountedCostAfterWarmUp,
                       'Discounted health': self.econEval.totalDiscountedEffectAfterWarmUp}

        return summary

    def get_discounted_cost_over_decision_periods(self):
        """ :returns: (list) of cost over decision periods discounted to the present value"""
        return self.econEval.get_discounted_cost_over_decision_periods()

    def get_discounted_health_over_decision_periods(self):
        """ :returns: (list) of health estimates over decision periods discounted to the present value"""
        return self.econEval.get_discounted_health_over_decision_periods()

    def get_discounted_nmb_loss_over_decision_periods(self, wtp, health_multiplier=1, cost_multiplier=1):
        """ :returns: (list) of losses in net monetary benefits over decision periods discounted to the present value
        :param wtp: (float) willingness-to-pay value
        :param health_multiplier: (float) to multiply the health estimates by
        :param cost_multiplier: (float) to multiply the cost estimates by
        """

        # time index when the first decision made
        t_index_decision_making = self.settings.nDeltaTsToStartDecisionMaking \
                                  + self.epiHistory.timeMonitor.simTimeIndexWhenEpidemicStarted
        n = int(t_index_decision_making / self.settings.nDeltaTsInObsPeriod)

        q = np.array(self.get_discounted_health_over_decision_periods()) * health_multiplier
        c = np.array(self.get_discounted_cost_over_decision_periods()) * cost_multiplier
        result = wtp * q + c
        return result[n:]
