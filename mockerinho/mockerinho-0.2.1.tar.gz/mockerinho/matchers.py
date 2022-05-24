import json
import re
import typing as t

from . import errors


class ExactMatcher:
    def __init__(self, suitable: str) -> None:
        self.__suitable_string = suitable

    def matches(self, captured: str) -> bool:
        return self.__suitable_string == captured


class RegexpMatcher:
    def __init__(self, suitable: str) -> None:
        try:
            suitable_regexp = re.compile(suitable)
        except re.error:
            raise errors.IncorrectSuitableError(
                'The "suitable" must be a valid regexp pattern.'
            )

        self.__suitable_regexp = suitable_regexp

    def matches(self, captured: str) -> bool:
        return bool(self.__suitable_regexp.match(captured))


class JsonMatcher:
    def __init__(self, suitable: str) -> None:
        suitable_json = JsonMatcher.__try_json_loads(suitable)

        if suitable_json is None:
            raise errors.IncorrectSuitableError(
                'The "suitable" must be a valid json string.'
            )

        self.__suitable_json = suitable_json

    def matches(self, captured: str) -> bool:
        captured_json = JsonMatcher.__try_json_loads(captured)

        if captured_json is None:
            return False

        captured_deep_equal_to_suitable = self.__suitable_json == captured_json

        return captured_deep_equal_to_suitable

    @staticmethod
    def __try_json_loads(s: str) -> t.Optional[dict]:
        try:
            loaded = json.loads(s)
        except json.JSONDecodeError:
            loaded = None

        return loaded


matcher_classes = {
    'exact': ExactMatcher,
    'regexp': RegexpMatcher,
    'json': JsonMatcher
}
