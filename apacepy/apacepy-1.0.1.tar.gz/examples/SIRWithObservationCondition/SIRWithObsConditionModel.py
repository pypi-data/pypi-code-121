from apacepy.TimeSeries import SumIncidence, SumPrevalence, RatioTimeSeries
from deampy.parameters import Constant, Inverse, Division

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, EpiIndepEvent, EpiDepEvent


class SIRParameters(EpiParameters):
    """ class to contain the parameters of an SIR model """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S': Constant(value=1000),
             'Size I': Constant(value=2),
             'Size R': Constant(value=0),
             'R0': Constant(value=1.5),
             'Infection duration': Constant(value=5/364)
             })

        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Infectivity'] = Division(par_numerator=self.dictOfParams['R0'],
                                                    par_denominator=self.dictOfParams['Infection duration'])


def get_model_settings():

    # model settings
    settings = ModelSettings()
    settings.deltaT = 1 / 364  # simulation time step
    settings.simulationDuration = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 1/364  # simulation output period (used to calculate the incidence)
    settings.observationPeriod = 7/364  # days in observation periods (for calibration + surveillance)

    return settings


def build_SIR_with_obs_conditions(model):

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

    # setup surveillance to check the start of the epidemic
    incidence = SumIncidence(name='Incidence', compartments=[I],
                             if_surveyed=True, first_nonzero_obs_marks_start_of_epidemic=True)

    # set up sum statistics to collect prevalence and incidence
    # population size
    pop_size = SumPrevalence(name='Population size', compartments=[S, I, R])
    # number of infected individuals
    num_infected = SumPrevalence(name='# I', compartments=[I])
    # prevalence
    prevalence = RatioTimeSeries(name='Prevalence',
                                 numerator_sum_time_series=num_infected,
                                 denominator_sum_time_series=pop_size,
                                 if_surveyed=True)
    # incidence rate
    incidence_rate = RatioTimeSeries(name='Incidence rate',
                                     numerator_sum_time_series=incidence,
                                     denominator_sum_time_series=pop_size,
                                     if_surveyed=True)

    # populate the model
    model.populate(compartments=[S, I, R], parameters=params,
                   list_of_sum_time_series=[incidence, num_infected, pop_size],
                   list_of_ratio_time_series=[incidence_rate, prevalence])
