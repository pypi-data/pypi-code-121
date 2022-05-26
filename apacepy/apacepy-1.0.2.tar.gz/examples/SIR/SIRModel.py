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
             })

        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Infectivity'] = Division(par_numerator=self.dictOfParams['R0'],
                                                    par_denominator=self.dictOfParams['Infection duration'])


def get_model_settings():
    """ :returns an instance of ModelSettings to store the settings for simulating the SIR model """

    # model settings
    settings = ModelSettings()

    # customize the model settings as needed
    settings.deltaT = 1 / 364  # simulated time steps
    settings.simulationDuration = 1  # simulate for 1 year
    settings.simulationOutputPeriod = 1/364  # simulation output period (used to calculate the incidence)

    # set to true to stop the simulation when eradication conditions are met
    settings.checkEradicationConditions = True

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

    # populate the model
    model.populate(compartments=[S, I, R], parameters=params)

