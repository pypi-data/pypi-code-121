"""Utilities to load AIML data."""
import json
from typing import Set, Mapping


def _normalize_string(s: str) -> str:
    """Uppercase and remove extra spaces from s."""
    s = s.upper()
    return " ".join(s.split())


def aiml_set_fromstring(s: str) -> Set[str]:
    r"""Guess the format and parse the AIML set.

    The loaded set is normalized -- in the sense that letters
    are uppercase-d and extra spaces removed.

    Supported formats include:
        1) ALICE format: one line per phrase,
        2) Pandorabots format [json]: list of strings,
            or list of lists of words

    :param s: string with AIML set
    :return: parsed AIML set
    :raises: ValueError if `s` does not represent an AIML set

    Examples:
        >>> s = "a\nb\nc"
        >>> aiml_set_fromstring(s) == { "A", "B", "C" }
        True

        >>> s = '[["a"], ["b", "c"]]'
        >>> aiml_set_fromstring(s) == { "A", "B C" }
        True

        >>> aiml_set_fromstring("") == set()
        True
        >>> aiml_set_fromstring("a") == {"A"}
        True
        >>> aiml_set_fromstring("a\n") == {"A"}
        True
    """
    if not s:
        return set()
    if "[" not in s:
        # each line has one phrase
        elems = map(_normalize_string, s.split("\n"))
        return set(filter(lambda x: len(x) > 0, elems))

    try:
        loaded = json.loads(s)
        assert isinstance(loaded, list)
        content = (" ".join(x) if isinstance(x, list) else x for x in loaded)
        elems = map(_normalize_string, content)
        return set(filter(lambda x: len(x) > 0, elems))
    except Exception as e:
        raise ValueError("Not supported AIML Set format") from e


def load_aiml_set(filename: str) -> Set[str]:
    """Try to load AIML set and guess its format.

    The loaded set is normalized -- in the sense that letters
    are uppercase-d and extra spaces removed.

    See `aiml_set_fromstring` for examples of usage.

    Supported formats include:
        1) ALICE format: one line per phrase,
        2) Pandorabots format [json]: list of strings,
            or list of lists of words

    :param filename: name of file to parse
    :return: parsed AIML set
    :raises: ValueError if `filename` does not represent an AIML set
    """
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
        return aiml_set_fromstring(content)


def aiml_map_fromstring(s: str) -> Mapping[str, str]:
    r"""Guess the format and parse AIML map from the given string.

    The loaded keys are normalized -- letters
    are uppercased and extra spaces removed.

    Records with empty keys are discarded.

    Supported formats include:
        1) ALICE format: key:value per each line,
        2) Pandorabots format [json]: list of lists with 2 strings each

    To Alice format: the first (:) is the separator between words, that is
        >>> text = "a:b:c"
        >>> aiml_map_fromstring(text) == dict(A="b:c")
        True

    :param s: string representing AIML map
    :return: parsed map
    :raises: ValueError if `s` does not represent an AIML map

    Examples:
        >>> s = "a:1\nb:c\nd:e"
        >>> aiml_map_fromstring(s) == dict(A="1", B="c", D="e")
        True

        >>> s = '[["key1", "val1"], ["key2    extra", "val2"]]'
        >>> aiml_map_fromstring(s) == { "KEY1": "val1", "KEY2 EXTRA": "val2"}
        True
    """
    if not s:
        return dict()

    try:
        if "[" not in s:
            aiml_map = {}
            for line in s.split("\n"):
                if not line.strip():  # empty lines
                    continue
                splitted = line.split(":", maxsplit=1)
                assert len(splitted) == 2
                key, value = splitted
                key = _normalize_string(key)
                if key:
                    aiml_map[key] = value
            return aiml_map

        loaded_json = json.loads(s)
        assert isinstance(loaded_json, list)

        aiml_map = {}
        for entry in loaded_json:
            assert isinstance(entry, list)
            assert len(entry) == 2
            key, value = entry
            key = _normalize_string(key)
            if key:
                aiml_map[key] = value
        return aiml_map
    except Exception as e:
        raise ValueError("Not supported AIML map format") from e


def load_aiml_map(filename: str) -> Mapping[str, str]:
    """Guess the format and parse AIML map from the given file.

    See `aiml_map_fromstring` for examples.

    Supported formats include:
        1) ALICE format: key:value per each line,
        2) Pandorabots format [json]: list of lists with 2 strings each

    :param filename: file with AIML map
    :return: parsed map
    :raises: ValueError if `filename` does not represent an AIML map
    """
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
        return aiml_map_fromstring(content)


def aiml_sub_fromstring(s: str) -> Mapping[str, str]:
    r"""Guess the format and parse AIML substitutions from the given string.

    :param s: string representing AIML substitutions
    :return: parsed substitutions
    :raises: ValueError if `s` does not represent an AIML substitutions

    Examples:
        >>> s = " a :1\nb: c \nd:e"
        >>> aiml_sub_fromstring(s) == {" a ": "1", "b": " c ", "d": "e"}
        True
    """
    if not s:
        return dict()

    try:
        if "[" not in s:
            aiml_map = {}
            for line in s.split("\n"):
                split = line.split(":", maxsplit=1)
                key, value = map(lambda s: s.strip('"'), split)
                if key:
                    aiml_map[key] = value
            return aiml_map

        loaded_json = json.loads(s)
        assert isinstance(loaded_json, list)

        aiml_map = {}
        for entry in loaded_json:
            assert isinstance(entry, list)
            assert len(entry) == 2
            key, value = entry
            if key:
                aiml_map[key] = value
        return aiml_map
    except Exception as e:
        raise ValueError("Not supported AIML subs format") from e


def load_aiml_sub(filename: str) -> Mapping[str, str]:
    """Guess the format and parse AIML substitutions from the given file.

    See `aiml_sub_fromstring` for examples.

    :param filename: file with AIML subs
    :return: parsed subs
    :raises: ValueError if `filename` does not represent an AIML subs
    """
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
        return aiml_sub_fromstring(content)
