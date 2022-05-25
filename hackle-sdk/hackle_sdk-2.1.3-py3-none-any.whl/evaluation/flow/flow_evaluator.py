import abc

from hackle.decision import DecisionReason
from hackle.entities import DraftExperiment, PausedExperiment, CompletedExperiment, RunningExperiment
from hackle.evaluation.evaluator import Evaluation


class FlowEvaluator(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        pass


class OverrideEvaluator(FlowEvaluator):
    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        overridden_variation = experiment.get_overridden_variation_or_none(user)

        if overridden_variation:
            if experiment.type == 'AB_TEST':
                return Evaluation.with_variation(overridden_variation, DecisionReason.OVERRIDDEN)
            elif experiment.type == 'FEATURE_FLAG':
                return Evaluation.with_variation(overridden_variation, DecisionReason.INDIVIDUAL_TARGET_MATCH)
            else:
                raise Exception('experiment type [{}]'.format(experiment.type))
        else:
            return next_flow.evaluate(workspace, experiment, user, default_variation_key)


class DraftEvaluator(FlowEvaluator):
    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        if isinstance(experiment, DraftExperiment):
            return Evaluation.of(experiment, default_variation_key, DecisionReason.EXPERIMENT_DRAFT)
        else:
            return next_flow.evaluate(workspace, experiment, user, default_variation_key)


class PausedEvaluator(FlowEvaluator):
    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        if isinstance(experiment, PausedExperiment):
            if experiment.type == 'AB_TEST':
                return Evaluation.of(experiment, default_variation_key, DecisionReason.EXPERIMENT_PAUSED)
            elif experiment.type == 'FEATURE_FLAG':
                return Evaluation.of(experiment, default_variation_key, DecisionReason.FEATURE_FLAG_INACTIVE)
            else:
                raise Exception('experiment type [{}]'.format(experiment.type))
        else:
            return next_flow.evaluate(workspace, experiment, user, default_variation_key)


class CompletedEvaluator(FlowEvaluator):
    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        if isinstance(experiment, CompletedExperiment):
            return Evaluation.with_variation(experiment.winner_variation, DecisionReason.EXPERIMENT_COMPLETED)
        else:
            return next_flow.evaluate(workspace, experiment, user, default_variation_key)


class ExperimentTargetEvaluator(FlowEvaluator):

    def __init__(self, experiment_target_determiner):
        self.experiment_target_determiner = experiment_target_determiner

    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        if not isinstance(experiment, RunningExperiment):
            raise Exception('experiment must be running [{}]'.format(experiment.id))

        if experiment.type != 'AB_TEST':
            raise Exception('experiment type must be AB_TEST [{}]'.format(experiment.id))

        is_user_in_experiment_target = self.experiment_target_determiner.is_user_in_experiment_target(workspace,
                                                                                                      experiment, user)
        if is_user_in_experiment_target:
            return next_flow.evaluate(workspace, experiment, user, default_variation_key)
        else:
            return Evaluation.of(experiment, default_variation_key, DecisionReason.NOT_IN_EXPERIMENT_TARGET)


class TrafficAllocateEvaluator(FlowEvaluator):

    def __init__(self, action_resolver):
        self.action_resolver = action_resolver

    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        if not isinstance(experiment, RunningExperiment):
            raise Exception('experiment must be running [{}]'.format(experiment.id))

        if experiment.type != 'AB_TEST':
            raise Exception('experiment type must be AB_TEST [{}]'.format(experiment.id))

        variation = self.action_resolver.resolve_or_none(experiment.default_rule, workspace, experiment, user)
        if not variation:
            return Evaluation.of(experiment, default_variation_key, DecisionReason.TRAFFIC_NOT_ALLOCATED)

        if variation.is_dropped:
            return Evaluation.of(experiment, default_variation_key, DecisionReason.VARIATION_DROPPED)

        return Evaluation.with_variation(variation, DecisionReason.TRAFFIC_ALLOCATED)


class TargetRuleEvaluator(FlowEvaluator):

    def __init__(self, target_rule_determiner, action_resolver):
        self.target_rule_determiner = target_rule_determiner
        self.action_resolver = action_resolver

    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        if not isinstance(experiment, RunningExperiment):
            raise Exception('experiment must be running [{}]'.format(experiment.id))

        if experiment.type != 'FEATURE_FLAG':
            raise Exception('experiment type must be FEATURE_FLAG [{}]'.format(experiment.id))

        target_rule = self.target_rule_determiner.determine_target_rule_or_none(workspace, experiment, user)
        if not target_rule:
            return next_flow.evaluate(workspace, experiment, user, default_variation_key)

        variation = self.action_resolver.resolve_or_none(target_rule.action, workspace, experiment, user)
        if not variation:
            raise Exception('FeatureFlag must decide the variation [{}]'.format(experiment.id))

        return Evaluation.with_variation(variation, DecisionReason.TARGET_RULE_MATCH)


class DefaultRuleEvaluator(FlowEvaluator):

    def __init__(self, action_resolver):
        self.action_resolver = action_resolver

    def evaluate(self, workspace, experiment, user, default_variation_key, next_flow):
        if not isinstance(experiment, RunningExperiment):
            raise Exception('experiment must be running [{}]'.format(experiment.id))

        if experiment.type != 'FEATURE_FLAG':
            raise Exception('experiment type must be FEATURE_FLAG [{}]'.format(experiment.id))

        variation = self.action_resolver.resolve_or_none(experiment.default_rule, workspace, experiment, user)
        if not variation:
            raise Exception('FeatureFlag must decide the variation [{}]'.format(experiment.id))

        return Evaluation.with_variation(variation, DecisionReason.DEFAULT_RULE)
