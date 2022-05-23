from typing import List
from .fib_number import recursive_fibonnaci_number


def calculate_numbers(numbers: List[int]) -> List[int]:
    return [recursive_fibonnaci_number(number=i) for i in numbers]