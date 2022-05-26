from apacepy.TimeSeries import SumIncidence
from deampy.parameters import Constant, Inverse, Division

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, EpiIndepEvent, EpiDepEvent


class SIRParameters(EpiParameters):
    """ class to contain the parameters of an SIR model """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S': Constant(value=1000),
             'Size I': Constant(value=10),
             'Size R': Constant(value=0),
             'R0': Constant(value=1.5),
             'Infection duration': Constant(value=5/364),
             'Infection cost': Constant(value=100),  # one-time cost of diagnosis and treatment
             'Disutility weight in I': Constant(value=0.00),  # quality weight while in I
             'Disutility weight when enter I': Constant(value=1)  # quality weight while in I
             })

        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Infectivity'] = Division(par_numerator=self.dictOfParams['R0'],
                                                    par_denominator=self.dictOfParams['Infection duration'])


def get_model_settings():

    # model settings
    settings = ModelSettings()

    # customize the model settings as needed
    settings.deltaT = 1 / 364  # simulated time steps
    settings.simulationDuration = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 7/364  # days for simulation output period

    # economic evaluation settings
    settings.collectEconEval = True   # to collect cost and health outcomes
    settings.annualDiscountRate = 0.0
    settings.endOfWarmUpPeriod = 7 / 364   # economic outcomes are collected after the end of the warm-up period

    # if want to report projected outcomes collected after the end of the warm-up period
    settings.storeProjectedOutcomes = True

    return settings


def build_SIR_model(model):

    # model parameters
    params = SIRParameters()

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

    # set up prevalence, incidence, and cumulative incidence to collect
    S.setup_history(collect_prev=True)
    I.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R.setup_history(collect_prev=True)

    # model events
    infection = EpiDepEvent(
        name='Infection', destination=I)
    recovering = EpiIndepEvent(
        name='Recovery',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=R)

    # attached epidemic events to compartments
    S.add_event(event=infection)
    I.add_event(event=recovering)

    # set up economic evaluation outcomes
    I.setup_econ_outcome(par_health_per_new_member=params.dictOfParams['Disutility weight when enter I'],
                         par_health_per_unit_of_time=params.dictOfParams['Disutility weight in I'],
                         par_cost_per_new_member=params.dictOfParams['Infection cost'])

    # set up collecting outcomes projected after the warm-up
    # to collect total cases after the warm-up
    # 's' is to collect cumulative observations after when the simulation time passes the warm-up period
    sum_I = SumIncidence(name='Incidence', compartments=[I],
                         collect_cumulative_after_warm_up='s')

    # populate the model
    model.populate(compartments=[S, I, R], parameters=params, list_of_sum_time_series=[sum_I])

