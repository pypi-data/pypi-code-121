"""Assurances for the numbers presented by user"""
from prep import number_systems, number_codes


def ensure_base_is_standard(base: int) -> bool:
    """
        Ensures the base entered is one of the 82 standard bases.
        Described 'prep/systems.csv' or https://en.wikipedia.org/wiki/List_of_numeral_systems
    """
    return base in number_systems[-1]


def ensure_number_representation_is_within_base_limits(number: str, base: int) -> bool:
    """
        Ensure the representations of a number are within the base character representations
        E.g., G4 cannot be base 16 as G is well beyond base 16
    """
    # . is removed since it's not part of the representation
    # uses the number codes up to a certain place to ensure only character usable for that base are checked
    return all([ord(c) in number_codes[:base] for c in number.replace('.', '')])
