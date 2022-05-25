from hackle import logger as _logging
from hackle.evaluation.match.operator_matcher import *
from hackle.evaluation.match.value_matcher import *


class ValueOperatorMatcher(object):

    def __init__(self, factory, logger=None):
        self.factory = factory
        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())

    def matches(self, user_value, match):
        value_matcher = self.factory.get_value_matcher_or_none(match.value_type)
        if not value_matcher:
            self.logger.debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(match.value_type))
            return False

        operator_matcher = self.factory.get_operator_matcher_or_none(match.operator)
        if not operator_matcher:
            self.logger.debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(match.operator))
            return False

        for match_value in match.values:
            if value_matcher.matches(operator_matcher, user_value, match_value):
                return self._matches(match.type, True)

        return self._matches(match.type, False)

    def _matches(self, match_type, is_matched):
        if match_type == 'MATCH':
            return is_matched
        elif match_type == 'NOT_MATCH':
            return not is_matched
        else:
            self.logger.debug('Unsupported type[{}]. Please use the latest version of sdk.'.format(match_type))
            return False


class ValueOperatorMatcherFactory(object):

    def __init__(self):
        self._value_matchers = {
            'STRING': StringValueMatcher(),
            'NUMBER': NumberValueMatcher(),
            'BOOLEAN': BoolValueMatcher()
        }
        self._operator_matchers = {
            'IN': InMatcher(),
            'CONTAINS': ContainsMatcher(),
            'STARTS_WITH': StartsWithMatcher(),
            'ENDS_WITH': EndsWithMatcher(),
            'GT': GreaterThanMatcher(),
            'GTE': GreaterThanOrEqualToMatcher(),
            'LT': LessThanMatcher(),
            'LTE': LessThanOrEqualToMatcher()
        }

    def get_value_matcher_or_none(self, value_type):
        return self._value_matchers.get(value_type)

    def get_operator_matcher_or_none(self, operator):
        return self._operator_matchers.get(operator)
