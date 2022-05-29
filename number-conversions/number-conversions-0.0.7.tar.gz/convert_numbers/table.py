"""
    Converts a list of numbers from one base to another
    the numbers are comma separated
    to use a file as input leave the first argument as 0 or anything and use the marker -if=input_file
    to output to a file use -f=output_file or --file=output_file

    File format of the input file is: e.g., numbers.txt
    1,23,45,6,7,87,86,46,35,24,234,53,6,63,3535

    the numbers are comma separated new lines are assumed to also be separators
"""
import argparse

import n_utils
from conversions import convert_number


class ListArgAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ListArgAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        values = [value for value in values.split(',') if value]
        setattr(namespace, self.dest, values)


par = argparse.ArgumentParser()

par.add_argument(
    'numbers',
    type=str,
    action=ListArgAction,
    help='A list of comma separated numbers in the same base. '
         'To use input file leave this as 0 or anything and add -if'
)

par.add_argument(
    'new_base',
    type=int,
    help='The base to convert the numbers to'
)

par.add_argument(
    '--current_base',
    '-cb',
    type=int,
    default=10,
    help='The current base of the numbers in the list'
)

par.add_argument(
    '--file',
    '-f',
    type=str,
    help='File to save the result in'
)

par.add_argument(
    '--in_file',
    '-if',
    type=str,
    help='File with input, ignores numbers, use 0 instead'
)

args = par.parse_args()

if args.in_file:
    with open(args.in_file, 'r', encoding='utf-8') as in_file:
        text = in_file.read()
        text = text.replace('\n', ',')
        numbers = [number.strip() for number in text.split(',') if number.strip()]
else:
    numbers = args.numbers

current_base = args.current_base
new_base = args.new_base
center_len = 4


# the real work begins
if all([n_utils.base_limits(num, current_base) for num in numbers]) and n_utils.ensure_base_is_standard(new_base):
    current_base_name = n_utils.base_find(current_base)
    new_base_name = n_utils.base_find(new_base)
    converted_numbers = [convert_number(num, current_base, new_base) for num in numbers]
    magic_key = key = lambda item: len(item)
    col_1_len = len(max([current_base_name, max(numbers, key=magic_key)], key=magic_key))
    col_2_len = len(max([new_base_name, max(converted_numbers, key=magic_key)], key=magic_key))
    lone_string = '-' * (col_1_len + 1 + col_2_len + (center_len * 2) + 2)

    numbers_string = f'\n'.join([
        f"|{num.center((col_1_len + center_len))}|"
        f"{conv.center((col_2_len + center_len))}|"
        for num, conv in zip(numbers, converted_numbers)
    ])

    result_string = f"|{current_base_name.center(col_1_len + center_len)}|" \
        f"{new_base_name.center(col_2_len + center_len)}|"

    top_s = f'Base {current_base} to base {new_base}'
    f_string = f'{lone_string}\n{result_string}\n{lone_string}\n{numbers_string}\n{lone_string}'
    final_string = f'{top_s}\n{f_string}'

    if args.file:
        with open(args.file, 'w', encoding='utf-8') as f:
            print(final_string, file=f)

        print(f"Results written to '{args.file}'")
    else:
        print(final_string)


else:
    print("Ensure your arguments are correct: "
          "The base should be standard or the numbers to be within the limit of the current base.")
