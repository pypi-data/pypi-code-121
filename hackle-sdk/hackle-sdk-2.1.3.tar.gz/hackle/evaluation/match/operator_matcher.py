import abc
from numbers import Number


class OperatorMatcher(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def string_matches(self, user_value, match_value):
        pass

    @abc.abstractmethod
    def number_matches(self, user_value, match_value):
        pass

    @abc.abstractmethod
    def bool_matches(self, user_value, match_value):
        pass


class InMatcher(OperatorMatcher):
    def string_matches(self, user_value, match_value):
        if isinstance(user_value, str) and isinstance(match_value, str):
            return user_value == match_value
        else:
            return False

    def number_matches(self, user_value, match_value):
        if isinstance(user_value, Number) and isinstance(match_value, Number):
            return user_value == match_value
        else:
            return False

    def bool_matches(self, user_value, match_value):
        if isinstance(user_value, bool) and isinstance(match_value, bool):
            return user_value == match_value
        else:
            return False


class ContainsMatcher(OperatorMatcher):
    def string_matches(self, user_value, match_value):
        if isinstance(user_value, str) and isinstance(match_value, str):
            return match_value in user_value
        else:
            return False

    def number_matches(self, user_value, match_value):
        return False

    def bool_matches(self, user_value, match_value):
        return False


class StartsWithMatcher(OperatorMatcher):
    def string_matches(self, user_value, match_value):
        if isinstance(user_value, str) and isinstance(match_value, str):
            return user_value.startswith(match_value)
        else:
            return False

    def number_matches(self, user_value, match_value):
        return False

    def bool_matches(self, user_value, match_value):
        return False


class EndsWithMatcher(OperatorMatcher):
    def string_matches(self, user_value, match_value):
        if isinstance(user_value, str) and isinstance(match_value, str):
            return user_value.endswith(match_value)
        else:
            return False

    def number_matches(self, user_value, match_value):
        return False

    def bool_matches(self, user_value, match_value):
        return False


class GreaterThanMatcher(OperatorMatcher):
    def string_matches(self, user_value, match_value):
        return False

    def number_matches(self, user_value, match_value):
        if isinstance(user_value, Number) and isinstance(match_value, Number):
            return user_value > match_value
        else:
            return False

    def bool_matches(self, user_value, match_value):
        return False


class GreaterThanOrEqualToMatcher(OperatorMatcher):
    def string_matches(self, user_value, match_value):
        return False

    def number_matches(self, user_value, match_value):
        if isinstance(user_value, Number) and isinstance(match_value, Number):
            return user_value >= match_value
        else:
            return False

    def bool_matches(self, user_value, match_value):
        return False


class LessThanMatcher(OperatorMatcher):
    def string_matches(self, user_value, match_value):
        return False

    def number_matches(self, user_value, match_value):
        if isinstance(user_value, Number) and isinstance(match_value, Number):
            return user_value < match_value
        else:
            return False

    def bool_matches(self, user_value, match_value):
        return False


class LessThanOrEqualToMatcher(OperatorMatcher):
    def string_matches(self, user_value, match_value):
        return False

    def number_matches(self, user_value, match_value):
        if isinstance(user_value, Number) and isinstance(match_value, Number):
            return user_value <= match_value
        else:
            return False

    def bool_matches(self, user_value, match_value):
        return False
