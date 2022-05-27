"""
Queries are a little different
Each time you iterate along, you dont add to the graph straight away.
This gives the Query time to modify the meaning of statements:
without waiting,
    ob.runs[1234] would be [traverse(ob), traverse(run), CopyAndFilter(id=1234)]
with waiting,
    ob.runs[1234] would be [traverse(ob), FilteredMatch(run, id=1234, optional=True)]
    much better!
it treats two chained expressions as one action
"""
from typing import List, TYPE_CHECKING, Union, Tuple, Dict, Any

from networkx import NetworkXNoPath

from .base import BaseQuery
from .exceptions import CardinalityError, AttributeNameError, UserError
from .parser import QueryGraph, ParserError
from .utilities import is_regex, dtype_conversion
from ..opr3.hierarchy import Exposure

if TYPE_CHECKING:
    from weaveio.data import Data


class GenericObjectQuery(BaseQuery):
    pass


def process_names(given_names, attrs: List['AttributeQuery']) -> List[str]:
    for i, (given_name, attr) in enumerate(zip(given_names, attrs)):
        if given_name is None:
            given_names[i] = attr._factor_name
    if len(set(given_names)) == len(given_names):
        return given_names
    names = [a._factor_name for a in attrs]
    if len(set(names)) == len(names):
        return names
    for i, n in enumerate(names):
        if names.count(n) > 1:
            j = names[:i].count(n)
            names[i] = f"{n}{j}"
    return [a._factor_name for a in attrs]  # todo: this could be better

class ObjectQuery(GenericObjectQuery):
    def _precompile(self) -> 'TableQuery':
        """
        If the object contains only one factor/product and defines no parents/children, return that
        Otherwise, try to return just the id or error
        """
        Obj = self._data.class_hierarchies[self._obj]
        if Obj.idname is not None:
            attr = Obj.idname
        elif len(Obj.products_and_factors) == 1:
            attr = Obj.products_and_factors[0]  # take the only data in it
        elif 'value' in Obj.products_and_factors:
            attr = 'value'
        else:
            raise SyntaxError(f"{self._obj} cannot be returned/identified since it doesn't define any unique idname. "
                              f"If you want to return all singular data for {self._obj} use ...['*']")
        return self.__getitem__(attr)._precompile()

    def _get_all_factors_table(self):
        """
        For use with ['*']
        """
        single_objs = self._data.all_single_links_to_hierarchy(self._obj)
        factors = {f if o.__name__ == self._obj else f"{o.singular_name}.{f}" for o in single_objs for f in o.products_and_factors}
        try:
            factors.remove('id')
            factors = ['id'] + sorted(factors)
        except KeyError:
            factors = sorted(factors)
        return factors

    def _select_all_attrs(self):
        h = self._data.class_hierarchies[self._data.class_name(self._obj)]
        return self.__getitem__(h.products_and_factors)

    def _traverse_to_generic_object(self):
        """
        obj.generic_obj['specific_type_name']
        filter, shrinks, destructive
        filters based on the type of object to make it more specific
        only shared factors can be accessed
        e.g. `obj.spectra` could be l1singlespectra, l1stackedspectra, l2modelspectra etc
             but `obj.spectra['l1']` ensures that it is only `l1` and only `l1` factors can be accessed
                 `obj.spectra['single']`
        """
        raise NotImplementedError

    def _traverse_to_specific_object(self, obj, want_single):
        """
        obj.obj
        traversal, expands
        e.g. `ob.runs`  reads "for each ob, get its runs"
        """
        plural = self._data.plural_name(obj)
        err_msg = f"There is no singular {obj} relative to {self._obj} try using its plural {plural}"
        try:
            path, single, _ = self._get_path_to_object(obj, want_single)
        except NetworkXNoPath:
            if not want_single:
                err_msg = f"There is no {obj} relative to {self._obj}"
            raise CardinalityError(err_msg)
        if not single and want_single:
            raise CardinalityError(err_msg)
        n = self._G.add_traversal(self._node, path, obj, single)
        return ObjectQuery._spawn(self, n, obj, single=want_single)

    def _traverse_by_object_index(self, obj, index):
        """
        obj['obj_id']
        filter, id, shrinks, destructive
        this is a filter which always returns one object
        if the object with this id is not in the hierarchy, then null is returned
        e.g. `obs[1234]` filters to the single ob with obid=1234
        """
        param = self._G.add_parameter(index)
        path, single, _ = self._get_path_to_object(obj, False)
        travel = self._G.add_traversal(self._node, path, obj, single)
        i = self._G.add_getitem(travel, 'id')
        eq, _ = self._G.add_scalar_operation(i, f'{{0}} = {param}', f'id={index}')
        n = self._G.add_filter(travel, eq, direct=True)
        return ObjectQuery._spawn(self, n, obj, single=True)

    def _traverse_by_object_indexes(self, obj, indexes: List):
        param = self._G.add_parameter(indexes)
        path, single, _ = self._get_path_to_object(obj, False)
        one_id = self._G.add_unwind_parameter(self._node, param)
        travel = self._G.add_traversal(self._node, path, obj, single, one_id)
        i = self._G.add_getitem(travel, 'id')
        eq, _ = self._G.add_combining_operation('{0} = {1}', 'ids', i, one_id)
        n = self._G.add_filter(travel, eq, direct=True)
        return ObjectQuery._spawn(self, n, obj, single=True)

    def _select_product(self, attr, want_single):
        attr = self._data.singular_name(attr)
        n = self._G.add_getproduct(self._node, attr)
        return ProductAttributeQuery._spawn(self, n, single=want_single, factor_name=attr, is_products=[True])

    def _select_attribute(self, attr, want_single):
        """
        # obj['factor'], obj.factor
        fetches an attribute from the object and cuts off any other functions after that
        if the factor is not found in the object then the nearest corresponding object is used.
        e.g. `exposure.mjd` returns the mjd held by exposure
             `run.mjd` returns the mjd by a run's exposure (still only one mjd per run though)
             `run.cnames` returns the cname of each target in a run (this is a list per run)
        """
        if self._data.is_product(attr, self._obj):
            return self._select_product(attr, want_single)
        attr = self._data.singular_name(attr)
        n = self._G.add_getitem(self._node, attr)
        return AttributeQuery._spawn(self, n, single=want_single, factor_name=attr)

    def _select_or_traverse_to_attribute(self, attr):
        obj, obj_is_single, attr_is_single = self._get_object_of(attr)  # if factor
        if obj == self._obj:
            return self._select_attribute(attr, attr_is_single)
        r = self._traverse_to_specific_object(obj, obj_is_single)._select_attribute(attr, attr_is_single)
        r._index_node = self._node
        return r

    def _make_table(self, *items):
        """
        obj['factor_string', AttributeQuery]
        obj['factora', 'factorb']
        obj['factora', obj.obj.factorb]
        obj['factora', 'obj.factorb']
        """
        attrs = []
        for item in items:
            if isinstance(item, ObjectQuery):
                item = item._precompile()
            if isinstance(item, AttributeQuery):
                attrs.append(item)
            else:
                new = self.__getitem__(item)
                if isinstance(new, ObjectQuery):
                    new = new._precompile()
                if isinstance(new, list):
                    for a in new:
                        attrs.append(a)
                attrs.append(new)
        force_plurals = [not a._single for a in attrs]
        is_products = [a._is_products[0] for a in attrs]
        n = self._G.add_results_table(self._node, [a._node for a in attrs], force_plurals, dropna=[self._node])
        names = process_names([i if isinstance(i, str) else None for i in items], attrs)
        return TableQuery._spawn(self, n, names=names, is_products=is_products, attrs=attrs)

    def _traverse_to_relative_object(self, obj, index):
        """
        obj.relative_path
        traversal, expands
        traverses by a specifically labelled relation instead of a name of an object
        e.g. l1stackedspectra.adjunct_spectrum will get the spectrum in the other arm
        CYPHER: (from:From)-[r]->(to:To) WHERE r.id = ...
        the last relationship will have a variable name:
            (Exposure)-->()-[r]->(Run)
            (Run)<-[r]-()<--(Exposure)
        """
        obj, obj_singular = self._normalise_object(obj)
        singular_name = self._data.singular_name(index)
        path, single, _ = self._get_path_to_object(obj, False)
        if not single and singular_name == index:
            raise SyntaxError(f"Relative index `{index}` is plural relative to `{self._obj}`.")
        n = self._G.add_traversal(self._node, path, obj, False)
        relation_id = self._G.add_getitem(n, 'relation_id', 1)
        name = self._G.add_parameter(singular_name)
        eq, _ = self._G.add_scalar_operation(relation_id, f'{{0}} = {name}', 'rel_id')
        f = self._G.add_filter(n, eq, direct=True)
        return ObjectQuery._spawn(self, f, obj, single=single)

    def _filter_by_relative_index(self):
        """
        obj1.obj2s['relative_id']
        filter, relative id, shrinks, destructive
        filters based on the relations between many `obj2`s and the `obj1`
        e.g. `ob.plate_exposures.fibre_exposures.single_spectra['red']` returns the red spectra
        the relative_id are explicitly stated in the database structure
        """
        raise NotImplementedError

    def _getitems(self, items, by_getitem):
        if not all(isinstance(i, (str, float, int, AttributeQuery)) for i in items):
            raise TypeError(f"Cannot index by non str/float/int/AttributeQuery values")
        if all(self._data.is_valid_name(i) or isinstance(i, AttributeQuery) for i in items):
            return self._make_table(*items)
        if any(self._data.is_valid_name(i) for i in items):
            raise SyntaxError(f"You may not mix filtering by id and building a table with attributes")
        # go back and be better
        return self._previous._traverse_by_object_indexes(self._obj, items)

    def _getitem(self, item, by_getitem):
        """
        item can be an id, a factor name, a list of those, a slice, or a boolean_mask
        """
        if isinstance(item, (tuple, list)):
            return self._getitems(item, by_getitem)
        elif isinstance(item, slice):
            return self._slice(item)
        elif isinstance(item, AttributeQuery):
            return self._filter_by_mask(item)  # a boolean_mask
        elif not isinstance(item, str):
            return self._previous._traverse_by_object_index(self._obj, item)
        elif item == '*':
            all_factors = self._get_all_factors_table()
            return self._getitems(all_factors, by_getitem)
        elif item == '**':
            all_factors = self._data.class_hierarchies[self._obj].products_and_factors
            return self._getitems(all_factors, by_getitem)
        else:
            try:
                return self._select_or_traverse_to_attribute(item)
            except (KeyError, ValueError):
                if '.' in item:  # split the parts and parse
                    try:
                        obj, attr = item.split('.')
                        return self.__getitem__(obj).__getitem__(attr)
                    except ValueError:
                        raise AttributeNameError(f"{item} cannot be parsed as an `obj.attribute`.")
                try: # try assuming its an object
                    obj, single = self._normalise_object(item)
                    if obj == self._obj:
                        return self
                    return self._traverse_to_specific_object(obj, single)
                except (KeyError, ValueError):  # assume its an index of some kind
                    singular = self._data.singular_name(item)
                    if singular in self._data.relative_names:  # if it's a relative id
                        # l1singlespectrum.adjunct gets the adjunct spectrum of a spectrum
                        try:
                            relation = self._data.relative_names[singular][self._obj]
                        except KeyError:
                            raise AttributeNameError(f"`{self._obj}` has no relative relation called `{singular}`")
                        return self._traverse_to_relative_object(relation.node.__name__, item)
                    elif by_getitem:  # otherwise treat as an index
                        return self._previous._traverse_by_object_index(self._obj, item)
                    else:
                        raise AttributeNameError(f"Unknown attribute `{item}`")

    def _getitem_handled(self, item, by_getitem):
        try:
            return self._getitem(item, by_getitem)
        except UserError as e:
            if isinstance(item, AttributeQuery):
                raise e
            self._data.autosuggest(item, self._obj, e)

    def __getattr__(self, item):
        return self._getitem_handled(item, False)

    def __getitem__(self, item):
        return self._getitem_handled(item, True)

    def __eq__(self, other):
        obj = self._data.class_hierarchies[self._obj]
        potential_id = obj.products_and_factors
        if 'id' in potential_id:
            i = 'id'
        elif 'name' in potential_id:
            i = 'name'
        elif 'value' in potential_id:
            i = 'value'
        else:
            raise AttributeNameError(f"`A {self._obj}` has no attribute `id`, `name`, or `value` to compare with. Choose a specific attribute like `{obj.singular_name}.id`.")
        return self._select_attribute(i, True).__eq__(other)


class Query(GenericObjectQuery):
    def __init__(self, data: 'Data', G: QueryGraph = None, node=None, previous: 'BaseQuery' = None, obj: str = None, start=None) -> None:
        super().__init__(data, G, node, previous, obj, start, 'start')

    def _compile(self):
        raise NotImplementedError(f"{self.__class__} is not compilable")

    def _traverse_to_specific_object(self, obj):
        obj, single = self._normalise_object(obj)
        if single:
            raise CardinalityError(f"Cannot start query with a single object `{obj}`")
        n = self._G.add_start_node(obj)
        return ObjectQuery._spawn(self, n, obj, single=False)

    def _traverse_by_object_index(self, obj, index):
        obj, single = self._normalise_object(obj)
        name = self._G.add_parameter(index)
        travel = self._G.add_start_node(obj)
        i = self._G.add_getitem(travel, 'id')
        eq, _ = self._G.add_scalar_operation(i, f'{{0}} = {name}', f'id={index}')
        n = self._G.add_filter(travel, eq, direct=True)
        return ObjectQuery._spawn(self, n, obj, single=True)

    def _traverse_by_object_indexes(self, obj, indexes: List):
        param = self._G.add_parameter(indexes)
        one_id = self._G.add_unwind_parameter(self._node, param)
        travel = self._G.add_start_node(obj, one_id)
        i = self._G.add_getitem(travel, 'id')
        eq, _ = self._G.add_combining_operation('{0} = {1}', 'ids', i, one_id)
        n = self._G.add_filter(travel, eq, direct=True)
        return ObjectQuery._spawn(self, n, obj, single=True)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __getattr__(self, item):
        try:
            if self._data.is_singular_name(item):
                raise CardinalityError(f"Cannot start a query with a single object `{item}`")
            obj = self._get_object_of(item)[0]
            obj = self._data.plural_name(obj)
            return self._traverse_to_specific_object(obj)._select_attribute(item, True)
        except (KeyError, ValueError):
            return self._traverse_to_specific_object(item)


class AttributeQuery(BaseQuery):
    one_column = True

    def __repr__(self):
        return f'<{self.__class__.__name__}({self._obj}.{self._factor_name})>'

    def __init__(self, data: 'Data', G: QueryGraph = None, node=None, previous: Union['Query', 'AttributeQuery', 'ObjectQuery'] = None,
                 obj: str = None, start: Query = None, index_node=None,
                 single=False, factor_name: str = None, dtype: str =None, *args, **kwargs) -> None:
        super().__init__(data, G, node, previous, obj, start, index_node, single, [factor_name], *args, **kwargs)
        self._factor_name = factor_name
        self.dtype = dtype

    def __getitem__(self, item):
        if not isinstance(item, AttributeQuery):
            raise TypeError(f"You can only filter an attribute by another attribute i.e. `lines[lines > 0]` not `lines[0]`")
        op_string = 'CASE WHEN toBoolean(toInteger({1})) THEN {0} ELSE null END'
        try:
            n, wrt = self._G.add_combining_operation(op_string, 'op-filter', self._node, item._node)
        except ParserError:
            raise SyntaxError(f"You may not perform an operation on {self} and {item} since one is not an ancestor of the other")
        return AttributeQuery._spawn(self, n, index_node=wrt, single=True, dtype=self.dtype)

    def _perform_arithmetic(self, op_string, op_name, other=None, expected_dtype=None, returns_dtype=None):
        """
        arithmetics
        [+, -, /, *, >, <, ==, !=, <=, >=]
        performs some maths on factors that have a shared parentage
        e.g. ob1.runs.snrs + ob2.runs.snrs` is not allowed, even if the number of runs/spectra is the same
        e.g. ob.l1stackedspectra[ob.l1stackedspectra.camera == 'red'].snr + ob.l1stackedspectra[ob.l1stackedspectra.camera == 'blue'].snr is not allowed
        e.g. ob.l1stackedspectra[ob.l1stackedspectra.camera == 'red'].snr + ob.l1stackedspectra[ob.l1stackedspectra.camera == 'red'].adjunct.snr is not allowed
        e.g. sum(ob.l1stackedspectra[ob.l1stackedspectra.camera == 'red'].snr, wrt=None) > ob.l1stackedspectra.snr is allowed since one is scalar,
             we take ob.l1stackedspectra as the hierarchy level in order to continue
        e.g. sum(ob.l1stackedspectra[ob.l1stackedspectra.camera == 'red'].snr, wrt=ob) > ob.l1stackedspectra.snr is allowed since there is a shared parent,
             we take ob.l1stackedspectra as the hierarchy level in order to continue
        """
        if isinstance(other, ObjectQuery):
            raise TypeError(f"Cannot do arithmetic directly on objects")
        if expected_dtype is not None:
            op_string = dtype_conversion(self.dtype, expected_dtype, op_string, '{0}', '{1}')
            # op_string = op_string.replace('{0}', f'to{expected_dtype}({{0}})')
            # op_string = op_string.replace('{1}', f'to{expected_dtype}({{1}})')  # both arguments
        if isinstance(other, BaseQuery):
            try:
                n, wrt = self._G.add_combining_operation(op_string, op_name, self._node, other._node)
            except ParserError:
                raise SyntaxError(f"You may not perform an operation on {self} and {other} since one is not an ancestor of the other")
        else:
            n, wrt = self._G.add_scalar_operation(self._node, op_string, op_name)
        return AttributeQuery._spawn(self, n, index_node=wrt, single=True, dtype=returns_dtype)

    def _basic_scalar_function(self, name):
        return self._perform_arithmetic(f'{name}({{0}})', name)

    def _basic_math_operator(self, operator, other, switch=False, out_dtype='number'):
        if not isinstance(other, AttributeQuery):
            other = self._G.add_parameter(other, 'add')
            string_op = f'{other} {operator} {{0}}' if switch else f'{{0}} {operator} {other}'
        else:
            string_op = f'{{1}} {operator} {{0}}' if switch else f'{{0}} {operator} {{1}}'
        return self._perform_arithmetic(string_op, operator, other, returns_dtype=out_dtype)

    def __and__(self, other):
        return self._basic_math_operator('and', other, out_dtype='boolean')

    def __rand__(self, other):
        return self._basic_math_operator('and', other, switch=True, out_dtype='boolean')

    def __or__(self, other):
        return self._basic_math_operator('or', other, out_dtype='boolean')

    def __ror__(self, other):
        return self._basic_math_operator('or', other, switch=True, out_dtype='boolean')

    def __xor__(self, other):
        return self._basic_math_operator('xor', other, out_dtype='boolean')

    def __rxor__(self, other):
        return self._basic_math_operator('xor', other, switch=True, out_dtype='boolean')

    def __invert__(self):
        return self._basic_scalar_function('not')

    def __add__(self, other):
        return self._basic_math_operator('+', other)

    def __radd__(self, other):
        return self._basic_math_operator('+', other, switch=True)

    def __mul__(self, other):
        return self._basic_math_operator('*', other)

    def __rmul__(self, other):
        return self._basic_math_operator('*', other, switch=True)

    def __sub__(self, other):
        return self._basic_math_operator('-', other)

    def __rsub__(self, other):
        return self._basic_math_operator('-', other, switch=True)

    def __truediv__(self, other):
        return self._basic_math_operator('/', other)

    def __rtruediv__(self, other):
        return self._basic_math_operator('/', other, switch=True)

    def __eq__(self, other):
        op = '='
        if isinstance(other, str):
            if is_regex(other):
                op = '=~'
                other = other.strip('/')
        return self._basic_math_operator(op, other, out_dtype='boolean')

    def __ne__(self, other):
        return self._basic_math_operator('<>', other, out_dtype='boolean')

    def __lt__(self, other):
        return self._basic_math_operator('<', other, out_dtype='boolean')

    def __le__(self, other):
        return self._basic_math_operator('<=', other, out_dtype='boolean')

    def __gt__(self, other):
        return self._basic_math_operator('>', other, out_dtype='boolean')

    def __ge__(self, other):
        return self._basic_math_operator('>=', other, out_dtype='boolean')

    def __ceil__(self):
        return self._basic_scalar_function('ceil')

    def __floor__(self):
        return self._basic_scalar_function('floor')

    def __round__(self, ndigits: int):
        raise self._perform_arithmetic(f'round({{0}}, {ndigits}', f'round{ndigits}')

    def __neg__(self):
        return self._perform_arithmetic('-{{0}}', 'neg')

    def __abs__(self):
        return self._basic_scalar_function('abs')

    def __iadd__(self, other):
        raise TypeError

    def _precompile(self) -> 'TableQuery':
        if self._index_node == 'start':
            index = self._G.start
        else:
            index = self._index_node
        r = self._G.add_results_table(index, [self._node], [not self._single], dropna=[self._node])
        a = AttributeQuery._spawn(self, r, self._obj, index, self._single, is_products=self._is_products,
                                  factor_name=self._factor_name)
        if index == 0:
            a.one_row = True
        return a


class ProductAttributeQuery(AttributeQuery):

    def __init__(self, data: 'Data', G: QueryGraph = None, node=None, previous: Union['Query', 'AttributeQuery', 'ObjectQuery'] = None,
                 obj: str = None, start: Query = None, index_node=None, single=False, factor_name: str = None, *args, **kwargs) -> None:
        super().__init__(data, G, node, previous, obj, start, index_node, single, factor_name, is_product=[True], *args, **kwargs)

    def _perform_arithmetic(self, op_string, op_name, other=None, expected_dtype=None):
        raise TypeError(f"Binary data products cannot be operated upon. "
                        f"This is because they are not stored in the database")


class TableQuery(BaseQuery):
    def __init__(self, data: 'Data', G: QueryGraph = None, node=None,
                 previous: Union['Query', 'AttributeQuery', 'ObjectQuery'] = None, obj: str = None,
                 start: Query = None, index_node=None,
                 single=False, attr_queries=None, names=None, *args, **kwargs) -> None:
        super().__init__(data, G, node, previous, obj, start, index_node, single, names, *args, **kwargs)
        self._attr_queries = attr_queries

    def _aggregate(self, wrt, string_op, predicate=False, expected_dtype=None, returns_dtype=None, remove_infs=None):
        return self._previous._aggregate(wrt, string_op, predicate, expected_dtype, returns_dtype, remove_infs)


class ListAttributeQuery(AttributeQuery):
    pass
