from pricecypher.collections.base_collection import BaseCollection
from pricecypher.models import ScopeValue


class ScopeValueCollection(BaseCollection):
    _type = ScopeValue

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

    def where_in(self, values):
        """
        Filter collection on the given values.

        :param list or float or str values: Value or values to filter the collection on.
        :return: Collection of filtered scope values.
        :rtype: ScopeValueCollection
        """
        # Turn values into a list if it is not a list already.
        if type(values) is not list:
            values = [values]

        # Make sure all values are strings.
        values = list(map(str, values))
        # Filter and create new collection
        scope_values = [sv for sv in self._list if sv.value in values]
        return ScopeValueCollection(scope_values)
