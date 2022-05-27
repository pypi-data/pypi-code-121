from __future__ import annotations

import datetime
import math
import typing

from .. import spec
from . import timelength_units
from . import timelength_identify


#
# # general conversions
#


@typing.overload
def convert_timelength(
    timelength: spec.Timelength,
    to_representation: typing.Literal['TimelengthSeconds'],
    from_representation: typing.Optional[spec.TimelengthRepresentation],
) -> spec.TimelengthSeconds:
    ...


@typing.overload
def convert_timelength(
    timelength: spec.Timelength,
    to_representation: typing.Literal['TimelengthSecondsPrecise'],
    from_representation: typing.Optional[spec.TimelengthRepresentation],
) -> spec.TimelengthSecondsPrecise:
    ...


@typing.overload
def convert_timelength(
    timelength: spec.Timelength,
    to_representation: typing.Literal['TimelengthLabel'],
    from_representation: typing.Optional[spec.TimelengthRepresentation],
) -> spec.TimelengthLabel:
    ...


@typing.overload
def convert_timelength(
    timelength: spec.Timelength,
    to_representation: typing.Literal['TimelengthClock'],
    from_representation: typing.Optional[spec.TimelengthRepresentation],
) -> spec.TimelengthClock:
    ...


@typing.overload
def convert_timelength(
    timelength: spec.Timelength,
    to_representation: typing.Literal['TimelengthPhrase'],
    from_representation: typing.Optional[spec.TimelengthRepresentation],
) -> spec.TimelengthPhrase:
    ...


@typing.overload
def convert_timelength(
    timelength: spec.Timelength,
    to_representation: typing.Literal['TimelengthClockPhrase'],
    from_representation: typing.Optional[spec.TimelengthRepresentation],
) -> spec.TimelengthClockPhrase:
    ...


@typing.overload
def convert_timelength(
    timelength: spec.Timelength,
    to_representation: typing.Literal['TimelengthTimedelta'],
    from_representation: typing.Optional[spec.TimelengthRepresentation],
) -> spec.TimelengthTimedelta:
    ...


def convert_timelength(
    timelength: spec.Timelength,
    to_representation: spec.TimelengthRepresentation,
    from_representation: typing.Optional[spec.TimelengthRepresentation] = None,
) -> spec.Timelength:
    """convert Timelength to a new representation

    ## Inputs
    - timelength: Timelength
    - to_representation: str of Timelength representation of input timelength
    - from_representation: str of target Timelength representation

    ## Returns
    - Timelength in specified representation
    """

    # detect timelength type
    if from_representation is None:
        from_representation = (
            timelength_identify.detect_timelength_representation(timelength)
        )

    # return if already in target type
    if from_representation == to_representation:
        return timelength

    # convert to seconds
    if timelength_identify.is_timelength_seconds(timelength):
        timelength_seconds: spec.TimelengthSecondsRaw = timelength
    elif timelength_identify.is_timelength_seconds_precise(timelength):
        timelength_seconds = timelength
    elif timelength_identify.is_timelength_label(timelength):
        timelength_seconds = timelength_label_to_seconds(timelength)
    elif timelength_identify.is_timelength_clock(timelength):
        timelength_seconds = timelength_clock_to_seconds(timelength)
    elif timelength_identify.is_timelength_phrase(timelength):
        timelength_seconds = timelength_phrase_to_seconds(timelength)
    elif timelength_identify.is_timelength_clock_phrase(timelength):
        timelength_seconds = timelength_clock_phrase_to_seconds(timelength)
    elif timelength_identify.is_timelength_timedelta(timelength):
        timelength_seconds = timelength_timedelta_to_seconds(timelength)
    else:
        raise Exception(
            'unknown timelength_representation: ' + str(from_representation)
        )

    # convert to target type
    if to_representation == 'TimelengthSeconds':
        return int(timelength_seconds)
    elif to_representation == 'TimelengthSecondsPrecise':
        return float(timelength_seconds)
    elif to_representation == 'TimelengthLabel':
        return timelength_seconds_to_label(timelength_seconds)
    elif to_representation == 'TimelengthClock':
        return timelength_seconds_to_clock(timelength_seconds)
    elif to_representation == 'TimelengthPhrase':
        return timelength_seconds_to_phrase(timelength_seconds)
    elif to_representation == 'TimelengthClockPhrase':
        return timelength_seconds_to_clock_phrase(timelength_seconds)
    elif to_representation == 'TimelengthTimedelta':
        return timelength_seconds_to_timedelta(timelength_seconds)
    else:
        raise Exception(
            'unknown timelength_representation: ' + str(to_representation)
        )


#
# # functions with target representation specified
#


def timelength_to_seconds(
    timelength: spec.Timelength,
    from_representation: spec.TimelengthRepresentation = None,
) -> spec.TimelengthSeconds:
    """convert Timelength to TimelengthSeconds

    ## Inputs
    - timelength: Timelength
    - from_representation: str representation name of input timelength

    ## Returns
    - TimelengthSeconds timelength
    """
    return convert_timelength(
        timelength=timelength,
        to_representation='TimelengthSeconds',
        from_representation=from_representation,
    )


def timelength_to_seconds_precise(
    timelength: spec.Timelength,
    from_representation: spec.TimelengthRepresentation = None,
) -> spec.TimelengthSecondsPrecise:
    """convert Timelength to TimelengthSecondsPrecise

    ## Inputs
    - timelength: Timelength
    - from_representation: str representation name of input timelength

    ## Returns
    - TimelengthSecondsPrecise timelength
    """
    return convert_timelength(
        timelength=timelength,
        to_representation='TimelengthSecondsPrecise',
        from_representation=from_representation,
    )


def timelength_to_label(
    timelength: spec.Timelength,
    from_representation: spec.TimelengthRepresentation = None,
) -> spec.TimelengthLabel:
    """convert Timelength to TimelengthLabel

    ## Inputs
    - timelength: Timelength
    - from_representation: str representation name of input timelength

    ## Returns
    - TimelengthLabel timelength
    """
    return convert_timelength(
        timelength=timelength,
        to_representation='TimelengthLabel',
        from_representation=from_representation,
    )


def timelength_to_phrase(
    timelength: spec.Timelength,
    from_representation: spec.TimelengthRepresentation = None,
) -> spec.TimelengthPhrase:
    """convert Timelength to TimelengthPhrase

    ## Inputs
    - timelength: Timelength
    - from_representation: str representation name of input timelength

    ## Returns
    - TimelengthPhrase timelength
    """
    return convert_timelength(
        timelength=timelength,
        to_representation='TimelengthPhrase',
        from_representation=from_representation,
    )


def timelength_to_clock(
    timelength: spec.Timelength,
    from_representation: spec.TimelengthRepresentation = None,
) -> spec.TimelengthClock:
    """convert Timelength to TimelengthClock

    ## Inputs
    - timelength: Timelength
    - from_representation: str representation name of input timelength

    ## Returns
    - TimelengthClock timelength
    """
    return convert_timelength(
        timelength=timelength,
        to_representation='TimelengthClock',
        from_representation=from_representation,
    )


def timelength_to_clock_phrase(
    timelength: spec.Timelength,
    from_representation: spec.TimelengthRepresentation = None,
) -> spec.TimelengthClockPhrase:
    """convert Timelength to TimelengthClockPhrase

    ## Inputs
    - timelength: Timelength
    - from_representation: str representation name of input timelength

    ## Returns
    - TimelengthClockPhrase timelength
    """
    return convert_timelength(
        timelength=timelength,
        to_representation='TimelengthClockPhrase',
        from_representation=from_representation,
    )


def timelength_to_timedelta(
    timelength: spec.Timelength,
    from_representation: spec.TimelengthRepresentation = None,
) -> spec.TimelengthTimedelta:
    """convert Timelength to TimelengthTimedelta

    ## Inputs
    - timelength: Timelength
    - from_representation: str representation name of input timelength

    ## Returns
    - TimelengthTimedelta timelength
    """
    return convert_timelength(
        timelength=timelength,
        to_representation='TimelengthTimedelta',
        from_representation=from_representation,
    )


#
# # specific conversion functions, from seconds
#


def timelength_seconds_to_label(
    timelength_seconds: spec.TimelengthSecondsRaw,
    base_only: bool = False,
    fuzzy_tolerance: typing.SupportsFloat = None,
    base_unit: str = None,
) -> spec.TimelengthLabel:
    """convert seconds to TimelengthLabel

    - matches integer multiples of base units
        - see get_base_units() for base units

    ## Inputs
    - seconds: int or float number of seconds
    - base_only: bool of whether to match only to base units
    - fuzzy_tolerance: float of how close seconds much be to a mathcing label
        - 0.1 -> '1m' would match any seconds in range [54, 66]
        - 0.1 -> '5m' would match any seconds in range [270, 330]
    - base_unit: str of base unit
    """

    seconds = timelength_seconds
    if type(seconds).__name__ in ['float', 'float64', 'float32', 'float16']:
        int_seconds = int(seconds)
        if math.isclose(int_seconds, seconds):
            seconds = int_seconds

        elif int_seconds > 5.0:
            seconds = int_seconds

    # collect possible base units
    base_units = timelength_units.get_base_units()
    if base_unit is not None:
        if base_unit not in base_units:
            raise Exception('invalid base unit: ' + str(base_unit))
        candidates = {base_unit: base_units[base_unit]}
    else:
        candidates = base_units

    # attempt matches to candidate base units in descending order
    descending = sorted(candidates.items(), key=lambda item: -item[-1])
    for base_label, base_seconds in descending:

        # attempt match to base unit
        if base_only:
            if math.isclose(seconds, base_seconds):
                return base_label
            else:
                continue

        # attempt exact match of base unit multiple
        quotient = seconds / base_seconds
        quotient_as_int = round(quotient)
        if math.isclose(quotient, quotient_as_int):
            unit_count = quotient_as_int
            unit_letter = base_label[-1]
            break

        # attempt fuzzy match of base unit multiple
        if fuzzy_tolerance is not None:
            round_quotient = round(quotient)
            factor = round_quotient * base_seconds
            upper_bound = (1 + spec.to_numeric(fuzzy_tolerance)) * factor
            lower_bound = (1 - spec.to_numeric(fuzzy_tolerance)) * factor
            if lower_bound <= seconds and seconds <= upper_bound:
                unit_count = round_quotient
                unit_letter = base_label[-1]
                break
    else:
        raise Exception('could not seconds convert to label')

    # create label
    label = str(unit_count) + unit_letter

    return label


def timelength_seconds_to_clock(
    timelength_seconds: spec.TimelengthSecondsRaw,
) -> spec.TimelengthClock:
    """convert seconds to TimelengthClock"""
    base_units = timelength_units.get_base_units()
    n_days = math.floor(timelength_seconds / base_units['1d'])
    n_seconds_remaining = timelength_seconds % base_units['1d']
    clock = str(datetime.timedelta(seconds=n_seconds_remaining))
    if n_days > 0:
        clock = str(n_days) + ':' + clock
    return clock


def timelength_seconds_to_phrase(
    timelength_seconds: spec.TimelengthSecondsRaw,
) -> spec.TimelengthPhrase:
    """convert seconds to TimelengthPhrase"""

    unit_names = [
        'years',
        'days',
        'hours',
        'minutes',
        'seconds',
    ]

    # compute count for each unit
    remaining = timelength_seconds
    base_units = timelength_units.get_base_units()
    unit_names_to_labels = timelength_units.get_unit_labels()
    unit_counts: list[typing.Union[int, float]] = []
    for unit_name in unit_names:
        unit_seconds = base_units[unit_names_to_labels[unit_name]]
        unit_count: typing.Union[int, float] = math.floor(
            remaining / unit_seconds
        )
        unit_counts.append(unit_count)
        remaining = remaining % unit_seconds
    if not math.isclose(remaining, 0):
        unit_counts[-1] += remaining

    # assemble pieces from unit counts
    pieces: list[str] = []
    for unit_count, unit_name in zip(unit_counts, unit_names):
        if unit_count > 0:
            piece = str(unit_count) + ' ' + unit_name
            pieces.append(piece)

    # assemble pieces into phrase
    if len(pieces) == 0:
        phrase = '0 ' + unit_names[-1]
    else:
        phrase = ', '.join(pieces)

    return phrase


def timelength_seconds_to_clock_phrase(
    timelength_seconds: spec.TimelengthSecondsRaw,
) -> spec.TimelengthClockPhrase:
    """convert seconds to TimelengthClockPhrase"""

    base_units = timelength_units.get_base_units()
    n_years = math.floor(timelength_seconds / base_units['1y'])
    n_years_remainder = timelength_seconds % base_units['1y']
    n_days = math.floor(n_years_remainder / base_units['1d'])
    n_days_remainder = n_years_remainder % base_units['1d']

    phrase_pieces = []
    if n_years > 0:
        phrase_pieces.append(str(n_years) + ' years')
    if n_days > 0:
        phrase_pieces.append(str(n_days) + ' days')
    if n_days_remainder > 0:
        if type(n_days_remainder).__name__ == 'int64':
            n_days_remainder = int(n_days_remainder)
        phrase_pieces.append(str(datetime.timedelta(seconds=n_days_remainder)))

    phrase = ', '.join(phrase_pieces)

    return phrase


def timelength_seconds_to_timedelta(
    timelength_seconds: spec.TimelengthSecondsRaw,
) -> spec.TimelengthTimedelta:
    """convert seconds to TimelengthTimedelta"""
    return datetime.timedelta(seconds=timelength_seconds)


#
# # to seconds
#


def timelength_label_to_seconds(
    timelength_label: spec.TimelengthLabel,
) -> spec.TimelengthSeconds:
    """convert TimelengthLabel to seconds"""
    number = int(timelength_label[:-1])
    letter = timelength_label[-1]
    base_units = timelength_units.get_base_units()
    base_seconds = base_units['1' + letter]
    seconds = number * base_seconds
    return seconds


def timelength_clock_to_seconds(
    timelength_clock: spec.TimelengthClock,
) -> spec.TimelengthSecondsRaw:
    """convert TimelengthClock to seconds"""

    pieces = timelength_clock.split(':')
    piece_numbers = [spec.str_to_numeric(piece) for piece in pieces]
    if len(pieces) == 3:
        days: typing.Union[int, float] = 0
        hours: typing.Union[int, float] = piece_numbers[0]
        minutes: typing.Union[int, float] = piece_numbers[1]
        seconds: typing.Union[int, float] = piece_numbers[2]
    elif len(pieces) == 4:
        days = piece_numbers[0]
        hours = piece_numbers[1]
        minutes = piece_numbers[2]
        seconds = piece_numbers[3]
    else:
        raise Exception('unknown timelength clock format')

    base_units = timelength_units.get_base_units()
    return (
        base_units['1d'] * days
        + base_units['1h'] * hours
        + base_units['1m'] * minutes
        + base_units['1s'] * seconds
    )


def timelength_phrase_to_seconds(
    timelength_phrase: spec.TimelengthPhrase,
) -> spec.TimelengthSecondsRaw:
    """convert TimelengthPhrase to seconds"""

    bases = timelength_units.get_base_units()
    unit_names_to_labels = timelength_units.get_unit_labels()
    phrase_pieces = timelength_phrase.split(', ')

    seconds: typing.Union[int, float] = 0
    for piece in phrase_pieces:
        unit_count, unit_name = piece.split(' ')
        unit_count_numeric = spec.str_to_numeric(unit_count)
        seconds += unit_count_numeric * bases[unit_names_to_labels[unit_name]]

    return seconds


def timelength_clock_phrase_to_seconds(
    timelength_clock_phrase: spec.TimelengthClockPhrase,
) -> spec.TimelengthSecondsRaw:
    """convert TimelengthClockPhrase to seconds"""

    pieces = timelength_clock_phrase.split(', ')
    phrase = ', '.join(pieces[:-1])
    if phrase != '':
        phrase_seconds = timelength_phrase_to_seconds(phrase)
    else:
        phrase_seconds = 0
    clock_seconds = timelength_clock_to_seconds(pieces[-1])
    return phrase_seconds + clock_seconds


def timelength_timedelta_to_seconds(
    timelength_timedelta: spec.TimelengthTimedelta,
) -> spec.TimelengthSecondsRaw:
    """convert TimelengthTimedelta to seconds"""
    return timelength_timedelta.total_seconds()


#
# # special conversions
#


def timelength_to_pandas_timelength(
    timelength: spec.Timelength,
) -> spec.TimelengthPandas:
    timelength_label = timelength_to_label(timelength)
    number = timelength_label[:-1]
    unit_name = timelength_units.unit_letters_to_names()[timelength_label[-1]]
    pandas_unit = timelength_units.get_english_to_pandas_units()[unit_name]
    return number + pandas_unit

