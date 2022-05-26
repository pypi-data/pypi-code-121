from deampy.discrete_event_sim import SimulationEvent as Event


""" priority of simulation events (low number implies higher priority)"""
# At each simulation time-step,
# first record the simulation history (priority 0)
# which allows calculating observed history (priority 1).
# Knowing the observed history, we can make decisions (priority 2),
# and then we can update the compartments over the current simulation period.
RECORD_SIM_HISTORY = 0
RECORD_OBS_HISTORY = 1
END_OF_SIM = 2
MAKE_DECISIONS = 3
UPDATE_COMPARTMENTS = 4
COLLECT_COST_HEALTH = 5


class EndOfSim(Event):
    """ event to end the simulation """
    def __init__(self, time, epi_model):
        Event.__init__(self, time, priority=END_OF_SIM)
        self.epiModel = epi_model

    def process(self, rng=None):
        self.epiModel.process_end_of_sim()


class UpdateCompartments(Event):
    """ event to update size of compartments """

    def __init__(self, time, epi_model):
        Event.__init__(self, time, priority=UPDATE_COMPARTMENTS)
        self.epiModel = epi_model

    def process(self, rng=None):
        self.epiModel.update_compartments()


class RecordSimHistory(Event):
    """ event to update the history of this simulated epidemic """

    def __init__(self, time, epi_model):
        Event.__init__(self, time, priority=RECORD_SIM_HISTORY)
        self.epiModel = epi_model

    def process(self, rng=None):
        self.epiModel.record_sim_outputs()


class RecordObservedHistory(Event):
    """ event to update the history of this simulated epidemic for calibration """

    def __init__(self, time, epi_model):
        Event.__init__(self, time, priority=RECORD_OBS_HISTORY)
        self.epiModel = epi_model

    def process(self, rng=None):
        self.epiModel.record_surveillance()


class CollectCostHealth(Event):
    """ event to collect the cost and health outcomes """

    def __init__(self, time, epi_model):
        Event.__init__(self, time, priority=COLLECT_COST_HEALTH)
        self.epiModel = epi_model

    def process(self, rng=None):
        self.epiModel.collect_cost_health()


class MakeDecisions(Event):
    """ event to make decisions (which interventions to employ) """

    def __init__(self, time, epi_model):
        Event.__init__(self, time, priority=MAKE_DECISIONS)
        self.epiModel = epi_model

    def process(self, rng=None):
        self.epiModel.make_decisions()
