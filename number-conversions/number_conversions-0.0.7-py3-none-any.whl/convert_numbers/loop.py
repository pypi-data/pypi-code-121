"""
User types in 3 numbers separated by a space
    number_to_convert base_to_convert_to current_base

if current_base is not provided base 10 is assumed

Runs until user types 'q'
"""
from typing import Tuple, Union

from .__dip import dip_this_func


def extract_numbers(string: str) -> Union[Tuple, None]:
    s_string = string.split(' ')
    number = s_string[0]

    if len(s_string) < 2:
        print(f'Please provide a base to convert {number} to')
        return

    try:

        new_base = int(s_string[1])
        try:
            current_base = int(s_string[2])
        except IndexError:
            current_base = 10

    except ValueError:
        print('Ensure the bases are integers')
        return

    return number, new_base, current_base


if __name__ == '__main__':
    run = True

    while run:
        try:
            user_text = input("Enter 'number new_base current_base': ")

            if user_text == 'q':
                run = False
                continue

            elif user_text == 'h':
                print(__doc__)
                continue

            else:
                numbers = extract_numbers(user_text)

                if type(numbers) == tuple and len(numbers) == 3 and all(numbers):
                    dip_this_func(*numbers)

        except KeyboardInterrupt:
            print("EXITING")
            run = False
