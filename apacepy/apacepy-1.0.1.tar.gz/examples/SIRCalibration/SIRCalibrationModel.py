from apacepy.TimeSeries import SumIncidence, SumPrevalence, RatioTimeSeries
from deampy.parameters import Constant, Inverse, Division, Uniform

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, EpiIndepEvent, EpiDepEvent
from examples.SIRCalibration.data import CalibrationData as D


class SIRParameters(EpiParameters):
    """ class to contain the parameters of an SIR model """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S': Constant(value=100000),
             'Size I': Constant(value=1),
             'Size R': Constant(value=0),
             'R0': Uniform(minimum=1, maximum=3),  # Constant(value=1.5),
             'Infection duration':  Uniform(minimum=1/364, maximum=14/364), # Constant(value=5/364)
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
    settings.observationPeriod = 7/364  # days in observation periods (for calibration + surveillance)

    settings.storeParameterValues = True  # store the sampled parameter values

    return settings


def build_SIR(model):

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

    # population size
    pop_size = SumPrevalence(name='Population size', compartments=[S, I, R])

    # setup incidence and surveillance to check the start of the epidemic
    incidence = SumIncidence(name='Incidence', compartments=[I], first_nonzero_obs_marks_start_of_epidemic=True)
    # add feasible ranges of incidence
    # incidence.add_feasible_conditions(feasible_conditions=FeasibleConditions(feasible_max=25,
    #                                                                          min_threshold_to_hit=4))

    # incidence rate
    incidence_rate = RatioTimeSeries(name='Incidence rate',
                                     numerator_sum_time_series=incidence,
                                     denominator_sum_time_series=pop_size,
                                     if_surveyed=True)

    # add calibration target
    incidence_rate.add_calibration_targets(ratios=[row[1] for row in D.IncidenceRate],
                                           survey_sizes=[D.SURVEY_SIZE]*len(D.IncidenceRate))

    # populate the model
    model.populate(compartments=[S, I, R], parameters=params,
                   list_of_sum_time_series=[pop_size, incidence],
                   list_of_ratio_time_series=[incidence_rate])
