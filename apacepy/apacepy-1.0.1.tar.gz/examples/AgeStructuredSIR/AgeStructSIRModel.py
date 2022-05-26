from apacepy.TimeSeries import SumIncidence, SumPrevalence, SumCumulativeIncidence, RatioTimeSeries
from deampy.parameters import Constant, Inverse, MatrixOfConstantParams

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, EpiIndepEvent, EpiDepEvent


class AgeStructuredSIRParameters(EpiParameters):
    """ class to contain the parameters of an age-structured SIR model """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S_Ch': Constant(value=1000),
             'Size S_Ad': Constant(value=2000),
             'Size I_Ch': Constant(value=1),
             'Size I_Ad': Constant(value=2),
             'Infection duration': Constant(value=5/364),
             # adults 1.5 times more susceptible compared to children
             'Susceptibility Ad to Ch': Constant(value=1.5),
             'Infectivity': Constant(value=3)
             })

        # recovery rate is the inverse of recovery duration
        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])

        # contact rates
        self.dictOfParams['Base contact rates'] = MatrixOfConstantParams([
            [40, 9],  # between children and [children, adults]
            [9, 15]  # between adults and [children, adults]
        ])


def get_model_settings():

    # model settings
    settings = ModelSettings()
    settings.deltaT = 1 / 364  # 1 day
    settings.simulationDuration = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 1/364  # days for simulation output period
    settings.observationPeriod = 7/364    # days for observation period

    return settings


def build_age_structured_SIR_model(model):

    # model parameters
    params = AgeStructuredSIRParameters()

    # model compartments
    S_Ch = Compartment(name='Susceptible Children', size_par=params.dictOfParams['Size S_Ch'],
                       susceptibility_params=Constant(value=1),
                       infectivity_params=Constant(value=0),
                       row_index_contact_matrix=0)
    S_Ad = Compartment(name='Susceptible Adults', size_par=params.dictOfParams['Size S_Ad'],
                       susceptibility_params=params.dictOfParams['Susceptibility Ad to Ch'],
                       infectivity_params=Constant(value=0),
                       row_index_contact_matrix=1)
    I_Ch = Compartment(name='Infectious Children', size_par=params.dictOfParams['Size I_Ch'],
                       susceptibility_params=Constant(value=0),
                       infectivity_params=params.dictOfParams['Infectivity'],
                       if_empty_to_eradicate=True,
                       row_index_contact_matrix=0)
    I_Ad = Compartment(name='Infectious Adults', size_par=params.dictOfParams['Size I_Ad'],
                       susceptibility_params=Constant(value=0),
                       infectivity_params=params.dictOfParams['Infectivity'],
                       if_empty_to_eradicate=True,
                       row_index_contact_matrix=1)
    R_Ch = Compartment(name='Recovered Children', size_par=Constant(value=0),
                       susceptibility_params=Constant(value=0),
                       infectivity_params=Constant(value=0),
                       row_index_contact_matrix=0)
    R_Ad = Compartment(name='Recovered Adults', size_par=Constant(value=0),
                       susceptibility_params=Constant(value=0),
                       infectivity_params=Constant(value=0),
                       row_index_contact_matrix=1)

    # set up prevalence, incidence, and cumulative incidence to collect
    S_Ch.setup_history(collect_prev=True)
    I_Ch.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R_Ch.setup_history(collect_prev=True)
    S_Ad.setup_history(collect_prev=True)
    I_Ad.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R_Ad.setup_history(collect_prev=True)

    # model events
    infection_ch = EpiDepEvent(
        name='Infection among children', destination=I_Ch)
    recovering_ch = EpiIndepEvent(
        name='Recovery among children',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=R_Ch)
    infection_ad = EpiDepEvent(
        name='Infection among adults', destination=I_Ad)
    recovering_ad = EpiIndepEvent(
        name='Recovery among adults',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=R_Ad)

    # attached epidemic events to compartments
    S_Ch.add_event(event=infection_ch)
    I_Ch.add_event(event=recovering_ch)
    S_Ad.add_event(event=infection_ad)
    I_Ad.add_event(event=recovering_ad)

    # population size
    pop_size = SumPrevalence(name='Population', compartments=[S_Ch, I_Ch, R_Ch, S_Ad, I_Ad, R_Ad])
    # total incidence
    total_incd = SumIncidence(name='Incidence', compartments=[I_Ch, I_Ad],
                              first_nonzero_obs_marks_start_of_epidemic=True)
    # total accumulating incidence
    total_cum_incd = SumCumulativeIncidence(name='Cumulative incidence', compartments=[I_Ch, I_Ad])
    # total prevalence of infection
    total_prev = SumPrevalence(name='Prevalence', compartments=[I_Ch, I_Ad])

    # age distribution of incidence
    prop_incd_children = RatioTimeSeries(name='% incidence | children',
                                         numerator_compartment_incd=I_Ch,
                                         denominator_sum_time_series=total_incd)
    prop_incd_adults = RatioTimeSeries(name='% incidence | adults',
                                       numerator_compartment_incd=I_Ad,
                                       denominator_sum_time_series=total_incd)
    # age distribution of accumulating incidence
    prop_cum_incd_children = RatioTimeSeries(name='% total incidence | children',
                                             numerator_compartment_cum_incd=I_Ch,
                                             denominator_sum_time_series=total_cum_incd)
    prop_cum_incd_adults = RatioTimeSeries(name='% total incidence | adults',
                                           numerator_compartment_cum_incd=I_Ad,
                                           denominator_sum_time_series=total_cum_incd)
    # age distribution of prevalence
    prop_prev_children = RatioTimeSeries(name='% prevalence | children',
                                         numerator_compartment_prev=I_Ch,
                                         denominator_sum_time_series=total_prev)
    prop_prev_adults = RatioTimeSeries(name='% prevalence | adults',
                                       numerator_compartment_prev=I_Ad,
                                       denominator_sum_time_series=total_prev)

    # surveyed prevalence
    survey_prev = RatioTimeSeries(name='Estimated prevalence',
                                  numerator_sum_time_series=total_prev,
                                  denominator_sum_time_series=pop_size,
                                  if_surveyed=True)

    # populate the model
    model.populate(compartments=[S_Ch, I_Ch, R_Ch, S_Ad, I_Ad, R_Ad],
                   parameters=params, param_base_contact_matrix=params.dictOfParams['Base contact rates'],
                   list_of_sum_time_series=[pop_size, total_incd, total_cum_incd, total_prev],
                   list_of_ratio_time_series=[prop_incd_children, prop_incd_adults,
                                              prop_cum_incd_children, prop_cum_incd_adults,
                                              prop_prev_children, prop_prev_adults,
                                              survey_prev]
                   )

