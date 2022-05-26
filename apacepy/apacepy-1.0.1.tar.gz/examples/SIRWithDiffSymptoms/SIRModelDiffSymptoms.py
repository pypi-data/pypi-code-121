from apacepy.TimeSeries import SumPrevalence
from deampy.parameters import Constant, Inverse, Product

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, ChanceNode, EpiIndepEvent, EpiDepEvent


class SIRParameters(EpiParameters):
    """ class to contain the parameters of an SIR model """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S': Constant(value=1000),
             'Size I-Severe': Constant(value=5),
             'Size I-Mild': Constant(value=10),
             'Size R': Constant(value=0),
             'Infectivity I-Mild': Constant(value=100),
             'Infectivity Severe to Mild': Constant(value=1.5),
             'Infection duration': Constant(value=5/364),
             'Probability of severe infection': Constant(value=0.1)
             })

        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Infectivity I-Severe'] = Product(
            parameters=[self.dictOfParams['Infectivity I-Mild'],
                        self.dictOfParams['Infectivity Severe to Mild']]
        )


def get_model_settings():

    # model settings
    settings = ModelSettings()
    settings.deltaT = 1 / 365  # 1 day
    settings.simulationDuration = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 1/364  # 1 day for simulation output period
    settings.observationPeriod = 1/364 # 1 day for observation period

    return settings


def build_SIR_model_with_diff_symptoms(model):

    # model parameters
    params = SIRParameters()

    # model compartments
    S = Compartment(name='Susceptible', size_par=params.dictOfParams['Size S'],
                    susceptibility_params=Constant(value=1),
                    infectivity_params=Constant(value=0))
    I_severe = Compartment(name='Infectious|Severe', size_par=params.dictOfParams['Size I-Severe'],
                           susceptibility_params=Constant(value=0),
                           infectivity_params=params.dictOfParams['Infectivity I-Severe'],
                           if_empty_to_eradicate=True)
    I_mild = Compartment(name='Infectious|Mild', size_par=params.dictOfParams['Size I-Mild'],
                         susceptibility_params=Constant(value=0),
                         infectivity_params=params.dictOfParams['Infectivity I-Mild'],
                         if_empty_to_eradicate=True)
    R = Compartment(name='Recovered', size_par=params.dictOfParams['Size R'],
                    susceptibility_params=Constant(value=0),
                    infectivity_params=Constant(value=0))

    # chance nodes
    severe_or_mild = ChanceNode(name='Severe or Mild',
                                destination_compartments=[I_severe, I_mild],
                                probability_params=params.dictOfParams['Probability of severe infection'])

    # set up prevalence, incidence, and cumulative incidence to collect
    S.setup_history(collect_prev=True)
    severe_or_mild.setup_history(collect_incd=True)
    I_severe.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    I_mild.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R.setup_history(collect_prev=True)

    # model events
    infection = EpiDepEvent(
        name='Infection', destination=severe_or_mild)
    recovering_severe = EpiIndepEvent(
        name='Recovery from severe infection',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=R)
    recovering_mild = EpiIndepEvent(
        name='Recovery from mild infection',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=R)

    # attached epidemic events to compartments
    S.add_event(event=infection)
    I_severe.add_event(event=recovering_severe)
    I_mild.add_event(event=recovering_mild)

    # total prevalence
    total_prevalence = SumPrevalence(name='Prevalence', compartments=[I_severe, I_mild])

    # populate the model
    model.populate(compartments=[S, I_severe, I_mild, R],
                   chance_nodes=[severe_or_mild],
                   parameters=params,
                   list_of_sum_time_series=[total_prevalence])

