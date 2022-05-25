from hackle.commons import validator, utils
from hackle.decision import ExperimentDecision, FeatureFlagDecision, DecisionReason
from hackle.event.user_event import ExposureEvent, TrackEvent


class InternalClient(object):

    def __init__(self, evaluator, workspace_fetcher, event_processor, logger):
        self.evaluator = evaluator
        self.workspace_fetcher = workspace_fetcher
        self.event_processor = event_processor
        self.logger = logger

    def close(self):
        self.workspace_fetcher.stop()
        self.event_processor.stop()

    def decide_experiment(self, experiment_key, user, default_variation_key):
        if not validator.is_non_zero_and_empty_int(experiment_key):
            self.logger.error('Experiment Key must not be empty. : {}'.format(experiment_key))
            return ExperimentDecision(default_variation_key, DecisionReason.INVALID_INPUT)

        if not validator.is_valid_user(user):
            self.logger.warning(
                'The user is not valid. user\'s type must be hackle.model.User and user.id\'s type must be '
                'string_types : {}'.format(user))
            return ExperimentDecision(default_variation_key, DecisionReason.INVALID_INPUT)

        if not validator.is_valid_properties(user.properties):
            self.logger.warning(
                'User properties is not valid. User properties must be not dic types and items types must be string_types, number, bool.'
                ': {}'.format(user.properties))
            user.properties = utils.filter_properties(user.properties)

        workspace = self.workspace_fetcher.get_workspace()
        if not workspace:
            self.logger.warning('Invalid Workspace. Hackle instance is not valid. {}'.format('variation'))
            return ExperimentDecision(default_variation_key, DecisionReason.SDK_NOK_READY)

        experiment = workspace.get_experiment_or_none(experiment_key)
        if not experiment:
            self.logger.debug('Could not find valid Experiment. "%s"' % experiment_key)
            return ExperimentDecision(default_variation_key, DecisionReason.EXPERIMENT_NOT_FOUND)

        evaluation = self.evaluator.evaluate(workspace, experiment, user, default_variation_key)
        self.event_processor.process(ExposureEvent(user, experiment, evaluation))

        return ExperimentDecision(evaluation.variation_key, evaluation.reason)

    def decide_feature_flag(self, feature_key, user):
        if not validator.is_non_zero_and_empty_int(feature_key):
            self.logger.error('Feature Key must not be empty. : {}'.format(feature_key))
            return FeatureFlagDecision(False, DecisionReason.INVALID_INPUT)

        if not validator.is_valid_user(user):
            self.logger.warning(
                'The user is not valid. user\'s type must be hackle.model.User and user.id\'s type must be '
                'string_types : {}'.format(user))
            return FeatureFlagDecision(False, DecisionReason.INVALID_INPUT)

        if not validator.is_valid_properties(user.properties):
            self.logger.warning(
                'User properties is not valid. User properties must be not dic types and items types must be string_types, number, bool.'
                ': {}'.format(user.properties))
            user.properties = utils.filter_properties(user.properties)

        workspace = self.workspace_fetcher.get_workspace()
        if not workspace:
            return FeatureFlagDecision(False, DecisionReason.SDK_NOK_READY)

        feature_flag = workspace.get_feature_flag_or_none(feature_key)
        if not feature_flag:
            return FeatureFlagDecision(False, DecisionReason.FEATURE_FLAG_NOT_FOUND)

        evaluation = self.evaluator.evaluate(workspace, feature_flag, user, 'A')
        self.event_processor.process(ExposureEvent(user, feature_flag, evaluation))

        if evaluation.variation_key == 'A':
            return FeatureFlagDecision(False, evaluation.reason)
        else:
            return FeatureFlagDecision(True, evaluation.reason)

    def track_event(self, event, user):
        if not validator.is_valid_event(event):
            self.logger.error('Event is not valid. Event must be hackle.model.event and event.id\'s type must be '
                              'string_types. value\'s type must be numeric. '
                              ': {}'.format(event))
            return

        if not validator.is_valid_user(user):
            self.logger.warning('User is not valid. user\'s type must be hackle.model.User and user.id\'s type must be '
                                'string_types : {}'.format(user))
            return

        if not validator.is_valid_properties(event.properties):
            self.logger.warning(
                'Event properties is not valid. Event properties must be not dic types and items types must be string_types, number, bool.'
                ': {}'.format(event.properties))
            event.properties = utils.filter_properties(event.properties)

        if not validator.is_valid_properties(user.properties):
            self.logger.warning(
                'User properties is not valid. User properties must be not dic types and items types must be string_types, number, bool.'
                ': {}'.format(user.properties))
            user.properties = utils.filter_properties(user.properties)

        config = self.workspace_fetcher.get_workspace()
        if not config:
            self.logger.warning('Invalid Workspace. Hackle instance is not valid. {}'.format('event'))
            return

        event_type = config.get_event_type_or_none(event.key)
        self.event_processor.process(TrackEvent(user, event_type, event))

        return
