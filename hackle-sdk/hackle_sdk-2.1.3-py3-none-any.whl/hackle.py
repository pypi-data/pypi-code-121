from hackle.evaluation.evaluator import Evaluator
from hackle.evaluation.flow.evaluation_flow_factory import EvaluationFlowFactory
from hackle import exceptions as hackle_exceptions
from hackle import logger as _logging
from hackle.decision import ExperimentDecision, DecisionReason, FeatureFlagDecision
from hackle.event.event_dispatcher import EventDispatcher
from hackle.event.event_processor import BatchEventProcessor
from hackle.internal_client import InternalClient
from hackle.workspace_fetcher import WorkspaceFetcher


def __singleton(cls):
    instance = [None]

    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper


@__singleton
class Client(object):
    def __init__(self, sdk_key=None, logger=None, timeout=None):
        if sdk_key is None:
            raise hackle_exceptions.RequiredParameterException('sdk_key must not be empty.')

        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())

        self.internal_client = InternalClient(
            evaluator=Evaluator(EvaluationFlowFactory(self.logger)),
            workspace_fetcher=WorkspaceFetcher(sdk_key, logger=self.logger, timeout=timeout),
            event_processor=BatchEventProcessor(sdk_key, EventDispatcher(), self.logger),
            logger=self.logger
        )

    def close(self):
        self.internal_client.close()

    def __exit__(self):
        self.close()

    def variation(self, experiment_key, user, default_variation='A'):
        """
        Decide the variation to expose to the user for experiment.

        This method return the "A" if:
            - The experiment key is invalid
            - The experiment has not started yet
            - The user is not allocated to the experiment
            - The decided variation has been dropped

        :param int experiment_key: the unique key of the experiment.
        :param hackle.model.User user: the user to participate in the experiment.
        :param str default_variation: the default variation of the experiment.

        :return: the decided variation for the user, or the default variation.
        """
        return self.variation_detail(experiment_key, user, default_variation).variation

    def variation_detail(self, experiment_key, user, default_variation='A'):
        """
        Decide the variation to expose to the user for experiment, and returns an object that
        describes the way the variation was decided.

        :param int experiment_key: the unique key of the experiment.
        :param hackle.model.User user: the user to participate in the experiment.
        :param str default_variation: the default variation of the experiment.

        :return: a object describing the result
        """
        try:
            return self.internal_client.decide_experiment(experiment_key, user, default_variation)
        except Exception as e:
            self.logger.error(
                "Unexpected error while deciding variation of experiment[{}]: {}".format(experiment_key, str(e)))
            return ExperimentDecision(default_variation, DecisionReason.EXCEPTION)

    def is_feature_on(self, feature_key, user):
        """
        Decide whether the feature is turned on to the user.

        :param int feature_key: the unique key of the feature.
        :param hackle.model.User user: the user requesting the feature.
        :return: True if the feature is on
                  False if the feature is off
        """
        return self.feature_flag_detail(feature_key, user).is_on

    def feature_flag_detail(self, feature_key, user):
        """
        Decide whether the feature is turned on to the user, and returns an object that
        describes the way the value was decided.

        :param int feature_key: the unique key of the feature.
        :param hackle.model.User user: the user requesting the feature.

        :return: a object describing the result
        """
        try:
            return self.internal_client.decide_feature_flag(feature_key, user)
        except Exception as e:
            self.logger.error("Unexpected error while deciding feature flag[{}]: {}".format(feature_key, str(e)))
            return FeatureFlagDecision(False, DecisionReason.EXCEPTION)

    def track(self, event, user):
        """
        Records the event performed by the user with additional numeric value.

        :param hackle.model.Event event: the unique key of the event. MUST NOT be null.
        :param user: the identifier of user that performed the event. MUST NOT be null.
        """
        try:
            self.internal_client.track_event(event, user)
        except Exception as e:
            self.logger.error('Unexpected error while tracking event: {}'.format(str(e)))
