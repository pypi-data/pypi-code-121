import typing as t


def get_version_number(version: t.Tuple[int, int, int]) -> str:
    version_number = '.'.join((str(number) for number in version))
    return version_number
