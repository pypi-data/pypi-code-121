from random import choice
from string import ascii_letters, digits


def sequence(count: int | None = None, length: int = 8) -> str | list[str]:
    '''
    Returns a random sequence consisting of ASCII symbols and digits
    or a list of a random sequences

    Args:
        count (int, optional): The number of sequances to be
            generated. Defaults to `None`
        length (int, optional): The length of the sequence.
            Defaults to `8`

    Returns:
        str | list[str]: The sequence if `count` is `None` or
            a list of sequences if `count` is not `None`
    '''
    chars = ascii_letters + digits

    if count:
        sequences = []
        for _ in range(count):
            sequences.append(''.join(choice(chars) for _ in range(length)))
        return sequences
    else:
        return ''.join(choice(chars) for _ in range(length))


def letter(count: int | None = None) -> str | list[str]:
    '''
    Returns a random ASCII letter or a list of them

    Args:
        count (int, optional): The number of letters to be
            generated. Defaults to `None`

    Returns:
        str | list[str]: An ASCII letter if `count` is `None` or
            a list of letters if `count` is not `None`
    '''
    if count:
        letters = []
        for _ in range(count):
            letters.append(choice(ascii_letters))
        return letters
    else:
        return choice(ascii_letters)


def digit(count: int | None = None) -> str | list[str]:
    '''
    Returns a random digit

    Args:
        count (int, optional): The number of digits to be
            generated. Defaults to `None`

    Returns:
        str | list[str]: A single digit if `count` is `None` or
            a list of digits if `count` is not `None`
    '''
    if count:
        digits_lst = []
        for _ in range(count):
            digits_lst.append(choice(digits))
        return digits_lst
    else:
        return choice(digits)


if __name__ == '__main__':
    print(sequence())
    print(letter())
    print(digit())
