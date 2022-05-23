import re

__all__ = ["camelcase"]

non_alpha = re.compile(r"[\W_\/]+([a-z])?")


def camelcase(string: str) -> str:
    return string[0].lower() + non_alpha.sub(
        lambda m: m.group(1).upper() if m.group(1) else "", string[1:]
    )
