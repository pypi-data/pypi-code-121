from pricecypher.collections.base_collection import BaseCollection
from pricecypher.models import Scope


class ScopeCollection(BaseCollection):
    _type = Scope

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self._list)

    def __len__(self):
        """List length"""
        return len(self._list)

    def __getitem__(self, ii):
        """Get a list item"""
        return self._list[ii]

    def __str__(self):
        return str(self._list)

    def find_by_id(self, scope_id):
        return next((s for s in self._list if s.id == scope_id), None)

    def find_by_repr(self, representation):
        return next((s for s in self._list if s.representation == representation), None)

    def find_by_name_dataset(self, name_dataset):
        return next((s for s in self._list if s.name_dataset == name_dataset), None)

    def _where(self, prop, value):
        scopes = filter(lambda v: getattr(v, prop) == value, self._list)
        return ScopeCollection(scopes)

    def where_type(self, typ):
        return self._where('type', typ)

    def where_multiply_by_volume_enabled(self, enabled=True):
        return self._where('multiply_by_volume_enabled', enabled)
