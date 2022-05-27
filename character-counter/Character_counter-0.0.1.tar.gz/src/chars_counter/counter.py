import collections
from functools import lru_cache
import argparse


INPUT = ''


def read_file(file):
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                line = f.readline().strip()
        except FileNotFoundError:
            print('\nFile not found! Please input correct path.\n')
            quit()

        if line == '':
            print('\nFile is empty!\n')
            quit()

        return line


def count_chars(string):
    chars_dict = collections.Counter(string)
    chars = [key for key, value in chars_dict.items() if value == 1]
    chars_str = ', '.join(map(str, chars))
    count = len(chars)

    return chars_str, count


@lru_cache(maxsize=128)
def output_counted_chars(string):
    return(
        f'"{string}" => {count_chars(string)[1]}\n'
        f'{count_chars(string)[0]} are present once')


def counter(INPUT):
    try:
        temp = INPUT.split()
        if temp[0] != '--string' and temp[0] != '--file':
            print('\nPlease enter valid key: --string or --file!\n')
            quit()
        else:
            if temp[0] == '--string':
                return(f"\n{output_counted_chars(str(temp[1]))}\n")
            elif temp[0] == '--file':
                return(f"\n{output_counted_chars(read_file(temp[1]))}\n")
    except IndexError:
        print(
            '\nPlease enter valid key and string or file path after key!\n'
            '\nExample:\n--string your_string\nor\n--file ypur_file_path\n')
        quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--string', type=str, default=False)
    parser.add_argument('--file', type=str, default=False)
    args = parser.parse_args()

    if args.string == False and args.file == False:
        print('\nPlease input --string or --file\n')
        quit()

    if args.file:
        return_data = output_counted_chars(read_file(args.file))
    elif args.string:
        return_data = output_counted_chars(str(args.string))

    print(f"\n{return_data}\n")
