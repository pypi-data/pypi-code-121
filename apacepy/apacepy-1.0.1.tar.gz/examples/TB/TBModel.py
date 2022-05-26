from deampy.parameters import Constant, Inverse, Uniform

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, ChanceNode, EpiIndepEvent, EpiDepEvent

USE_PRIOR = True
TRANS = 10
PROB_PROG = 0.1
INF_DUR = 1
INF_PREV = 0.01
R_PREV = 0.005
L_PREV = 0.75


class TBarameters(EpiParameters):
    """ class to contain the parameters of an TB model """
    def __init__(self):
        EpiParameters.__init__(self)
        N = 100000
        if USE_PRIOR:
            self.dictOfParams = dict(
                {'Size S': Constant(value=0.25*N),
                 'Size L': Uniform(minimum=L_PREV*N*0.9, maximum=L_PREV*N*1.1),
                 'Size I': Uniform(minimum=INF_PREV*N*0.9, maximum=INF_PREV*N*1.1),
                 'Size R': Uniform(minimum=R_PREV*N*0.9, maximum=R_PREV*N*1.1),
                 'Transmission': Uniform(minimum=TRANS*0.9, maximum=TRANS*1.1),
                 'Prob progression': Uniform(minimum=PROB_PROG*0.9, maximum=PROB_PROG*1.1),
                 'Infection duration': Uniform(minimum=INF_DUR*0.9, maximum=INF_DUR*1.1),
                 'Treatment duration': Constant(value=0.5)
                 })
        else:
            self.dictOfParams = dict(
                {'Size S': Constant(value=0.25*N),
                 'Size L': Constant(value=L_PREV*N),
                 'Size I': Constant(value=INF_PREV*N),
                 'Size R': Constant(value=R_PREV*N),
                 'Transmission': Constant(value=TRANS),
                 'Prob progression': Constant(value=PROB_PROG),
                 'Infection duration': Constant(value=INF_DUR),
                 'Treatment duration': Constant(value=0.5)
                 })

        self.dictOfParams['Rate of seeking treatment'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Rate of recovery'] = Inverse(par=self.dictOfParams['Treatment duration'])


def get_model_settings():
    """ :returns an instance of ModelSettings to store the settings for simulating the SIR model """

    # model settings
    settings = ModelSettings()

    # customize the model settings as needed
    settings.deltaT = 7 / 364  # simulated time steps
    settings.simulationDuration = 25  # simulate for 1 year
    settings.simulationOutputPeriod = 1  # simulation output period (used to calculate the incidence)

    # set to true to stop the simulation when eradication conditions are met
    settings.checkEradicationConditions = False

    return settings


def build_TB_model(model):

    # model parameters
    params = TBarameters()

    # model compartments
    S = Compartment(name='Susceptible', size_par=params.dictOfParams['Size S'],
                    susceptibility_params=Constant(value=1),
                    infectivity_params=Constant(value=0))
    L = Compartment(name='Latent', size_par=params.dictOfParams['Size L'],
                    susceptibility_params=Constant(value=1))
    I = Compartment(name='Infectious', size_par=params.dictOfParams['Size I'],
                    infectivity_params=params.dictOfParams['Transmission'],
                    if_empty_to_eradicate=True)
    R = Compartment(name='Recovered', size_par=params.dictOfParams['Size R'])

    # chance node
    if_prog = ChanceNode(name='If progress',
                         destination_compartments=[I, L],
                         probability_params=params.dictOfParams['Prob progression'])

    # set up prevalence, incidence, and cumulative incidence to collect
    S.setup_history(collect_prev=True)
    L.setup_history(collect_prev=True)
    I.setup_history(collect_prev=True, collect_incd=True)
    R.setup_history(collect_prev=True)

    # model events
    infection = EpiDepEvent(
        name='Infection', destination=if_prog)
    reinfection = EpiDepEvent(
        name='Re-Infection', destination=if_prog)
    seeking_treatment = EpiIndepEvent(
        name='Seeking treatment',
        rate_param=params.dictOfParams['Rate of seeking treatment'],
        destination=R)
    recovering = EpiIndepEvent(
        name='Recovery',
        rate_param=params.dictOfParams['Rate of recovery'],
        destination=S)

    # attached epidemic events to compartments
    S.add_event(event=infection)
    L.add_event(event=reinfection)
    I.add_event(event=seeking_treatment)
    R.add_event(event=recovering)

    # populate the model
    model.populate(compartments=[S, L, I, R], chance_nodes=[if_prog], parameters=params)

