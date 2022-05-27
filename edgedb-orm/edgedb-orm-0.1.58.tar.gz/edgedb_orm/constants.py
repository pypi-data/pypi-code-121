import typing as T
import random
import string

ALIAS_PATTERN = r">\$(\w+)"


def random_str(n: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def chunk_list(lst: list, chunk_size: int) -> T.List[list]:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(lst: T.List[list]) -> list:
    return [j for sub in lst for j in sub]
