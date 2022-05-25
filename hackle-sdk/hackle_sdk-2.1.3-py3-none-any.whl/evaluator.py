from hackle.decision import DecisionReason
from hackle.entities import DraftExperiment, RunningExperiment, PausedExperiment, CompletedExperiment


class Evaluation(object):
    def __init__(self, variation_id, variation_key, reason):
        self.variation_id = variation_id
        self.variation_key = variation_key
        self.reason = reason

    def __eq__(self, o):
        if isinstance(o, self.__class__):
            return self.__dict__ == o.__dict__
        else:
            return False

    @staticmethod
    def with_key(variation_key, reason):
        return Evaluation(variation_id=None, variation_key=variation_key, reason=reason)

    @staticmethod
    def with_variation(variation, reason):
        return Evaluation(variation_id=variation.id, variation_key=variation.key, reason=reason)


class Evaluator(object):
    def __init__(self, bucketer, logger):
        self.bucketer = bucketer
        self.logger = logger

    def evaluate(self, experiment, user, default_variation_key):
        variation = experiment.get_overridden_variation_or_none(user.id)
        if variation:
            return Evaluation.with_key(variation.key, DecisionReason.OVERRIDDEN)

        if isinstance(experiment, DraftExperiment):
            return Evaluation.with_key(default_variation_key, DecisionReason.EXPERIMENT_DRAFT)
        elif isinstance(experiment, RunningExperiment):
            return self.__evaluate(experiment, user, default_variation_key)
        elif isinstance(experiment, PausedExperiment):
            return Evaluation.with_key(default_variation_key, DecisionReason.EXPERIMENT_PAUSED)
        elif isinstance(experiment, CompletedExperiment):
            return Evaluation.with_key(experiment.winner_variation.key, DecisionReason.EXPERIMENT_COMPLETED)
        else:
            raise Exception('Unsupported experiment')

    def __evaluate(self, experiment, user, default_variation_key):
        allocated_slot = self.bucketer.bucketing(experiment.bucket, user.id)
        if not allocated_slot:
            return Evaluation.with_key(default_variation_key, DecisionReason.TRAFFIC_NOT_ALLOCATED)

        allocated_variation = experiment.get_variation_or_none(allocated_slot.variation_id)
        if not allocated_variation:
            return Evaluation.with_key(default_variation_key, DecisionReason.TRAFFIC_NOT_ALLOCATED)

        if allocated_variation.is_dropped:
            return Evaluation.with_key(default_variation_key, DecisionReason.VARIATION_DROPPED)

        return Evaluation.with_variation(allocated_variation, DecisionReason.TRAFFIC_ALLOCATED)
