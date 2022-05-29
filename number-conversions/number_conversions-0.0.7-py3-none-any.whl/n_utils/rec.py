from re import compile as re_compile, findall as re_findall


rec_pattern = re_compile(r'(.+?)\1{2}')


def find_recurring_pattern(r_str: str) -> str:
    """
        finds the recurring pattern in a string.
        The pattern has to repeat more that 3 times
        returns the recurring pattern
    """
    res = ''

    c_str = re_findall(rec_pattern, r_str)

    if len(c_str) > 0:
        res = c_str[-1]

    return res
