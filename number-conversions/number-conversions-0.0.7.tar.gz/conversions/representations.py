"""
Convert to and from a representation
"""

from typing import List

from prep import number_codes


def convert_to_representation(numbers: List[int]) -> str:
    """Represent the numbers using the format of one character per number"""
    return ''.join([chr(number_codes[num]) for num in numbers])


def convert_from_representation(representation: str) -> List[int]:
    """Get a list of numbers used to make the representation"""
    return [number_codes.index(ord(c)) for c in representation]
