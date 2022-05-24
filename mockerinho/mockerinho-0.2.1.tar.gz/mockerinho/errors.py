
class MockerinhoError(Exception):
    """A base class for errors used by mockerinho."""


class MatcherError(MockerinhoError):
    """This is a base class for all errors related
    to request matchers."""


class IncorrectSuitableError(MatcherError):
    pass


class ConfigFileParserError(MockerinhoError):
    """A base class for all errors related to config file parser."""


class IncorrectConfigFileSchemaError(ConfigFileParserError):
    pass


class ParsingConfigFileError(ConfigFileParserError):
    pass
