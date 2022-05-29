from conversions import convert as __convert

__convert_whole_to_base_10 = __convert.convert_to_base_10
__convert_float_to_base_10 = __convert.convert_float_to_base_10
__float_from_base_10 = __convert.convert_float_from_base_10
__whole_from_base_10 = __convert.convert_from_base_10


def convert_number(number: str, base_from: int, base_to: int) -> str:
    """Convert a number from a base to another"""

    if type(number) != str or type(base_from) != int or type(base_to) != int:
        raise TypeError('Enter the correct type arguments')

    # divide up the number by decimal place/ index 0 is the whole number while index -1 is the floating part
    numbers = number.split('.')
    no_float = False

    if len(numbers) == 1:
        numbers.append('0')
        no_float = True

    # convert every thing to base 10
    if base_from == 10:
        base_10_numbers = [int(numbers[0]), float(f'0.{numbers[-1]}')]

    else:
        base_10_numbers = [
            __convert_whole_to_base_10(numbers[0], base_from),
            __convert_float_to_base_10(f'0.{numbers[-1]}', base_from)
        ]

    # convert to new base
    if base_to == 10:
        new_base_numbers = [str(base_10_numbers[0]), str(base_10_numbers[-1])]

    else:
        new_base_numbers = [
            __whole_from_base_10(base_10_numbers[0], base_to)[0],
            __float_from_base_10(base_10_numbers[-1], base_to)[0]
        ]

    # create the final number
    final_number = new_base_numbers[0]

    if not no_float:
        final_number = f'{final_number}.{new_base_numbers[-1].replace("0.", "")}'

    return final_number
