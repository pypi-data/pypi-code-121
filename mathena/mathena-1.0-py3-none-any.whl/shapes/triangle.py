import math


def is_valid_angles(angle1: int, angle2: int, angle3: int) -> bool:
    total = angle1 + angle2 + angle3
    if total != 180:
        return False
    else:
        return True
