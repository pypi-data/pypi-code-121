from hackle import logger as _logging


class TargetMatcher(object):

    def __init__(self, condition_matcher_factory, logger=None):
        self.condition_matcher_factory = condition_matcher_factory
        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())

    def matches(self, target, workspace, user):
        for condition in target.conditions:
            if not self._matches(condition, workspace, user):
                return False
        return True

    def _matches(self, condition, workspace, user):
        condition_matcher = self.condition_matcher_factory.get_condition_matcher_or_none(condition.key.type)
        if not condition_matcher:
            self.logger.debug('Unsupported type [{}]. Please use the latest version of sdk.'.format(condition.key.type))
            return False

        return condition_matcher.matches(condition, workspace, user)
