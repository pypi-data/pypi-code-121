# pylint: skip-file


class DatetimeParserError(Exception):
    pass


class InvalidYearError(DatetimeParserError):
    pass


class AmbiguousDateError(DatetimeParserError):
    pass


class MultipleDatesError(DatetimeParserError):
    pass


class MultipleDatePartsError(DatetimeParserError):
    pass


class MultipleTimesFoundError(DatetimeParserError):
    pass


class InvalidTimeError(DatetimeParserError):
    pass


class InvalidOffsetError(DatetimeParserError):
    pass


class MultipleOffsetsError(DatetimeParserError):
    pass


class InvalidDateError(DatetimeParserError):
    pass


class TimestampBuildError(DatetimeParserError):
    pass


class AmbiguousFoldError(DatetimeParserError):
    pass


class OffsetNotKnownError(DatetimeParserError):
    pass


class AmbiguousDatetimeFormatsError(DatetimeParserError):
    pass
