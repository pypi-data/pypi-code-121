from typing import Optional


def recursive_fibonnaci_number(number: int) -> int:
    if number < 0:
        raise ValueError("Fibonacci has to be equal or above zero.")
    elif number <= 1:
        return number
    else:
        return recursive_fibonnaci_number(number - 1) + recursive_fibonnaci_number(number - 2)