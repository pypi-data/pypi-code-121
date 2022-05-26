from apacepy.Control import InterventionAffectingEvents, TimeBasedDecisionRule
from deampy.parameters import Constant, Inverse, Division

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, EpiIndepEvent, EpiDepEvent


class SIRWithVaccineParameters(EpiParameters):
    """ class to contain the parameters of an SIR with vaccine model """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S': Constant(value=10000),
             'Size I': Constant(value=10),
             'R0': Constant(value=1.5),
             'Infection duration': Constant(value=5/364),
             'Vaccination rate': Constant(value=364/10)
             })

        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Infectivity'] = Division(par_numerator=self.dictOfParams['R0'],
                                                    par_denominator=self.dictOfParams['Infection duration'])


def get_model_settings(vaccination_on=False):

    # model settings
    settings = ModelSettings()
    settings.deltaT = 1 / 364  # 1 day
    settings.simulationDuration = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 1/364  # simulation output period

    settings.vaccinationOne = vaccination_on
    if vaccination_on:
        settings.folderToSaveTrajs = 'trajectories-with-vaccine'
        settings.folderToSaveSummary = 'summary-with-vaccine'
    else:
        settings.folderToSaveTrajs = 'trajectories-without-vaccine'
        settings.folderToSaveSummary = 'summary-without-vaccine'

    return settings


def build_SIR_with_vaccine_model(model):

    # model parameters
    params = SIRWithVaccineParameters()

    # model compartments
    S = Compartment(name='Susceptible', size_par=params.dictOfParams['Size S'],
                    susceptibility_params=Constant(value=1))
    I = Compartment(name='Infectious', size_par=params.dictOfParams['Size I'],
                    infectivity_params=params.dictOfParams['Infectivity'],
                    if_empty_to_eradicate=True)
    R = Compartment(name='Recovered')
    V = Compartment(name='Vaccinated')

    # set up prevalence, incidence, and cumulative incidence to collect
    S.setup_history(collect_prev=True)
    I.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R.setup_history(collect_prev=True)
    V.setup_history(collect_prev=True)

    # vaccine intervention
    decision_rule = TimeBasedDecisionRule(
        time_to_turn_on=5 / 52,  # at the beginning of the second week
        time_to_turn_off=20 / 52)  # at the end of the fourth week
    vaccine_intervention = InterventionAffectingEvents(name='Vaccination',
                                                       decision_rule=decision_rule)
    interventions = None
    if model.settings.vaccinationOne:
        interventions = [vaccine_intervention]

    # model events
    infection = EpiDepEvent(
        name='Infection', destination=I)
    recovering = EpiIndepEvent(
        name='Recovery',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=R)
    vaccination = EpiIndepEvent(
        name='Vaccination',
        rate_param=params.dictOfParams['Vaccination rate'],
        destination=V,
        interv_to_activate=vaccine_intervention)

    # attached epidemic events to compartments
    S.add_events(events=[infection, vaccination])
    I.add_event(event=recovering)

    # populate the model
    model.populate(compartments=[S, I, R, V], parameters=params, interventions=interventions)

