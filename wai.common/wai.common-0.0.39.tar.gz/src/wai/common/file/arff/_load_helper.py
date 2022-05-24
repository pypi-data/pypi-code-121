import re
from typing import IO, Set, Iterable, Optional, Tuple

from ._error import ARFFError
from . import constants

# The set of characters that can delimit a data value
DATA_DELIMITERS: Set[str] = {'\t', ',', '\n'}

# The set of quotation symbols
QUOTES: Set[str] = {'\"', '\''}

# Regular expression for matching a name (for a relation or attribute)
# (possibly surrounded by quotes)
NAME_PATTERN: str = '''
    (?P<quote>['"])?            # An optional beginning quote
    (?![{},%])                  # Must not start with '{', '}', ',' or '%'
    (?(quote)                   # If we are in quotes...
        .+?                     # Match any characters up to the first end-quote
        |                       # If we are not in quotes...
        (\\S)+                  # Match any non-whitespace characters
    )
    (?(quote)(?P=quote))        # Match the same ending quote as was found at the beginning (if there was one)
    '''

# Regular expression for matching the name in a line
# (possibly surrounded by quotes)
NOMINAL_VALUE_PATTERN: str = '''
    (?P<quote>['"])?            # An optional beginning quote
    (?(quote)                   # If we are in quotes...
        .+?                     # Match any characters up to the close quotation
        |                       # If we are not in quotes...
        [^\\s,}]+               # Match to the next space or delimiter
    )
    (?(quote)(?P=quote))        # Match the same ending quote as was found at the beginning (if there was one)
    '''

# Matches the attribute type portion of an attribute declaration
ATTRIBUTE_TYPE_PATTERN: str = '''
    (numeric|integer|real|string|date|{.*?})    # A type keyword or a nominal specification
    '''

# Regular expression which matches a data row value and its delimiter
DATA_VALUE_PATTERN: str = '''
    (?P<quote>['"])?            # An optional beginning quote
    .*?                         # Any characters can exist in the value (will be checked separately)
    (?(quote)(?P=quote))        # Match the same ending quote as was found at the beginning (if there was one)
    \\s*                        # Some possible trailing whitespace
    (\\t|,|\\n)                 # The delimiter is a tab, a comma, or a new line
    '''

# Regular expression which matches a date-format string
# TODO: Implement properly. csterling
DATE_FORMAT_PATTERN: str = '''
    .*          # Just match anything for now
    '''


def consume(line: str,
            pattern: str,
            ignore_leading_whitespace: bool = True,
            case_insensitive: bool = True) -> Tuple[Optional[str], str]:
    """
    Consumes the beginning portion of the line that is matched by the given pattern.

    :param line:                        The line to consume from the start of.
    :param pattern:                     The pattern to match for consumption.
    :param ignore_leading_whitespace:   Whether to drop any leading whitespace.
    :param case_insensitive:            Whether to ignore case.
    :return:                            The consumed part of the line, and the remainder.
    """

    # Remove leading whitespace if ignoring
    if ignore_leading_whitespace:
        line = line.lstrip()

    # Initialise the flags
    flags = re.VERBOSE
    if case_insensitive:
        flags |= re.IGNORECASE

    # Match the pattern
    match = re.match(pattern, line, flags)

    # Return the matched part of the line and the remainder
    if match:
        return line[:match.end()], line[match.end():]
    else:
        return None, line


def read_till_found(file: IO[str],
                    words: Set[str],
                    search_comments: bool = False,
                    case_insensitive: bool = True) -> str:
    """
    Reads lines from the ARFF file until a line is found that contains at least
    one of the given search words.

    :param file:                The ARFF file to read from.
    :param words:               The set of words to search for.
    :param search_comments:     Whether to allow the search to look inside comments as well.
    :param case_insensitive:    Whether the search should be case-insensitive.
    :return:                    The line where the word was found.
    """

    # Lower-case all search words if doing case-insensitive search
    if case_insensitive:
        words = {word.lower() for word in words}

    # Keep reading lines until we run out or find the desired line
    line = None
    while line != "":
        # Read the next line from the file
        line = file.readline()

        # Skip blank lines
        if is_whitespace_only(line):
            continue

        # Skip comments if we are not searching them
        if not search_comments:
            if is_comment_line(line):
                continue

        # Lower-case the searched line if doing case-insensitive search
        search_line = line.lower() if case_insensitive else line

        # If it contains one of the words, return it
        for word in words:
            if search_line.find(word) != -1:
                return line

    # None of the words were found
    raise KeywordNotFoundError(words)


def remove_quotes(string: str) -> str:
    """
    Removes quotes from around a string, if they are present.

    :param string:  The string to remove quotes from.
    :return:        The string without quotes.
    """

    # If starts and ends with double-quotes, remove them
    if string.startswith('\"') and string.endswith('\"'):
        string = string[1:-1]

    # If starts and ends with single-quotes, remove them
    elif string.endswith('\'') and string.endswith('\''):
        string = string[1:-1]

    # Return the (unquoted) string
    return string


def is_comment_line(line: str) -> bool:
    """
    Checks whether the given line is a comment line.

    :param line:    The line to check.
    :return:        True if the line is a comment line, False if not.
    """

    return line_starts_with(line, constants.COMMENT_SYMBOL, False)


def remove_keyword(line: str, keyword: str) -> str:
    """
    Removes the given keyword from the beginning of the line.

    :param line:        The line to remove the keyword from.
    :param keyword:     The keyword to remove.
    :return:            The line with the keyword removed.
    """

    # The line should start with the given keyword
    assert line_starts_with(line, keyword), line + ' does not start with keyword: ' + keyword

    # Return the line with the keyword removed
    return line[len(keyword):]


def is_whitespace_only(line: str) -> bool:
    """
    Checks if the given line contains only whitespace.

    :param line:    The line to check.
    :return:        True if the line contains only whitespace, False if not.
    """

    return line.strip() == ''


def line_starts_with(line: str, string: str, case_insensitive: bool = True) -> bool:
    """
    Checks if the line starts with the given string.

    :param line:                The line to check.
    :param string:              The string to look for.
    :param case_insensitive:    Whether the check should disregard case.
    :return:                    True if the line starts with the given string, False otherwise.
    """

    # Remove case information if case-insensitive
    if case_insensitive:
        line = line.lower()
        string = string.lower()

    # Return the result of the check
    return line.startswith(string)


class KeywordNotFoundError(ARFFError):
    """
    Exception where an expected keyword was never found in the ARFF file.
    """
    def __init__(self, keywords: Iterable[str]):
        # Format the message
        message = "Couldn't find line containing any of: " + ", ".join(keywords)
        super().__init__(message)


class UnrecognisedContentError(ARFFError):
    """
    Exception when part of a line cannot be parsed because it is not valid ARFF content.
    """
    def __init__(self, content: str, line: str):
        super().__init__("Unrecognised content '" + content + "' in line: " + line)
