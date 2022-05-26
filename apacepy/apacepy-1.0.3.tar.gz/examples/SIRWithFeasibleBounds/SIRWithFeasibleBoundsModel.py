from apacepy.CalibrationSupport import FeasibleConditions
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
             'Size I': Constant(value=1),
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
    settings.deltaT = 1 / 364  # 1 day
    settings.simulationOutputPeriod = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 1/364  # 1 day for simulation output period
    settings.observationPeriod = 1/364  # days in observation periods (for calibration + surveillance)

    settings.storeParameterValues = True  # store the sampled parameter values

    return settings


def build_SIR_with_feasible_bounds(model):

    # model parameters
    params = SIRParameters()

    # model compartments
    S = Compartment(name='Susceptible', size_par=params.dictOfParams['Size S'],
                    susceptibility_params=Constant(value=1))
    I = Compartment(name='Infectious', size_par=params.dictOfParams['Size I'],
                    infectivity_params=params.dictOfParams['Infectivity'],
                    if_empty_to_eradicate=True)
    R = Compartment(name='Recovered', size_par=params.dictOfParams['Size R'])

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
    incidence = SumIncidence(name='Incidence', compartments=[I], first_nonzero_obs_marks_start_of_epidemic=True)
    # add feasible ranges of incidence
    incidence.add_feasible_conditions(feasible_conditions=FeasibleConditions(feasible_max=25,
                                                                             min_threshold_to_hit=4))

    # populate the model
    model.populate(compartments=[S, I, R], parameters=params, list_of_sum_time_series=[incidence])
