_PARSERS = dict()


class Parser:
    def __init__(self, name, parser_function, is_active, is_deprecated, is_native):
        self.name = name
        self.parser_function = parser_function
        self.is_active = is_active
        self.is_deprecated = is_deprecated
        self.is_native = is_native


def parser(name, is_active=True, is_deprecated=False, is_native=True):
    def wrapper(func):
        _PARSERS[name] = Parser(name, func, is_active, is_deprecated, is_native)
        return func

    return wrapper
