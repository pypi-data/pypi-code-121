""" formatter.py : String formatter util module
Allows you to insert dynamic values inside strings
"""
# Built-in imports
from typing import Optional
from copy import deepcopy

# third parties imports
import numpy as np

# Own package imports
from mfire.settings import get_logger, TEMPLATES_FILENAMES, Settings
from mfire.utils.date import Datetime
from mfire.utils.json_utils import JsonFile


# Logging
LOGGER = get_logger(name="formatter.mod", bind="formatter")

SYNONYMS = JsonFile(TEMPLATES_FILENAMES[Settings().language]["synonyms"]).load()


def find_synonyms(word: str) -> tuple:
    """function that finds all the synonym of a given word

    Args:
        word (str): word

    Returns:
        tuple: tuple of all synonyms
    """
    return next((seq for seq in SYNONYMS if word in seq), (word,))


def get_synonym(word: str) -> str:
    """returns a random synonym

    Args:
        word (str): word

    Returns:
        str: synonym of the given word
    """
    return np.random.choice(find_synonyms(word))


def match_text(text1: str, text2: str, synonyms: Optional[tuple] = None) -> bool:
    """Function for checking if a text matches with a given template.
    For instance:
    >>> text1 = "Toto aime Tata"
    >>> text2 = "Toto apprécie Tata"
    >>> text3 = "Toto déteste Tata"
    >>> synonyms = (("aime", "apprécie"), ("n'aime pas", "déteste"))
    >>> match_text(text1, text2, synonyms)
    True
    >>> match_text(text1, text3, synonyms)
    False
    >>> ...

    Useful for tests and avoiding random synonyms.

    Args:
        text1 (str): Text to compare with template.
        text2 (str): Template with tags between '<...>'
        tags (Optional[tuple]): Mapping between tags and possible values.
    """
    if synonyms is None:
        synonyms = SYNONYMS
    ntext1, ntext2 = text1, text2
    for seq in synonyms:
        tag = f"<{seq[0]}>"
        for word in seq:
            ntext1 = ntext1.replace(word, tag)
            ntext2 = ntext2.replace(word, tag)
    return ntext1 == ntext2


class TagFormatter:
    """ TagFormatter: Format a str containing tags of type '[key:func]'.
    Its like the vortex standard.
    """

    time_format: dict = {
        "fmth": "{:04d}",
        "fmthm": "{:04d}:00",
        "fmthhmm": "{:02d}:00",
        "fmtraw": "{:04d}00",
    }
    datetime_format: dict = {
        "julian": "%j",
        "ymd": "%Y%m%d",
        "yymd": "%y%m%d",
        "y": "%Y",
        "ymdh": "%Y%m%d%H",
        "yymdh": "%y%m%d%H",
        "ymdhm": "%Y%m%d%H%M",
        "ymdhms": "%Y%m%d%H%M%S",
        "mmddhh": "%m%d%H",
        "mm": "%m",
        "hm": "%H%M",
        "dd": "%d",
        "hh": "%H",
        "h": "%-H",
        "vortex": "%Y%m%dT%H%M%S",
        "stdvortex": "%Y%m%dT%H%M",
        "iso8601": "%Y-%m-%dT%H:%M:%SZ",
    }

    def format_tags(self, original_text: str, tags: dict = None) -> str:
        """format_tags : Format a str containing tags of type '[key:func]'.
        Its like the vortex standard.

        Args:
            original_text (str): Str to format
            tags (dict, optional): Dictionnary (key, value) containing the
            values to insert in the str. The values formatting is done
            according to the tags_format_conf. Defaults to dict().

        Returns:
            str: formatted str
        """
        text = deepcopy(original_text)

        if not tags:
            return text

        for key, value in tags.items():
            # Raw key formatting
            text = text.replace("[{}]".format(key), str(value))

            # Time formatting
            if isinstance(value, int):
                for func, fmt in self.time_format.items():
                    text = text.replace("[{}:{}]".format(key, func), fmt.format(value))

            # Datetime formatting
            try:
                value_dt = Datetime(value)
                for func, fmt in self.datetime_format.items():
                    text = text.replace(
                        "[{}:{}]".format(key, func), value_dt.strftime(fmt)
                    )
            except TypeError:
                pass
            except ValueError:
                pass

            # Geometry formatting
            text = text.replace("[{}:area]".format(key), str(value).upper())

        return text
