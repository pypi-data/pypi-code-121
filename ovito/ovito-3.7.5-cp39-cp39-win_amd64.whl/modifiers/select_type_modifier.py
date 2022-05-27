import collections.abc as collections
import itertools
from . import SelectTypeModifier

# Implementation of the SelectTypeModifier.types collection:
def _get_SelectTypeModifier_types(self):
    """ 
        The ``set`` of types to select. You can add numeric type *IDs* or type *names* to this set. 
        Type names will automatically be translated into corresponding numeric type IDs by the modifier.
        Thus, it is not necessary for you to look up the numeric ID for a type name using :py:meth:`Property.type_by_name() <ovito.data.Property.type_by_name>`.
        For example, to select all atoms belonging to the type named 'Cu':

        .. literalinclude:: ../example_snippets/select_type_example1.py
           :lines: 7-7
        
        When using the :py:class:`!SelectTypeModifier` to select *structural* types, you can directly use the predefined numeric constants for the structures, e.g.:

        .. literalinclude:: ../example_snippets/select_type_example2.py
           :lines: 7-13

        :Default: ``set([])``
    """

    class TypeSelectionSet(collections.MutableSet):
        """ Helper class that emulates a Python set. It is sourced by two native sets, one containing the numeric 
            type IDS to select and one containing the string type names to select. """

        def __init__(self, modifier): 
            """ The constructor stores away a back-pointer to the owning SelectTypeModifier. """
            self.modifier = modifier

        def __len__(self):
            return len(self.modifier._selected_type_ids) + len(self.modifier._selected_type_names)

        def __iter__(self):
            return itertools.chain(self.modifier._selected_type_ids, self.modifier._selected_type_names)

        def __contains__(self, id):
            return (id in self.modifier._selected_type_ids) or (id in self.modifier._selected_type_names)

        def discard(self, id):
            if isinstance(id, str): 
                name_set = self.modifier._selected_type_names
                name_set.discard(id)
                self.modifier._selected_type_names = name_set
            else:
                numeric_set = self.modifier._selected_type_ids
                numeric_set.discard(id)
                self.modifier._selected_type_ids = numeric_set

        def add(self, id):
            if isinstance(id, str): 
                name_set = self.modifier._selected_type_names
                name_set.add(id)
                self.modifier._selected_type_names = name_set
            else:
                numeric_set = self.modifier._selected_type_ids
                numeric_set.add(id)
                self.modifier._selected_type_ids = numeric_set

        def __repr__(self):
            return repr(self.modifier._selected_type_ids.union(self.modifier._selected_type_names))

        def __str__(self):
            return str(self.modifier._selected_type_ids.union(self.modifier._selected_type_names))

    return TypeSelectionSet(self)

def _set_SelectTypeModifier_types(self, id_set):
    # Decompose the mixed set into two separate sets: one for ints and one for strings:
    name_set = set()
    numeric_set = set()
    for id in id_set:
        if isinstance(id, str): name_set.add(id)
        else: numeric_set.add(int(id))
    # Now pass the two sets to the modifier:
    self._selected_type_names = name_set
    self._selected_type_ids = numeric_set

SelectTypeModifier.types = property(_get_SelectTypeModifier_types, _set_SelectTypeModifier_types)
