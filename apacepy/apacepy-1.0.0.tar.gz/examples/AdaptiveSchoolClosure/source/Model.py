import numpy as np
from apacepy.Control import DynamicDecisionRule
from deampy.Optimization.ApproxPolicyIteration import SimModel
from deampy.Support.Simulation import SeedGenerator

import examples.SchoolClosure.SchoolClosureModel as M
from apacepy.epidemic import EpiModel


class SchoolClosureModelForOpt(SimModel):

    def __init__(self, wtp, dynamic_type, seeds, weights):
        """
        :param wtp: willingness-to-pay value
        :param dynamic_type:
                'cum incd' for using cumulative incidence as feature
                'incd + delta incd' for using incidence and change in incidence as features
                'incd + cum incd' for using incidence and cumulative incidence as features
                'incd + pd status' for using incidence and the status of physical distancing intervention
                as features
        :param seeds:
        :param weights:
        """

        SimModel.__init__(self)

        self.wtp = wtp
        self.dynamicType = dynamic_type
        self.rng = np.random.RandomState(seed=0)
        self.seedGenerator = SeedGenerator(seeds=seeds, weights=weights)

        # get model settings
        self.sets = M.SchoolClosureSettings(if_optimizing=True)
        self.sets.update_settings(schools_closed=True, decision_rule='dynamic', dynamic_type=dynamic_type, wtp=wtp)

        # make an (empty) epidemic model
        self.model = EpiModel(id=0, settings=self.sets)
        # populate the model
        M.build_school_closure_model(self.model)

    def set_approx_decision_maker(self, approx_decision_maker):
        """ to allow the optimization algorithm to set a decision maker for the model that makes
            approximately optimal decisions. """

        # find features
        indicator_features = None
        fs = self.model.epiHistory.featureName

        if self.dynamicType == 'cum incd':
            continuous_features = [f for f in fs if f.name == 'Cumulative incidence']

        elif self.dynamicType == 'incd + delta incd':
            continuous_features = [f for f in fs if f.name in ('Incidence', 'Change in incidence')]

        elif self.dynamicType == 'incd + cum incd':
            continuous_features = [f for f in fs if f.name in ('Incidence', 'Cumulative incidence')]

        elif self.dynamicType == 'incd + closure status':
            continuous_features = [f for f in fs if f.name == 'Incidence']
            indicator_features = [f for f in fs if f.name == 'Status of school closure']
        else:
            raise ValueError('Invalid type for dynamic decision rule.')

        # create a dynamic decision rule
        dynamic_decision_rule = DynamicDecisionRule(approx_decision_maker=approx_decision_maker,
                                                    continuous_features=continuous_features,
                                                    indicator_features=indicator_features)

        # add decision rules
        self.model.decisionMaker.interventions[0].add_decision_rule(
            decision_rule=dynamic_decision_rule)

    def simulate(self, itr):
        """ to allow th optimization algorithm to get one replication of the simulation model
        :param itr: (int) the iteration of the optimization algorithm
        """

        seed = self.seedGenerator.next_seed(rng=self.rng)
        self.model.simulate(seed=seed)

    def get_seq_of_costs(self):
        """ to allow tht optimization algorithm to get the sequence of cost observed
            during the decision periods of the simulation """

        nmb = self.model.get_discounted_nmb_loss_over_decision_periods(
            wtp=self.wtp, health_multiplier=1, cost_multiplier=52)

        # no decision was made in the first period
        return nmb[1:]
