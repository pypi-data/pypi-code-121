import re

# RFC 3986
SUB_DELIMITERS_PATTERN = r"!$&'()\*+,;="
UNRESERVED_PATTERN = r'A-Za-z0-9._~\-'

PCT_ENCODED = '%[A-Fa-f0-9]{2}'
PCHAR = '([%s%s:@]|%s)' % (
    UNRESERVED_PATTERN, SUB_DELIMITERS_PATTERN, PCT_ENCODED
)

segments = {
    'segment': PCHAR + '*',
    'segment-nz': PCHAR + '+',
    'segment-nz-nc': PCHAR.replace(':', '') + '+',
}

# https://datatracker.ietf.org/doc/html/rfc3986#section-3.3
PATH_ABEMPTY = '(/%(segment)s)*' % segments
PATH_ROOTLESS = '%(segment-nz)s(/%(segment)s)*' % segments
PATH_NOSCHEME = '%(segment-nz-nc)s(/%(segment)s)*' % segments
PATH_ABSOLUTE = '/(%s)?' % PATH_ROOTLESS
PATH_EMPTY = '^$'
PATH_PATTERN = '^({}|{}|{}|{}|{})$'.format(
    PATH_ABEMPTY,
    PATH_ABSOLUTE,
    PATH_NOSCHEME,
    PATH_ROOTLESS,
    PATH_EMPTY,
)

PATH_REGEXP = re.compile(PATH_PATTERN)


def is_request_path_valid(path: str) -> bool:
    matches = bool(PATH_REGEXP.match(path))
    return matches


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
ALLOWED_HTTP_METHODS = (
    'GET',
    'HEAD',
    'POST',
    'PUT',
    'DELETE',
    'CONNECT',
    'OPTIONS',
    'TRACE',
    'PATCH',
)


def is_request_method_valid(method: str) -> bool:
    contains = method.upper() in ALLOWED_HTTP_METHODS
    return contains


# RFC 7230
ALPHA = 'a-zA-Z'
DIGIT = r'\d'

HEADER_NAME_SPECIAL_CHARACTERS_PATTERN = '_-'
HEADER_NAME_PATTERN = '^[%s%s]+$' % (
    ALPHA, HEADER_NAME_SPECIAL_CHARACTERS_PATTERN
)
HEADER_NAME_REGEXP = re.compile(HEADER_NAME_PATTERN)

HEADER_VALUE_SPECIAL_CHARACTERS_PATTERN = r"_\s:;\.,\/\"'\?!\(\){}\[\]@<>=\-\+\*#\$&`\|~\^%"
HEADER_VALUE_PATTERN = '^[%s%s%s]+$' % (
    ALPHA, DIGIT, HEADER_VALUE_SPECIAL_CHARACTERS_PATTERN
)
HEADER_VALUE_REGEXP = re.compile(HEADER_VALUE_PATTERN)


def is_header_name_valid(header_name: str) -> bool:
    matches = bool(HEADER_NAME_REGEXP.match(header_name))
    return matches


def is_header_value_valid(header_value: str) -> bool:
    matches = bool(HEADER_VALUE_REGEXP.match(header_value))
    return matches


ALLOWED_HEADER_VALUE_MATCHERS = ('exact', 'regexp')


def is_header_value_matcher_valid(header_value_matcher: str) -> bool:
    contains = header_value_matcher.lower() in ALLOWED_HEADER_VALUE_MATCHERS
    return contains


# Disabled due to circumstances determination
# QUERY_PATTERN = '^([/?:@%s%s]|%s)*$' % (
#     UNRESERVED_PATTERN, SUB_DELIMITERS_PATTERN, PCT_ENCODED
# )


def is_query_name_valid(query_name: str) -> bool:
    is_valid = True
    return is_valid


def is_query_value_valid(query_key: str) -> bool:
    is_valid = True
    return is_valid


ALLOWED_QUERY_VALUE_MATCHERS = ('exact', 'regexp')


def is_query_value_matcher_valid(query_value_matcher: str) -> bool:
    contains = query_value_matcher.lower() in ALLOWED_QUERY_VALUE_MATCHERS
    return contains


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
INFORMATIONAL = (
    100, 101, 102, 103,
)
SUCCESSFUL = (
    200, 201, 202, 203, 204, 205, 206, 207, 208, 226,
)
REDIRECTION = (
    300, 301, 302, 303, 304, 305, 306, 307, 308,
)
CLIENT_ERROR = (
    400, 401, 402, 403, 404, 405,
    406, 407, 408, 409, 410, 411,
    412, 413, 414, 415, 416, 417,
    418, 421, 422, 423, 424, 425,
    426, 428, 429, 431, 449, 451,
)
SERVER_ERROR = (
    500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511,
)
VALID_HTTP_STATUS_CODES = (
    *INFORMATIONAL,
    *SUCCESSFUL,
    *REDIRECTION,
    *CLIENT_ERROR,
    *SERVER_ERROR,
)


def is_status_code_valid(status_code: int) -> bool:
    contains = status_code in VALID_HTTP_STATUS_CODES
    return contains


ALLOWED_BODY_VALUE_MATCHERS = ('exact', 'regexp', 'json')


def is_request_body_value_matcher_valid(body_value_matcher: str) -> bool:
    contains = body_value_matcher.lower() in ALLOWED_BODY_VALUE_MATCHERS
    return contains
