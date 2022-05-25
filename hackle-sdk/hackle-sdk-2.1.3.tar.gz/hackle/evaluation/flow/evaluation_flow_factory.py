from hackle import logger as _logging
from hackle.evaluation.action.action_resolver import ActionResolver
from hackle.evaluation.bucket.bucketer import Bucketer
from hackle.evaluation.flow.evaluation_flow import EvaluationFlow
from hackle.evaluation.flow.flow_evaluator import *
from hackle.evaluation.match.condition_matcher import ConditionMatcherFactory
from hackle.evaluation.match.target_matcher import TargetMatcher
from hackle.evaluation.target.experiment_target_determiner import ExperimentTargetDeterminer
from hackle.evaluation.target.target_rule_determiner import TargetRuleDeterminer


class EvaluationFlowFactory(object):

    def __init__(self, logger=None):
        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())

        target_matcher = TargetMatcher(ConditionMatcherFactory())
        action_resolver = ActionResolver(Bucketer(), self.logger)

        self.ab_test_flow = EvaluationFlow.of(
            OverrideEvaluator(),
            DraftEvaluator(),
            PausedEvaluator(),
            CompletedEvaluator(),
            ExperimentTargetEvaluator(ExperimentTargetDeterminer(target_matcher)),
            TrafficAllocateEvaluator(action_resolver)
        )

        self.feature_flag_flow = EvaluationFlow.of(
            DraftEvaluator(),
            PausedEvaluator(),
            CompletedEvaluator(),
            OverrideEvaluator(),
            TargetRuleEvaluator(TargetRuleDeterminer(target_matcher), action_resolver),
            DefaultRuleEvaluator(action_resolver)
        )

    def get_evaluation_flow(self, experiment_type):
        if experiment_type == 'AB_TEST':
            return self.ab_test_flow
        elif experiment_type == 'FEATURE_FLAG':
            return self.feature_flag_flow
        else:
            raise Exception('Unsupported type [{}]'.format(experiment_type))
