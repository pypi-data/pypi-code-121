__all__ = ('FilterMixin',)

from typing import OrderedDict


class FilterError(Exception):
    pass


class FilterAttrNotSet(FilterError):
    pass


class FilterMixin:

    def filter(self, **kwargs) -> tuple:
        if not kwargs:
            raise FilterAttrNotSet('Set filter attr. Example: status="NEW"')
        result = self.list()
        for key, find_value in kwargs.items():
            result = self._find_objects(result, key, find_value)
        return tuple(result)

    def first(self) -> OrderedDict:
        result = self.list()
        return result[0] if len(result) > 0 else None

    def last(self) -> OrderedDict:
        result = self.list()
        return result[-1] if len(result) > 0 else None

    def filter_first(self, **kwargs) -> OrderedDict:
        result = self.filter(**kwargs)
        return result[0] if len(result) > 0 else None

    def filter_last(self, **kwargs) -> OrderedDict:
        result = self.filter(**kwargs)
        return result[-1] if len(result) > 0 else None

    @staticmethod
    def _find_objects(all_values, key, find_value):
        find_value = find_value if isinstance(find_value, (list, tuple)) else (find_value,)
        found_values = [item for item in all_values if item.get(key) in find_value]
        return found_values
