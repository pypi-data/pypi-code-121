import abc

from hackle import logger as _logging
from hackle.evaluation.match.value_operator_matcher import ValueOperatorMatcher, ValueOperatorMatcherFactory


class ConditionMatcher(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def matches(self, condition, workspace, user):
        pass


class PropertyConditionMatcher(ConditionMatcher):
    def __init__(self, value_operator_matcher, logger=None):
        self.value_operator_matcher = value_operator_matcher
        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())

    def matches(self, condition, workspace, user):
        user_value = self._resolve_property_or_none(user, condition.key)
        if not user_value:
            return False

        return self.value_operator_matcher.matches(user_value, condition.match)

    def _resolve_property_or_none(self, user, target_key):
        if target_key.type == 'USER_PROPERTY':
            return user.properties.get(target_key.name)
        elif target_key.type == 'HACKLE_PROPERTY':
            return None
        else:
            self.logger.debug('Unsupported type [{}]. Please use the latest version of sdk.'.format(target_key))
            return None


class ConditionMatcherFactory(object):

    def __init__(self, logger=None):
        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())

        self.property_condition_matcher = PropertyConditionMatcher(
            ValueOperatorMatcher(ValueOperatorMatcherFactory(), self.logger),
            self.logger)

    def get_condition_matcher_or_none(self, target_key_type):
        if target_key_type == 'USER_PROPERTY':
            return self.property_condition_matcher
        elif target_key_type == 'HACKLE_PROPERTY':
            return self.property_condition_matcher
        else:
            return None
