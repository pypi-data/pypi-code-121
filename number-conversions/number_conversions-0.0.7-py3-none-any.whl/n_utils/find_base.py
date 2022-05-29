from functools import lru_cache
from typing import Union

from prep import number_systems


@lru_cache(1024)
def find(base: int) -> Union[str, None]:
    """Given the numeral of a base, find its name"""
    # uses binary search to find the base name
    systems = number_systems[0]
    start = 0
    end = 81

    while start <= end:
        mid = (start + end) // 2
        temp_base = systems[mid]
        temp_base_number = int(temp_base['base'])

        if temp_base_number == base:
            return temp_base['system_name']

        elif temp_base_number < base:
            start = mid + 1

        else:
            end = mid - 1

    return None
