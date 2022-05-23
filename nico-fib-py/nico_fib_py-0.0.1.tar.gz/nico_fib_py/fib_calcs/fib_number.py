from typing import Optional

def recursive_fibonnaci_number(number: int) -> Optional[int]:
    if number < 0:
        return None
    elif number <= 1:
        return number
    else:
        return recursive_fibonnaci_number(number - 1) + recursive_fibonnaci_number(number - 2)