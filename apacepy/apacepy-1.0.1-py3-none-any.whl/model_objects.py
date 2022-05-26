from deampy.parameters import _Parameter, Constant
from numpy import exp

from apacepy.econ_eval import CostHealthOverDeltaT
from apacepy.history import CompartmentSimHistory
from apacepy.time_series import SumPrevalence, IncidenceTimeSeries


class _Node:

    def __init__(self, name):
        """
        :param name: (string) name of the compartment
        """
        self.name = name
        self.sizePar = None
        self.size = 0           # current size
        self.ifEmptyToEradicate = False  # if should be empty for the spread to stop
        self.n_delta_t_incoming = 0     # over this simulation time-step
        self.n_past_delta_t_incoming = 0  # over the past simulation time-step
        self.deltaT = None
        self.history = None     # history of this compartment during simulation
        self.healthCostOverDeltaT = None    # to collect health anc cost outcome over a deltaT

    def reset(self):
        self.size = 0
        self.n_delta_t_incoming = 0
        self.n_past_delta_t_incoming = 0
        if self.history is not None:
            self.history.reset()

    def setup_history(self, collect_prev=False, collect_incd=False, collect_cum_incd=False):
        """ to specify which part of history (prevalence, incidence, accumulated incidence) to collect """

        if isinstance(self, ChanceNode) and collect_prev:
            raise ValueError('Prevalence is not defined for Chance Nodes.')
        if isinstance(self, DeathCompartment) and collect_prev:
            raise ValueError('Prevalence is not defined for Death Nodes.')

        self.history = CompartmentSimHistory(
            collect_prev=collect_prev, collect_incd=collect_incd, collect_cum_incd=collect_cum_incd)

    def add_and_get_time_series(self, time_series_type):
        """ returns the time-series of the specified type
        :param time_series_type: 'prev', 'incd', or 'cum-incd'
        :return: (list) the time-series of prevalence, incidence, or cumulative incidence
        """

        if time_series_type == 'prev':
            if self.history is None:
                self.setup_history(collect_prev=True)
            elif self.history.prevSeries is None:
                self.history.prevSeries = []
            return self.history.prevSeries

        elif time_series_type == 'incd':
            if self.history is None:
                self.setup_history(collect_incd=True)
            elif self.history.incdSeries is None:
                self.history.incdSeries = IncidenceTimeSeries()
            return self.history.incdSeries.timeSeries

        elif time_series_type == 'cum-incd':
            if self.history is None:
                self.setup_history(collect_cum_incd=True)
            elif self.history.cumIncdSeries is None:
                self.history.cumIncdSeries = []
            return self.history.cumIncdSeries

        else:
            raise ValueError('Invalid time-series type.')

    def setup_econ_outcome(self, par_health_per_new_member=None, par_cost_per_new_member=None,
                           par_health_per_unit_of_time=None, par_cost_per_unit_of_time=None):
        """ to specify which cost and health outcomes to collect
        :param par_health_per_new_member: (Parameter) of the change in health per new member
        :param par_cost_per_new_member: (Parameter) of the cost incurred per per new member
        :param par_health_per_unit_of_time: (Parameter) of the change in health that is sustained over time
        :param par_cost_per_unit_of_time: (Parameter) of the cost that is continuously incurred
        """

        if isinstance(self, ChanceNode):
            if par_health_per_unit_of_time is not None:
                raise ValueError(
                    "Error in '{0}'. Chance nodes cannot collect health per unit of time.".format(self.name))
            if par_cost_per_unit_of_time is not None:
                raise ValueError(
                    "Error in '{0}'. Chance nodes cannot collect cost per unit of time.".format(self.name))

        self.healthCostOverDeltaT = CostHealthOverDeltaT(
            par_health_per_new_member=par_health_per_new_member,
            par_cost_per_new_member=par_cost_per_new_member,
            par_health_per_unit_of_time=par_health_per_unit_of_time,
            par_cost_per_unit_of_time=par_cost_per_unit_of_time
        )

    def initialize(self, delta_t):
        """ initialize this compartment
        :param delta_t: (double) simulation time step
        """

        if self.sizePar is not None:
            self.size = int(self.sizePar.value)
            assert self.size >= 0, 'Size of {} cannot be less than 0.'.format(self.name)

        self.deltaT = delta_t
        if self.healthCostOverDeltaT:
            self.healthCostOverDeltaT.deltaT = delta_t

    def receive_delta_t_incoming(self):
        """ update the compartment size based on the number of incoming members """

        if self.history:
            self.history.update_incd(n=self.n_delta_t_incoming)

        if self.n_delta_t_incoming == 0:
            return

        self.size += self.n_delta_t_incoming
        self.n_past_delta_t_incoming += self.n_delta_t_incoming

        self.n_delta_t_incoming = 0

    def record_history(self):
        """ record the history (prevalence, incidence, accumulative incidence) at this moment """

        if self.history:
            self.history.record_sim_output(prev=self.size)

    def sample_outgoing(self, rng):
        """ finds the number of members existing this compartment """


class Compartment(_Node):

    def __init__(self, name, size_par=None, if_empty_to_eradicate=False,
                 susceptibility_params=None, infectivity_params=None,
                 row_index_contact_matrix=None, num_of_pathogens=None):
        """
        :param name: (string) name of the compartment
        :param size_par: (Parameter) parameter for the initial size of this compartment
        :param if_empty_to_eradicate: (bool) set to True for compartments that should be empty for the disease
            to be eradicated.
        :param susceptibility_params: (Parameter or list of Parameter)
            susceptibility parameters (will assume 0 if not provided)
        :param infectivity_params: (Parameter or list of Parameter)
            infectivity parameters (will assume 0 if not provided)
        :param row_index_contact_matrix: (int) row index in the contact matrix
        :param num_of_pathogens: (int) number of pathogens
        """

        # find the number of pathogens
        n = 1
        if susceptibility_params is not None:
            if isinstance(susceptibility_params, _Parameter):
                susceptibility_params = [susceptibility_params]
            n = len(susceptibility_params)
        if infectivity_params is not None:
            if isinstance(infectivity_params, _Parameter):
                infectivity_params = [infectivity_params]
            n = max(n, len(infectivity_params))
        
        if susceptibility_params is None and infectivity_params is None:
            if num_of_pathogens is None:
                num_of_pathogens = 1
            n = num_of_pathogens
        
        if size_par is None:
            size_par = Constant(value=0)
        if susceptibility_params is None:
            susceptibility_params = [Constant(value=0)] * n
        if infectivity_params is None:
            infectivity_params = [Constant(value=0)] * n
        if row_index_contact_matrix is None:
            row_index_contact_matrix = 0

        assert isinstance(size_par, _Parameter)
        for p in susceptibility_params:
            assert isinstance(p, _Parameter)
        for p in infectivity_params:
            assert isinstance(p, _Parameter)

        _Node.__init__(self, name)
        self.sizePar = size_par
        self.epiDepEvents = []
        self.epiIndEvents = []
        self.poissonEvents = []
        self.ifEmptyToEradicate = if_empty_to_eradicate
        self.susParams = susceptibility_params
        self.infParams = infectivity_params
        self.idxContactMatrix = row_index_contact_matrix

    def add_event(self, event):
        """ attache an epidemic event to this compartment
        :param event (EpiDepEvent, EpiIndepEvent, PoissonEvent)
        """

        assert isinstance(event, _EpiEvent)

        if isinstance(event, EpiIndepEvent):
            self.epiIndEvents.append(event)
        elif isinstance(event, EpiDepEvent):
            self.epiDepEvents.append(event)
        elif isinstance(event, PoissonEvent):
            self.poissonEvents.append(event)
        else:
            raise ValueError('Invalid event type.')

    def add_events(self, events):
        """ attache epidemic events to this compartment
        :param events (list) of (EpiDepEvent, EpiIndepEvent, PoissonEvent)
        """
        assert isinstance(events, list)

        for e in events:
            self.add_event(event=e)

    def sample_outgoing(self, rng):
        """ finds the number of members existing this compartment """

        # find numbers out of poisson events
        # (this should be processed regardless of the current size of this compartment)
        for e in self.poissonEvents:
            e.destComp.n_delta_t_incoming += rng.poisson(e.get_rate() * self.deltaT)

        if self.size == 0:
            return

        self._sample_outgoing(rng=rng)

    def _sample_outgoing(self, rng):

        rates_out = []
        sum_rates = 0
        # for epidemic dependent event
        for e in self.epiDepEvents:
            if e.intervToActivate is None or e.intervToActivate.switchValue == 1:
                rates_out.append(e.get_rate())
                sum_rates += rates_out[-1]
        # for epidemic independent events
        for e in self.epiIndEvents:
            if e.intervToActivate is None or e.intervToActivate.switchValue == 1:
                rates_out.append(e.get_rate())
                sum_rates += rates_out[-1]

        # find numbers out of competing events
        if sum_rates > 0:
            # at position 0 put the probability of staying in this compartment
            try:
                probs_out = [exp(-sum_rates * self.deltaT)]
            except FloatingPointError:
                probs_out = [0]

            # probability of leaving due to event i is
            # (prob of leaving due to any event) * rate_i / sum(rate_i)
            coeff = (1 - probs_out[0]) / sum_rates
            for rate in rates_out:
                probs_out.append(coeff * rate)

            outs = rng.multinomial(self.size, probs_out)

            i = 1
            for e in self.epiDepEvents:
                if e.intervToActivate is None or e.intervToActivate.switchValue == 1:
                    self.epiDepEvents[i-1].destComp.n_delta_t_incoming += outs[i]
                    self.size -= outs[i]
                    i += 1
            for e in self.epiIndEvents:
                if e.intervToActivate is None or e.intervToActivate.switchValue == 1:
                    e.destComp.n_delta_t_incoming += outs[i]
                    self.size -= outs[i]
                    i += 1


class ChanceNode(_Node):
    def __init__(self, name, destination_compartments, probability_params):
        """
        :param name: (string) name of the compartment
        :param destination_compartments: (list) destination compartments attached to this chance node
        :param probability_params: (Parameter or a Dirichlet distribution)
            if destination_compartments contains 2 compartments, probability_param is the probability of moving
                to the first compartment;
            if destination_compartments contains more than 2 compartments,  then probability_param is
                a Constant distribution (with list of probabilities as value) or a Dirichlet distribution.
        """
        _Node.__init__(self, name)

        assert isinstance(destination_compartments, list)
        assert isinstance(probability_params, _Parameter)
        if type(self) == ChanceNode:
            for c in destination_compartments:
                assert c is not None, 'Destination compartments cannot be None.'

        self.destComps = destination_compartments
        self.probParam = probability_params

    def sample_outgoing(self, rng):
        """ finds the number of members existing this chance node """

        if self.size == 0:
            return

        if len(self.destComps) == 2:

            if self.probParam.value < 0 or self.probParam.value > 1:
                raise ValueError("Invalid value ({}) for the probability of success in ChanceNode '{}'"
                                 .format(self.probParam.value, self.name))

            if self.probParam.value == 1:
                self.destComps[0].n_delta_t_incoming += self.size
            elif self.probParam.value == 0:
                self.destComps[1].n_delta_t_incoming += self.size
            else:
                out_to_first = rng.binomial(self.size, self.probParam.value)
                self.destComps[0].n_delta_t_incoming += out_to_first
                self.destComps[1].n_delta_t_incoming += self.size - out_to_first

            self.size = 0
        else:
            outs = rng.multinomial(self.size, self.probParam.value)
            for i, c in enumerate(self.destComps):
                c.n_delta_t_incoming += outs[i]
                self.size -= outs[i]


class Counter(ChanceNode):
    def __init__(self, name, destination_compartment):
        """
        :param name: (string) name of the compartment
        :param destination_compartment: (Compartment) destination compartment
        """

        ChanceNode.__init__(self, name=name,
                            destination_compartments=[destination_compartment, None],
                            probability_params=Constant(1))


class Capacity:
    def __init__(self, capacity_param, consumption_prevalence):
        """
        :param capacity_param: (Parameter) of maximum capacity available
        :param consumption_prevalence: (SumPrevalence) representing the current capacity occupied
        """
        assert isinstance(capacity_param, _Parameter)
        assert isinstance(consumption_prevalence, SumPrevalence)

        self.capacityParam = capacity_param  # maximum capacity
        self.consumptionPrev = consumption_prevalence
        self.realTimeCapacity = 0   # real-time capacity

    def update_realtime_capacity(self):

        self.realTimeCapacity = max(self.capacityParam.value - self.consumptionPrev.timeSeries[-1], 0)


class QueueCompartment(Compartment):
    def __init__(self, name, destination_if_capacity_available, capacity,
                 size_par=None, if_empty_to_eradicate=False,
                 susceptibility_params=None, infectivity_params=None, row_index_contact_matrix=None):
        """
        :param name: (string) name of the compartment
        :param destination_if_capacity_available: compartment or chance node to move if enough capacity is available
        :param size_par: (Parameter) parameter for the initial size of this compartment
        :param if_empty_to_eradicate: (bool) set to True for compartments that should be empty for the disease
            to be eradicated.
        :param susceptibility_params: (Parameter or list of Parameter)
            susceptibility parameters (will assume 0 if not provided)
        :param infectivity_params: (Parameter or list of Parameter)
            infectivity parameters (will assume 0 if not provided)
        :param row_index_contact_matrix: (int) row index in the contact matrix
        """
        Compartment.__init__(self, name=name, size_par=size_par, if_empty_to_eradicate=if_empty_to_eradicate,
                             susceptibility_params=susceptibility_params, infectivity_params=infectivity_params,
                             row_index_contact_matrix=row_index_contact_matrix)

        assert isinstance(capacity, Capacity)

        self.destCapacityAvailable = destination_if_capacity_available
        self.capacity = capacity

    def update_capacity(self):
        """ to be called at the beginning of each simulation time step """

        self.capacity.update_realtime_capacity()

    def sample_outgoing(self, rng):
        """ finds the number of members existing this chance node """

        if self.size == 0:
            return

        # available capacity = max capacity - currently used
        if self.capacity.realTimeCapacity > 0:
            served = min(self.capacity.realTimeCapacity, self.size)
            self.destCapacityAvailable.n_delta_t_incoming += served
            self.capacity.realTimeCapacity -= served
            self.size -= served

        # determine what happens to the remaining members
        if self.size > 0:
            self._sample_outgoing(rng=rng)


class DeathCompartment(_Node):

    def __init__(self, name):
        _Node.__init__(self, name=name)

    def sample_outgoing(self, rng):
        """ this is only to make sure the size of death compartment remains 0 """

        self.size = 0


class _EpiEvent:
    """ epidemic event to move an individuals from one compartment to another"""

    def __init__(self, name, dest_comp, interv_to_activate=None):

        assert isinstance(dest_comp, _Node),\
            "For event '{}', destination should be a compartment or a chance node, '{}' is provided instead"\
                .format(name, type(dest_comp))

        self.name = name
        self.destComp = dest_comp
        self.intervToActivate = interv_to_activate

    def set_rate(self, value):
        pass

    def get_rate(self):
        pass


class EpiDepEvent(_EpiEvent):
    """ epidemic dependent event """

    def __init__(self, name, destination, generating_pathogen=None, interv_to_activate=None):
        """
        :param name: (string) name of this event
        :param destination: (Compartment) destination compartment
        :param generating_pathogen: (int: 0, 1, ...) id of the generating pathogen
                (for when multiple pathogens are being modelled)
        :param interv_to_activate: (Intervention) intervention that activates this event
        """

        _EpiEvent.__init__(self, name=name,
                           dest_comp=destination,
                           interv_to_activate=interv_to_activate)

        self.rate = 0
        if generating_pathogen is None:
            self.generatingPathogen = 0
        else:
            self.generatingPathogen = generating_pathogen

    def set_rate(self, value):
        self.rate = value

    def get_rate(self):
        return self.rate


class EpiIndepEvent(_EpiEvent):
    """ epidemic independent event """

    def __init__(self, name, destination, rate_param, interv_to_activate=None):
        """
        :param name: (string) name of this event
        :param destination: (Compartment) destination compartment
        :param rate_param: (Parameter) rate parameter of this event
        :param interv_to_activate: (Intervention) intervention that activates this event
        """

        assert isinstance(rate_param, _Parameter),\
            "For event '{}', rate_param should be a parameter, '{}' is provided instead"\
                .format(name, type(rate_param))

        _EpiEvent.__init__(self, name=name,
                           dest_comp=destination,
                           interv_to_activate=interv_to_activate)
        self.ratePar = rate_param

    def get_rate(self):
        return self.ratePar.value


class PoissonEvent(_EpiEvent):

    def __init__(self, name, destination, rate_param):
        """
        :param name: (string) name of this event
        :param destination: (Compartment) destination compartment
        :param rate_param: (Parameter) rate parameter of this event
        """

        assert isinstance(rate_param, _Parameter),\
            "For event '{}', rate_param should be a parameter, '{}' is provided instead"\
                .format(name, type(rate_param))

        _EpiEvent.__init__(self, name, destination)
        self.ratePar = rate_param

    def get_rate(self):
        return self.ratePar.value
