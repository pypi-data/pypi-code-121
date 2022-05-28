"""
An easy, readable interface for checking string arguments as effectively enums

Intended for high-level arguments instead of actual data processing as not as efficient
"""


from typing import List

from stefutil.prettier import logi


__all__ = ['CheckArg', 'ca']


class CheckArg:
    """
    Raise errors when common arguments don't match the expected values
    """

    @staticmethod
    def check_mismatch(display_name: str, val: str, accepted_values: List[str]):
        if val not in accepted_values:
            raise ValueError(f'Unexpected {logi(display_name)}: '
                             f'expect one of {logi(accepted_values)}, got {logi(val)}')

    def __init__(self):
        self.d_name2func = dict()

    def __call__(self, **kwargs):
        for k in kwargs:
            self.d_name2func[k](kwargs[k])

    def cache_mismatch(self, display_name: str, attr_name: str, accepted_values: List[str]):
        self.d_name2func[attr_name] = lambda x: CheckArg.check_mismatch(display_name, x, accepted_values)


ca = CheckArg()
ca.cache_mismatch(  # See `stefutil::plot.py`
    'Bar Plot Orientation', attr_name='bar_orient', accepted_values=['v', 'h', 'vertical', 'horizontal']
)


if __name__ == '__main__':
    ori = 'v'
    ca(bar_orient=ori)
