from deampy.parameters import Constant, Inverse, Product

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, ChanceNode, EpiIndepEvent, EpiDepEvent


class SISWithResistanceParameters(EpiParameters):
    """ class to contain the parameters of an SIS model with resistance """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S': Constant(value=1000000),
             'Size I-Sus': Constant(value=10),
             'Size I-Res': Constant(value=0),
             'Infectivity for susceptible strain': Constant(value=100),
             'Relative infectivity for resistant strain': Constant(value=0.5),
             'Infection duration': Constant(value=5/364),
             'Prob of resistance': Constant(value=0.001)
             })

        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])
        self.dictOfParams['Infectivity for resistant strain'] = Product(
            parameters=[self.dictOfParams['Infectivity for susceptible strain'],
                        self.dictOfParams['Relative infectivity for resistant strain']
                        ])


def get_model_settings():

    # model settings
    settings = ModelSettings()
    settings.deltaT = 1 / 364  # 1 day
    settings.simulationDuration = 1  # years
    settings.simulationOutputPeriod = 1/364  # simulation output period

    return settings


def build_SIS_with_resistance_model(model):

    # model parameters
    params = SISWithResistanceParameters()

    # model compartments
    S = Compartment(name='Sus', size_par=params.dictOfParams['Size S'],
                    susceptibility_params=[Constant(value=1), Constant(value=1)])
    I_S = Compartment(name='Inf-Sus',
                      size_par=params.dictOfParams['Size I-Sus'],
                      infectivity_params=[
                          params.dictOfParams['Infectivity for susceptible strain'],
                          Constant(value=0)],
                      if_empty_to_eradicate=True)
    I_R = Compartment(name='Inf-Res',
                      size_par=params.dictOfParams['Size I-Res'],
                      infectivity_params=[
                          Constant(value=0),
                          params.dictOfParams['Infectivity for resistant strain']],
                      if_empty_to_eradicate=True)

    if_resist = ChanceNode(name='If Res after Tx',
                           destination_compartments=[I_R, S],
                           probability_params=params.dictOfParams['Prob of resistance'])

    # set up prevalence, incidence, and cumulative incidence to collect
    S.setup_history(collect_prev=True)
    I_S.setup_history(collect_prev=True, collect_incd=True)
    I_R.setup_history(collect_prev=True, collect_incd=True)

    # model events
    infection_sus = EpiDepEvent(
        name='Infection-Sus', destination=I_S, generating_pathogen=0)
    infection_res = EpiDepEvent(
        name='Infection-Res', destination=I_R, generating_pathogen=1)
    recovering_sus = EpiIndepEvent(
        name='Recovery from susceptible infection',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=if_resist)
    recovering_res = EpiIndepEvent(
        name='Recovery from resistant infection',
        rate_param=params.dictOfParams['Recovery rate'],
        destination=S)

    # attached epidemic events to compartments
    S.add_events(events=[infection_sus, infection_res])
    I_S.add_event(event=recovering_sus)
    I_R.add_event(event=recovering_res)

    # populate the model
    model.populate(compartments=[S, I_S, I_R],
                   chance_nodes=[if_resist],
                   parameters=params)

