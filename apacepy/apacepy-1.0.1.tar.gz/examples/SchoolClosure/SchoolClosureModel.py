from apacepy.CalibrationSupport import FeasibleConditions
from apacepy.Control import InterventionAffectingContacts, TimeBasedDecisionRule, \
    ConditionBasedDecisionRule, DynamicDecisionRule
from apacepy.FeaturesAndConditions import FeatureSurveillance, FeatureIntervention, ConditionOnFeatures
from apacepy.TimeSeries import SumIncidence, SumPrevalence, SumCumulativeIncidence
from deampy.Optimization.ApproxPolicyIteration import GreedyApproxDecisionMaker
from deampy.parameters import Constant, Inverse, MatrixOfParams

from apacepy.inputs import EpiParameters, ModelSettings
from apacepy.model_objects import Compartment, EpiIndepEvent, EpiDepEvent
from examples.AdaptiveSchoolClosure.ROOT import ROOT_DIR


class SchoolClosureParameters(EpiParameters):
    """ class to contain the parameters of an age-structured SIR model to evaluate school closure """
    def __init__(self):
        EpiParameters.__init__(self)

        self.dictOfParams = dict(
            {'Size S_Ch': Constant(value=1000),
             'Size S_Ad': Constant(value=2000),
             'Size I_Ch': Constant(value=1),
             'Size I_Ad': Constant(value=1),
             'Infection duration': Constant(value=5/364),
             # adults 1.5 times more susceptible compared to children
             'Susceptibility Ad to Ch': Constant(value=1.5),
             'Infectivity': Constant(value=2.5)
             })

        # recovery rate is the inverse of recovery duration
        self.dictOfParams['Recovery rate'] = Inverse(par=self.dictOfParams['Infection duration'])

        # contact rates
        self.dictOfParams['Base contact matrix'] = MatrixOfParams(
            matrix_of_params_or_values=[[40, 9],  # between children and [children, adults]
                                        [9, 15]   # between adults and [children, adults]
                                        ])
        self.dictOfParams['Change in contact matrix under school closure'] = MatrixOfParams(
            matrix_of_params_or_values=[[-0.5, 0.1],
                                        [0.1, 0]])


class SchoolClosureSettings(ModelSettings):

    def __init__(self, if_optimizing=False):

        ModelSettings.__init__(self)

        # model settings
        self.deltaT = 1 / 364  # 1 day
        self.simulationDuration = 2  # years of simulation
        self.simulationOutputPeriod = 1 / 364  # years for simulation output period
        self.observationPeriod = 7 / 364  # years for observation period
        self.timeToStartDecisionMaking = 7/364  # after the detection of spread
                                                 # (when we have at least 1 case during an observation period)
        self.storeProjectedOutcomes = True

        # economic evaluation settings
        self.collectEconEval = True  # to collect cost and health outcomes
        self.annualDiscountRate = 0.0

        # custom settings
        self.closeSchools = False
        self.decisionRule = None

        self.timeOn = None
        self.timeOff = None

        self.thresholdOn = None
        self.thresholdOff = None

        self.ifOptimizing = if_optimizing
        self.dynamicType = None
        self.qFunctionDegrees = None
        self.qFunctionCSVFile = None

    def update_settings(self, schools_closed=False, decision_rule='time-based',
                        time_on=None, time_off=None,
                        threshold_on=None, threshold_off=None,
                        dynamic_type=None, wtp=None):
        """
        :param schools_closed:
        :param decision_rule:
        :param time_on:
        :param time_off:
        :param threshold_on:
        :param threshold_off:
        :param dynamic_type:
                'cum incd' for using cumulative incidence as feature
                'incd + delta incd' for using incidence and change in incidence as features
                'incd + cum incd' for using incidence and cumulative incidence as features
                'incd + pd status' for using incidence and the status of physical distancing intervention
                as features
        :param wtp: willingness-to-pay threshold to use to optimize the dynamic policy
        """
        if schools_closed:
            self.folderToSaveTrajs = 'outputs/trajectories/closed-' + decision_rule
            self.folderToSaveSummary = 'outputs/summaries/closed-' + decision_rule
            self.closeSchools = True
            self.decisionRule = decision_rule
            self.timeOn = time_on
            self.timeOff = time_off
            self.thresholdOn = threshold_on
            self.thresholdOff = threshold_off
            self.qFunctionDegrees = 2
            self.dynamicType = dynamic_type
            self.qFunctionCSVFile = ROOT_DIR+'/q-functions/WTP{}-{}/q-functions.csv'\
                .format(wtp, dynamic_type)
        else:
            self.folderToSaveTrajs = 'outputs/trajectories/open'
            self.folderToSaveSummary = 'outputs/summaries/open'
            self.closeSchools = False


def build_school_closure_model(model):

    # settings
    sets = model.settings

    # model parameters
    params = SchoolClosureParameters()

    # --------- model compartments ---------
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

    # --------- model outputs to collect ---------
    # set up prevalence, incidence, and cumulative incidence to collect
    S_Ch.setup_history(collect_prev=True)
    I_Ch.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R_Ch.setup_history(collect_prev=True)
    S_Ad.setup_history(collect_prev=True)
    I_Ad.setup_history(collect_prev=True, collect_incd=True, collect_cum_incd=True)
    R_Ad.setup_history(collect_prev=True)

    # --------- model events ---------
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

    # --------- connections of events and compartments ---------
    # attached epidemic events to compartments
    S_Ch.add_event(event=infection_ch)
    I_Ch.add_event(event=recovering_ch)
    S_Ad.add_event(event=infection_ad)
    I_Ad.add_event(event=recovering_ad)

    # --------- sum statistics and surveillance ---------
    # incidence
    incidence = SumIncidence(name='Incidence', compartments=[I_Ch, I_Ad],
                             if_surveyed=True,
                             first_nonzero_obs_marks_start_of_epidemic=True,
                             collect_cumulative_after_warm_up='e')
    # cumulative incidence
    cum_incd = SumCumulativeIncidence(name='Cumulative incidence',
                                      compartments=[I_Ch, I_Ad],
                                      if_surveyed=True)
    # prevalence of infection
    total_prev = SumPrevalence(name='Prevalence', compartments=[I_Ch, I_Ad])

    # add feasible ranges for incidence if calibrating the model
    if model.settings.calcLikelihood:
        incidence.add_feasible_conditions(
            feasible_conditions=FeasibleConditions(min_threshold_to_hit=5))

    # --------- set up economic evaluation outcomes ---------
    incidence.setup_econ_outcome(par_health_per_new_member=Constant(1))

    #  --------- set up modeling school closure ---------
    interventions = None
    features = None
    conditions = None
    if sets.closeSchools:
        interventions, features, conditions = get_interventions_features_conditions(
            settings=sets, params=params, incidence=incidence, cum_incd=cum_incd)

    # --------- populate the model ---------
    model.populate(compartments=[S_Ch, I_Ch, R_Ch, S_Ad, I_Ad, R_Ad],
                   parameters=params, param_base_contact_matrix=params.dictOfParams['Base contact matrix'],
                   list_of_sum_time_series=[incidence, cum_incd, total_prev],
                   interventions=interventions,
                   features=features,
                   conditions=conditions)


def get_interventions_features_conditions(settings, params, incidence, cum_incd):

    features = None
    conditions = None

    # --------- intervention ---------
    school_closure = InterventionAffectingContacts(
        name='School closure',
        par_perc_change_in_contact_matrix=params.dictOfParams['Change in contact matrix under school closure'])
    # economic outcomes
    school_closure.setup_econ_outcome(par_cost_per_unit_of_time=Constant(1))

    # --------- decision rule ---------
    if settings.decisionRule == 'time-based':
        decision_rule = TimeBasedDecisionRule(
                time_to_turn_on=settings.timeOn / 52,    # at the beginning of the week
                time_to_turn_off=settings.timeOff / 52)  # at the end of the week

    elif settings.decisionRule in ('threshold-based', 'dynamic'):

        # --------- features ---------
        # feature: incidence
        feature_incidence = FeatureSurveillance(name='Incidence',
                                                sum_time_series_with_surveillance=incidence)
        # feature: change in incidence
        feature_delta_incidence = FeatureSurveillance(name='Change in incidence',
                                                      sum_time_series_with_surveillance=incidence,
                                                      feature_type='s')

        # feature: cumulative incidence
        feature_cum_incd = FeatureSurveillance(name='Cumulative incidence',
                                               sum_time_series_with_surveillance=cum_incd)

        # feature: the switch status of the intervention
        feature_intervention = FeatureIntervention(name='Status of school closure',
                                                   intervention=school_closure)

        # --------- conditions ---------
        if settings.decisionRule == 'threshold-based':
            on_condition = ConditionOnFeatures(name='turn on school closure',
                                               features=[feature_intervention, feature_incidence],
                                               signs=['e', 'ge'],
                                               thresholds=[0, settings.thresholdOn])
            off_condition = ConditionOnFeatures(name='turn off school closure',
                                                features=[feature_intervention, feature_incidence],
                                                signs=['e', 'l'],
                                                thresholds=[1, settings.thresholdOff])

            # --------- decision rule ---------
            decision_rule = ConditionBasedDecisionRule(
                default_switch_value=0,
                condition_to_turn_on=on_condition,
                condition_to_turn_off=off_condition)
            conditions = [on_condition, off_condition]

        elif settings.decisionRule == 'dynamic':
            if not settings.ifOptimizing:
                # make an approximate decision maker
                approx_decision_maker = GreedyApproxDecisionMaker(num_of_actions=1,
                                                                  q_function_degree=settings.qFunctionDegrees,
                                                                  q_functions_csv_file=settings.qFunctionCSVFile)

                # check the type of dynamic policies
                if settings.dynamicType == 'cum incd':
                    # using cumulative incidence as feature
                    decision_rule = DynamicDecisionRule(
                        approx_decision_maker=approx_decision_maker,
                        continuous_features=[feature_cum_incd])
                elif settings.dynamicType == 'incd + delta incd':
                    # using incidence and change in incidence as feature
                    decision_rule = DynamicDecisionRule(
                        approx_decision_maker=approx_decision_maker,
                        continuous_features=[feature_incidence, feature_delta_incidence])
                elif settings.dynamicType == 'incd + cum incd':
                    # using incidence and cumulative incidence as feature
                    decision_rule = DynamicDecisionRule(
                        approx_decision_maker=approx_decision_maker,
                        continuous_features=[feature_incidence, feature_cum_incd])
                elif settings.dynamicType == 'incd + closure status':
                    # using incidence and status of the intervention as feature
                    decision_rule = DynamicDecisionRule(
                        approx_decision_maker=approx_decision_maker,
                        continuous_features=[feature_incidence],
                        indicator_features=[feature_intervention])
                else:
                    raise ValueError('Invalid type for dynamic decision rule.')
            else:
                decision_rule = None
        else:
            raise ValueError('Invalid decision rule.')
        # --------- features and conditions ---------
        features = [feature_incidence, feature_delta_incidence, feature_cum_incd, feature_intervention]

    else:
        raise ValueError

    # add decision rules
    if decision_rule is not None:
        school_closure.add_decision_rule(decision_rule=decision_rule)

    interventions = [school_closure]

    return interventions, features, conditions
