from collections import namedtuple

from . import bucketer
from . import entities
from .commons import enums

Decision = namedtuple('Decision', 'experiment variation type')


class Decider(object):
    def __init__(self, logger):
        self.bucketer = bucketer.Bucketer()
        self.logger = logger

    def decide(self, experiment, user):
        if isinstance(experiment, entities.CompletedExperiment):
            return Decision(None, experiment.winnerVariationKey, enums.DecisionType.FORCED)

        if isinstance(experiment, entities.RunningExperiment):
            return self.__decide(experiment, user)

    def __decide(self, experiment, user):
        variation = experiment.userOverrides.get(user.id)
        if variation:
            return Decision(None, variation.key, enums.DecisionType.FORCED)

        slot = self.bucketer.bucketing(experiment.bucket, user.id)
        if not slot:
            return None

        variation = experiment.variations[slot.variationId]

        if not variation:
            return None

        if variation.isDropped:
            return None

        return Decision(experiment, variation, enums.DecisionType.NATURAL)
