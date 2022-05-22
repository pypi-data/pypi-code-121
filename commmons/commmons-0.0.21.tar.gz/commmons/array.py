from math import floor

__all__ = [
    "linear_sample"
]


def linear_sample(array: list, n: int) -> list:
    if n >= len(array):
        return array

    if n == 0:
        return list()

    unique_indices = set([floor(x * len(array) / n) for x in range(n)])
    return [array[i] for i in unique_indices]
