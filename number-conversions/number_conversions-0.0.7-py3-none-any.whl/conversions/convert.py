from typing import List
from re import compile as re_compile, search as re_search

from conversions.representations import convert_to_representation, convert_from_representation
from n_utils import find_recurring_pattern


def convert_from_base_10(decimal: int, new_base: int) -> List[str]:
    """
    Takes a decimal and converts it to the the designated number into the new base.
    """
    rems = []
    value = decimal

    while value >= new_base:
        rems.append(value % new_base)
        value //= new_base

    rems.append(value)

    return [convert_to_representation([rem for rem in reversed(rems)]), new_base]


def convert_float_from_base_10(floating_decimal: float, new_base: int) -> List[str]:
    """
    Takes the decimal part and converts it to the new base
    Maximum possible decimal points. However in case of recurring decimal points, the max is 15
    """
    assert 1 > floating_decimal >= 0

    float_match = re_compile(r'\.[0]+$')
    number = floating_decimal
    full_numbers = []

    # multiply until the floating part is zero
    while not re_search(float_match, str(number)):
        number *= new_base
        ex_numbers = str(number).split('.')
        full_numbers.append(ex_numbers[0])
        number = float(f'0.{ex_numbers[-1]}')

        # stop if you find a recurring number no rounding off, just truncate
        if len(full_numbers) > 14 and find_recurring_pattern(''.join(full_numbers)):
            break

    result = convert_to_representation(
        [int(num) for num in full_numbers]
    )

    return [f'0.{result}', new_base]


def convert_to_base_10(number: str, current_base: int) -> int:
    """Takes a number in any base and returns its decimal/base 10 equivalent"""
    numbers = convert_from_representation(number)

    return sum(
        [(current_base**i) * num for i, num in enumerate(reversed(numbers))]
    )


def convert_float_to_base_10(number: str, current_base: int) -> float:
    """Takes a floating number in any base and returns its decimal/base 10 equivalent"""
    assert '.' in number
    number = number.split('.')[-1]
    numbers = convert_from_representation(number)

    return sum(
        [(current_base**-i) * num for i, num in enumerate(numbers, 1)]
    )
