from apacepy.TimeSeries import SumIncidence
from deampy.parameters import Constant, Inverse, Division

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, DeathCompartment, EpiIndepEvent, EpiDepEvent


class SIRWithDeathParameters(EpiParameters):
    """ class to contain the parameters of an SIR model with death """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S': Constant(value=10000),
             'Size I': Constant(value=10),
             'Size R': Constant(value=0),
             'R0': Constant(value=1.5),
             'Infection duration': Constant(value=5/364),
             'Death rate': Constant(value=364 / 50)
             })

        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Infectivity'] = Division(par_numerator=self.dictOfParams['R0'],
                                                    par_denominator=self.dictOfParams['Infection duration'])


def get_model_settings():

    # model settings
    settings = ModelSettings()
    settings.deltaT = 1 / 364  # 1 day
    settings.simulationDuration = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 1/364  # simulation output period
    settings.storeProjectedOutcomes = True

    return settings


def build_SIR_with_death_model(model):

    # model parameters
    params = SIRWithDeathParameters()

    # model compartments
    S = Compartment(name='Susceptible', size_par=params.dictOfParams['Size S'],
                    susceptibility_params=Constant(value=1),
                    infectivity_params=Constant(value=0))
    I = Compartment(name='Infectious', size_par=params.dictOfParams['Size I'],
                    susceptibility_params=Constant(value=0),
                    infectivity_params=params.dictOfParams['Infectivity'],
                    if_empty_to_eradicate=True)
    R = Compartment(name='Recovered', size_par=params.dictOfParams['Size R'],
                    susceptibility_params=Constant(value=0),
                    infectivity_params=Constant(value=0))
    D = DeathCompartment(name='Death')

    # set up prevalence, incidence, and cumulative incidence to collect
    S.setup_history(collect_prev=True)
    I.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R.setup_history(collect_prev=True)
    D.setup_history(collect_incd=True, collect_cum_incd=True)

    # model events
    infection = EpiDepEvent(
        name='Infection', destination=I)
    recovering = EpiIndepEvent(
        name='Recovery',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=R)
    death = EpiIndepEvent(
        name='Death',
        rate_param=params.dictOfParams['Death rate'],
        destination=D)

    # attached epidemic events to compartments
    S.add_event(event=infection)
    I.add_event(event=recovering)
    I.add_event(event=death)

    death_stat = SumIncidence(name='Death',
                              compartments=[D],
                              collect_cumulative_after_warm_up='s')
    # populate the model
    model.populate(compartments=[S, I, R, D],
                   parameters=params, list_of_sum_time_series=[death_stat])

