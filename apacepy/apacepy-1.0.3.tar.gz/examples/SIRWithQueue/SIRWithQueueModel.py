from apacepy.TimeSeries import SumPrevalence
from deampy.parameters import Constant, Inverse, Division

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, ChanceNode, QueueCompartment, DeathCompartment, Capacity, EpiIndepEvent, \
    EpiDepEvent


class SIRWithQueueParameters(EpiParameters):
    """ class to contain the parameters of an SIR model with queue """
    def __init__(self, delta_t):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S': Constant(value=10000),
             'Size I': Constant(value=10),
             'R0': Constant(value=1.75),
             'Infection duration': Constant(value=5/364),
             'Hospitalization duration': Constant(value=10/364),
             'Prob of hospitalization': Constant(value=0.2),
             'Hospital beds': Constant(value=100),
             'Death rate while waiting for hospital bed': Constant(value=364/30)
             })

        self.dictOfParams['Rate out of I'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Discharge rate'] = Inverse(par=self.dictOfParams['Hospitalization duration'])
        self.dictOfParams['Infectivity'] = Division(par_numerator=self.dictOfParams['R0'],
                                                    par_denominator=self.dictOfParams['Infection duration'])


def get_model_settings():

    # model settings
    settings = ModelSettings()
    settings.deltaT = 1 / 364  # 1 day
    settings.simulationDuration = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 1/364  # simulation output period

    return settings


def build_SIR_with_queue_model(model):

    # model parameters
    params = SIRWithQueueParameters(delta_t=model.settings.deltaT)

    # model compartments
    S = Compartment(name='Susceptible', size_par=params.dictOfParams['Size S'],
                    susceptibility_params=Constant(value=1))
    I = Compartment(name='Infectious', size_par=params.dictOfParams['Size I'],
                    infectivity_params=params.dictOfParams['Infectivity'],
                    if_empty_to_eradicate=True)
    H = Compartment(name='Hospitalized')
    R = Compartment(name='Recovered')
    D = DeathCompartment(name='Death')

    # time series of hospitalizations
    hospitalizations = SumPrevalence(name='Number hospitalized',
                                     compartments=[H])
    # hospital queue
    Q = QueueCompartment(name='Hospital queue',
                         if_empty_to_eradicate=True,
                         destination_if_capacity_available=H,
                         capacity=Capacity(capacity_param=params.dictOfParams['Hospital beds'],
                                           consumption_prevalence=hospitalizations))

    # chance nodes
    if_hospitalized = ChanceNode(name='If hospitalized',
                                 destination_compartments=[Q, R],
                                 probability_params=params.dictOfParams['Prob of hospitalization'])

    # set up prevalence, incidence, and cumulative incidence to collect
    S.setup_history(collect_prev=True)
    I.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R.setup_history(collect_prev=True)
    H.setup_history(collect_prev=True, collect_incd=True)
    Q.setup_history(collect_prev=True, collect_incd=True)
    D.setup_history(collect_incd=True, collect_cum_incd=True)

    # model events
    infection = EpiDepEvent(
        name='Infection', destination=I)
    leaving_i = EpiIndepEvent(
        name='Leaving I',
        rate_param=params.dictOfParams['Rate out of I'],
        destination=if_hospitalized)
    discharge = EpiIndepEvent(
        name='Hospital discharge',
        rate_param=params.dictOfParams['Discharge rate'],
        destination=R)
    death_while_waiting = EpiIndepEvent(
        name='Death while waiting for hospital bed',
        rate_param=params.dictOfParams['Death rate while waiting for hospital bed'],
        destination=D)

    # attached epidemic events to compartments
    S.add_event(event=infection)
    I.add_event(event=leaving_i)
    H.add_event(event=discharge)
    Q.add_event(event=death_while_waiting)

    # populate the model
    model.populate(compartments=[S, I, H, R, D],
                   chance_nodes=[if_hospitalized],
                   queue_compartments=[Q],
                   list_of_sum_time_series=[hospitalizations],
                   parameters=params)

