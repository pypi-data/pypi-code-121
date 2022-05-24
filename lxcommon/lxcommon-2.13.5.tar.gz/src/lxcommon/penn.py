ESCAPE_BRACKETS = {
    "(": "-lrb-",
    ")": "-rrb-",
    "[": "-lsb-",
    "]": "-rsb-",
    "{": "-lcb-",
    "}": "-rcb-",
}

UNESCAPE_BRACKETS = {
    "-lrb-": "(",
    "-rrb-": ")",
    "-lsb-": "[",
    "-rsb-": "]",
    "-lcb-": "{",
    "-rcb-": "}",
}


def escape_token(token):
    return ESCAPE_BRACKETS.get(token, token)


def unescape_token(token):
    return UNESCAPE_BRACKETS.get(token, token)
