"""
Read digits from a file and convert them to expected base
File format is: e.g., numbers.txt
1,23,45,6,7,87,86,46,35,24,234,53,6,63,3535
2
10

first line is the numbers to convert, comma separated
second line is the base to convert to
third line is the current base, if none it's assumed base 10

"""
import argparse
from typing import Union, Tuple

from conversions import convert_number
import n_utils


par = argparse.ArgumentParser()

par.add_argument(
    'input_file',
    type=str,
    help='The path of the file where the numbers are'
)

par.add_argument(
    'output_file',
    type=str,
    help='File to write the results in'
)

args = par.parse_args()


# The real work begins
def extract_details(text: str) -> Union[Tuple, None]:
    split_text = text.split('\n')
    assert len(split_text) in (2, 3)
    detail_numbers = [item.strip() for item in split_text[0].split(',') if item.strip()]

    try:
        detail_new_base = int(split_text[1])

        try:
            detail_current_base = int(split_text[2])
        except IndexError:
            detail_current_base = 10
    except ValueError:
        print("Ensure the bases are integers")
        return

    return detail_numbers, detail_new_base, detail_current_base


with open(args.output_file, 'w', encoding='utf-8') as out_file:
    with open(args.input_file, 'r', encoding='utf-8') as in_file:
        read_text = in_file.read()
        details = extract_details(read_text)

    if type(details) == tuple and len(details) == 3 and all(details):
        numbers = details[0]
        new_base = details[1]
        current_base = details[2]

        if all([n_utils.base_limits(num, current_base) for num in numbers]):
            if n_utils.ensure_base_is_standard(new_base):
                converted_numbers = [convert_number(number, current_base, new_base) for number in numbers]

                print(f'Base {current_base},base {new_base}', file=out_file)
                print(f'{n_utils.base_find(current_base)},{n_utils.base_find(new_base)}', file=out_file)
                print('\n'.join([
                    f'{num},{conv}' for num, conv in zip(numbers, converted_numbers)
                ]), file=out_file)

                print(f"Written to '{args.output_file}'")

            else:
                print(f"Base {new_base} is not standard. Refer to wikipedia")

        else:
            print(f"The numbers are not really base {current_base}")

    else:
        print(f"Format '{args.input_file}' properly")
