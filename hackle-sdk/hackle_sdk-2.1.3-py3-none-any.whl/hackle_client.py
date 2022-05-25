from hackle.event.event_dispatcher import EventDispatcher
from . import decider
from . import exceptions as hackle_exceptions
from . import logger as _logging
from .commons import validator, enums
from .event import event_processor, event
from .workspace_fetcher import WorkspaceFetcher


class Client(object):
    def __init__(
            self,
            sdk_key=None,
            logger=None
    ):
        if sdk_key is None:
            raise hackle_exceptions.RequiredParameterException('sdk_key must not be empty')

        self.event_dispatcher = EventDispatcher()
        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())
        self.event_processor = event_processor.BatchEventProcessor(sdk_key, self.event_dispatcher, self.logger)
        self.decider = decider.Decider(self.logger)
        self.workspace_fetcher = WorkspaceFetcher(sdk_key, logger=self.logger)

    def close(self):
        self.workspace_fetcher.stop()
        self.event_processor.stop()

    def __exit__(self):
        self.close()

    def variation(self, experiment_key, user_id, default_variation='A'):
        if not validator.is_non_zero_and_empty_int(experiment_key):
            self.logger.error('Experiment Key Is Not Empty : {}'.format(experiment_key))
            return default_variation

        config = self.workspace_fetcher.get_config()
        if not config:
            self.logger.error('Invalid Workspace. Hackle instance is not valid. {}'.format('variation'))
            return default_variation

        experiment = config.get_experiment_from_key(experiment_key)

        if not experiment:
            self.logger.info('Experiment Key "%s" is invalid. Not Allocated.' % experiment_key)
            return default_variation

        decision = self.decider.decide(experiment, user_id)
        if not decision:
            return None

        if decision.type == enums.DecisionType.FORCED:
            return decision.variation
        elif decision.type == enums.DecisionType.NATURAL:
            self.event_processor.process(
                event.ExposureEvent(user_id, decision.experiment.id, decision.experiment.key, decision.variation.id,
                                    decision.variation.key))
            return decision.variation.key
        return None

    def track(self, event_key, user_id, value=None):
        if not validator.is_non_empty_string(event_key):
            self.logger.error('Event Key Is Not Empty : {}'.format(event_key))
            return

        config = self.workspace_fetcher.get_config()
        if not config:
            self.logger.error('Invalid Workspace. Hackle instance is not valid. {}'.format('event'))
            return

        event_type = config.get_event(event_key)
        if event_type:
            self.event_processor.process(
                event.TrackEvent(user_id, event_type.id, event_type.key, value)
            )

        return
