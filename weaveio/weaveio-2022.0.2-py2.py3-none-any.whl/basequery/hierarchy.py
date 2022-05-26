from _warnings import warn
from collections import defaultdict
from typing import List, Union, Type, Tuple
from warnings import warn

import networkx as nx
import py2neo
import numpy as np

from .common import FrozenQuery, AmbiguousPathError, is_regex
from .dissociated import Dissociated
from .factor import SingleFactorFrozenQuery, TableFactorFrozenQuery, FactorFrozenQuery
from .tree import Branch
from ..helper import _convert_obj
from ..hierarchy import Hierarchy, Multiple, One2One
from ..writequery import CypherVariable


GET_PRODUCT = "[({{h}})<-[p:product {{{{name: '{name}'}}}}]-(hdu: HDU) | [hdu.sourcefile, hdu.extn, p.index, p.column_name]]"
GET_FACTOR = "{{h}}.{name}"
GET_FACTOR_FORCE_PLURAL = f"[{GET_FACTOR}]"


class HierarchyFrozenQuery(FrozenQuery):
    def __getitem__(self, item):
        raise NotImplementedError

    def __getattr__(self, item):
        raise NotImplementedError

    def _get_factor(self, item, plural):
        raise NotImplementedError(f"Getting singular factors is not supported for {self.__class__.__name__}")

    def _get_hierarchy(self, item, plural):
        raise NotImplementedError(f"Getting singular hierarchies is not supported for {self.__class__.__name__}")

    def _get_table_factor(self, item):
        raise NotImplementedError(f"Getting table factors is not supported for {self.__class__.__name__}")

    def _filter_by_identifiers(self, items):
        raise NotImplementedError(f"Filtering by multiple identifiers is not supported for {self.__class__.__name__}")

    def _filter_by_identifier(self, item):
        raise NotImplementedError(f"Filtering by an identifier is not supported for {self.__class__.__name__}")

    def _filter_by_boolean(self, condition):
        raise NotImplementedError(f"Filtering by a boolean condition is not supported for {self.__class__.__name__}")

    def _apply_aligning_func(self, string, other: 'HierarchyFrozenQuery'):
        if isinstance(other, HierarchyFrozenQuery):
            aligned = self.branch.align(other.branch)
            parent = self
            inputs = {
                'x': aligned.action.transformed_variables.get(parent.branch.current_hierarchy, parent.branch.current_hierarchy),
                'y': aligned.action.transformed_variables.get(other.branch.current_hierarchy, other.branch.current_hierarchy)
            }
        elif isinstance(other, Hierarchy):
            if other.identifier is None:
                raise ValueError(f"Cannot compare with an out-of-db object if it has no identifier")
            parent = getattr(self, self.hierarchy_type.idname)
            data = parent.branch.add_data(other.identifier)
            inputs = {
                'x': parent.branch.current_variables[0],
                'y': data.current_variables[0]
            }
            aligned = data
        elif isinstance(other, FrozenQuery):
            raise TypeError(f"Can only compare an object with another object not with {type(other)}")
        else:
            parent = getattr(self, self.hierarchy_type.idname)
            data = parent.branch.add_data(other)
            inputs = {
                'x': parent.branch.current_variables[0],
                'y': data.current_variables[0]
            }
            aligned = data
        newbranch = aligned.operate(string, **inputs)
        return Dissociated(self.handler, newbranch, newbranch.current_variables[-1], self)

    def __eq__(self, other: Union[Hierarchy, 'HierarchyFrozenQuery', int, float, str]) -> 'Dissociated':
        string = '{x} = {y}'
        if isinstance(other, str):
            if is_regex(other):
                string = '{x} =~ {y}'
                other = other.strip('/')
        return self._apply_aligning_func(string, other)

    def __ne__(self, other: Union[Hierarchy, 'HierarchyFrozenQuery', int, float, str]) -> 'Dissociated':
        string = '{x} <> {y}'
        if isinstance(other, str):
            if is_regex(other):
                string = 'NOT ({x} =~ {y})'
                other = other.strip('/')
        return self._apply_aligning_func(string, other)


class HeterogeneousHierarchyFrozenQuery(HierarchyFrozenQuery):
    """
    The start point for building queries. e.g. `data`
    Available data calls:
        single factor `data.runids` (but always plural)
        single hierarchy `data.runs` (but always plural)
    """
    executable = False

    def __repr__(self):
        return f'query("{self.data.rootdir}/")'

    def _get_hierarchy(self, hierarchy_name, plural) -> 'DefiniteHierarchyFrozenQuery':
        paths, hiers, startbase, endbase = self.handler.paths2hierarchy(hierarchy_name, plural=plural)
        new = self.branch.handler.begin(endbase.__name__)
        return DefiniteHierarchyFrozenQuery(self.handler, new, endbase, new.current_hierarchy, [], self)

    def _get_factor(self, factor_name, plural):
        factor_name = self.data.singular_name(factor_name)
        pathdict, base, is_product, factor_name = self.handler.paths2factor(factor_name, plural=plural)
        begin = self.branch.handler.begin(base.__name__)
        if is_product:
            func = GET_PRODUCT.format(name=factor_name)
        else:
            func = GET_FACTOR.format(name=factor_name)
        new = begin.operate(func, h=begin.current_hierarchy)
        return SingleFactorFrozenQuery(self.handler, new, factor_name, new.current_variables[0], is_product, self)

    def __getattr__(self, item):
        if item in self.data.plural_factors:
            return self._get_factor(item, plural=True)
        elif self.data.is_singular_name(item):
            raise AmbiguousPathError(f"Cannot return only one {item} since the DB contains more than one. Either filter your query first or try {self.data.plural_name(item)}")
        elif item in self.data.plural_hierarchies:
            name = self.data.singular_name(item)
            return self._get_hierarchy(name, plural=True)
        else:
            autosuggest(item, self.handler.data)


class DefiniteHierarchyFrozenQuery(HierarchyFrozenQuery):
    """
    The template class for hierarchy classes that are not heterogeneous i.e. they have a defined hierarchy type
    The start point for building queries. E.g. `data.obs, data.runs.exposure`
    It can have ids or not.
    Available data calls:
        single factor `data.exposures.runids`
        single hierarchy `data.runs.exposure`
        table of factors `data.runs[['runid', 'expmjd']]`
        filter by id `data.runs[11234]`
        filter by condition `data.runs[data.runs.runid > 0]`
    """
    def __init__(self, handler, branch: Branch, hierarchy_type: Type[Hierarchy], hierarchy_variable: CypherVariable,
                 identifiers: List, parent: 'FrozenQuery'):
        super().__init__(handler, branch, parent)
        self.hierarchy_type = hierarchy_type
        self.hierarchy_variable = hierarchy_variable
        self.identifiers = identifiers
        self.string = f"{self.hierarchy_type.singular_name}"

    def _filter_by_boolean(self, boolean_filter: 'FrozenQuery'):
        new = self._make_filtered_branch(boolean_filter)
        return self.__class__(self.handler, new, self.hierarchy_type, self.hierarchy_variable, self.identifiers, self)

    def _prepare_query(self):
        """Add a hierarchy node return statement"""
        query = super(DefiniteHierarchyFrozenQuery, self)._prepare_query()
        with query:
            query.returns(self.branch.find_hierarchies()[-1])
        return query

    def _process_result_row(self, row, nodetype):
        node = row[0]
        if node is None:
            return None
        inputs = {}
        for f in nodetype.factors:
            inputs[f] = node[f]
        if nodetype.idname is not None:
            inputs[nodetype.idname] = node[nodetype.idname]
        base_query = self.handler.hierarchy_from_neo4j_identity(nodetype, node.identity)
        for p in nodetype.parents:
            if isinstance(p, One2One):
                inputs[p.singular_name] = getattr(base_query, p.plural_name)
            elif isinstance(p, Multiple):
                inputs[p.plural_name] = getattr(base_query, p.plural_name)
            else:
                try:
                    inputs[p.singular_name] = getattr(base_query, p.singular_name)
                except AmbiguousPathError:
                    inputs[p.singular_name] = getattr(base_query, p.plural_name)  # this should not have to be done
        h = nodetype(**inputs, do_not_create=True)
        h.add_parent_query(base_query)
        h.add_parent_data(self.handler.data)
        return h

    def _post_process(self, result: py2neo.database.Cursor, squeeze: bool = True):
        result = result.to_table()
        if len(result) == 1 and result[0] is None:
            return []
        results = []
        for row in result:
            h = self._process_result_row(row, self.hierarchy_type)
            results.append(h)
        if len(results) == 1 and squeeze:
            return results[0]
        return results

    def _get_hierarchy(self, name, plural):
        pathlist, endlist, starthier, endhier = self.handler.paths2hierarchy(name, plural=plural, start=self.hierarchy_type)
        new = self.branch.traverse(*pathlist)
        return DefiniteHierarchyFrozenQuery(self.handler, new, endhier, new.current_hierarchy, [], self)

    def _get_factor_query_paths(self, names, plurals):
        if not isinstance(names, (list, tuple)):
            names = [names]
        if not isinstance(plurals, (list, tuple)):
            plurals = [plurals]
        names = [self.data.singular_name(name) for name in names]
        local = []
        remote = defaultdict(list)
        remote_paths = {}
        for i, (name, plural) in enumerate(zip(names, plurals)):
            pathsdict, basehier, is_product, name = self.handler.paths2factor(name, plural, self.hierarchy_type)
            names[i] = name
            if basehier == self.hierarchy_type:
                local.append((name, plural, is_product))
            else:
                remote[(basehier, plural)].append((name, is_product))
                remote_paths[(basehier, plural)] = {path for pathset in pathsdict.values() for path in pathset}
        return names, plurals, local, remote, remote_paths

    def _get_multifactor_query(self, names: Union[List[str], str], plurals: Union[List[bool], bool],
                               collect_plurals: bool = True) -> Tuple[Branch, List[CypherVariable], List[bool]]:
        """
        Return the query branch, variables of a list of factor/product names
        We do this by grouping into the containing hierarchies and traversing each branch before collapsing
        returns:
                branch: The new branch object to continue the query with
                variables: The list of CypherVariable that contains the query result
                is_product: The list of True if the factor is a product
        """
        # TODO: tidy this all up
        names, plurals, local, remote, remote_paths = self._get_factor_query_paths(names, plurals)
        variables = {}
        is_products = {}
        branch = self.branch

        for (basehier, plural), factor_product_tuples in remote.items():
            paths = remote_paths[(basehier, plural)]
            travel = branch.traverse(*paths)
            funcs = []
            for name, is_product in factor_product_tuples:
                if is_product:
                    func = GET_PRODUCT.format(name=name)
                else:
                    func = GET_FACTOR.format(name=name)
                funcs.append(func)
            operate = travel.operate(*funcs, h=travel.current_hierarchy)
            if collect_plurals:
                if plural:
                    branch = branch.collect([], [operate])
                else:
                    branch = branch.collect([operate], [])
                for v, (name, is_product) in zip(operate.current_variables, factor_product_tuples):
                    variables[(name, plural)] = branch.action.transformed_variables[v]
                    is_products[(name, plural)] = is_product
            else:
                branch = operate
                for v, (name, is_product) in zip(operate.current_variables, factor_product_tuples):
                    variables[(name, plural)] = v
                    is_products[(name, plural)] = is_product

        if len(local):
            funcs = []
            for name, plural, is_product in local:
                if is_product:
                    func = GET_PRODUCT.format(name=name)
                elif plural and collect_plurals:
                    func = GET_FACTOR_FORCE_PLURAL.format(name=name)
                else:
                    func = GET_FACTOR.format(name=name)
                funcs.append(func)
            branch = branch.operate(*funcs, h=self.hierarchy_variable)
            for v, (k, plural, is_product) in zip(branch.action.output_variables, local):
                variables[(k, plural)] = v
                is_products[(k, plural)] = is_product

        # now propagate variables forward
        values = [variables[(name, plural)] for name, plural in zip(names, plurals)]
        variables = branch.get_variables(values)
        return branch, variables, [is_products[(name, plural)] for name, plural in zip(names, plurals)]

    def _get_factor(self, name, plural):
        branch, factor_variables, is_products = self._get_multifactor_query([name], [plural], collect_plurals=False)
        return SingleFactorFrozenQuery(self.handler, branch, name, factor_variables[0], is_products[0], self)

    def _get_factor_table_query(self, item) -> FactorFrozenQuery:
        """
        __getitem__ is for returning factors and ids
        There are three types of getitem input values:
        List: [[a, b]], where labelled table-like rows are output
        Tuple: [a, b], where a list of unlabelled dictionaries are output
        str: [a], where a single value is returned

        In all three cases, you still need to specify plural or singular forms.
        This allows you to have a row of n dimensional heterogeneous data.
        returns query and the labels (if any) for the table
        """
        if isinstance(item, tuple):  # return without headers
            return_keys = list(item)
            keys = list(item)
        elif isinstance(item, list):
            keys = item
            return_keys = item
        elif item is None:
            raise TypeError("item must be of type list, tuple, or str")
        else:
            raise KeyError(f"Unknown item {item} for `{self}`")
        plurals = [not self.data.is_singular_name(i) for i in item]
        branch, factor_variables, is_products = self._get_multifactor_query(keys, plurals, collect_plurals=len(plurals) > 0)
        if len(factor_variables) == 1:
            return SingleFactorFrozenQuery(self.handler, branch, keys[0], factor_variables[0], is_products[0], self.parent)
        return TableFactorFrozenQuery(self.handler, branch, keys, factor_variables, plurals, is_products, return_keys, self.parent)

    def _filter_by_identifiers(self, identifiers: List[Union[str, int, float]]) -> 'DefiniteHierarchyFrozenQuery':
        idname = self.hierarchy_type.idname
        if isinstance(identifiers, np.ndarray):
            identifiers = identifiers.ravel()
        new = self.branch.add_data(identifiers)
        identifiers_var = new.current_variables[0]
        branch = new.filter('{h}.' + idname + ' in {identifiers}', h=self.hierarchy_variable, identifiers=identifiers_var)
        return DefiniteHierarchyFrozenQuery(self.handler, branch, self.hierarchy_type, self.hierarchy_variable, identifiers, self)

    def _filter_by_identifier(self, identifier: Union[str, int, float]) -> 'DefiniteHierarchyFrozenQuery':
        idname = self.hierarchy_type.idname
        new = self.branch.add_data(identifier)
        identifier_var = new.current_variables[0]
        branch = new.filter('{h}.' + idname + ' = {identifier}', h=self.hierarchy_variable, identifier=identifier_var)
        return DefiniteHierarchyFrozenQuery(self.handler, branch, self.hierarchy_type, self.hierarchy_variable, [identifier], self)

    def __getitem__(self, item):
        """
        If there is a scalar, then return a SingleFactorFrozenQuery otherwise assume its a request for a table
        The order of resolution is:
            vector hierarchy/
        """
        if isinstance(item, Dissociated):
            return self._filter_by_boolean(item)
        if isinstance(item, (list, tuple, np.ndarray)):
            valids = list(map(self.data.is_valid_name, item))
            if all(valids):
                return self._get_factor_table_query(item)
            elif any(valids):
                bad = [i for i, v in zip(item, valids) if not v]
                raise KeyError(f"{bad} are not recognised")
            else:
                return self._filter_by_identifiers(item)
        if not self.data.is_valid_name(item):
            return self._filter_by_identifier(item)  # then assume its an ID
        if isinstance(item, str) and self.data.is_valid_name(item):
            return self._get_factor_table_query([item])
        else:
            return getattr(self, item)

    def __getattr__(self, item):
        plural = self.data.is_plural_name(item)
        factor = self.data.is_factor_name(item)
        exists = self.data.is_singular_name(item) or plural
        if not exists:
            autosuggest(item, self.handler.data, self.hierarchy_type)
        if factor:
            return self._get_factor(item, plural=plural)
        else:
            return self._get_hierarchy(item, plural=plural)


def _autosuggest(a, data, relative_to=None):
    import textdistance
    distance, distance_reverse = textdistance.jaro_winkler, True
    suggestions = []
    if relative_to is not None:
        relative_to, data = _convert_obj(relative_to, data)

    for h in data.hierarchies:
        newsuggestions = []
        if relative_to is not None:
            try:
                data.find_hierarchy_paths(relative_to, h, plural=False)
            except (nx.NetworkXNoPath, AmbiguousPathError):
                plural = True
                hier = h.plural_name
                factors = [data.plural_name(f) for f in h.products_and_factors]
            else:
                plural = False
                hier = h.singular_name
                factors = h.products_and_factors
            newsuggestions.append(hier)
            newsuggestions += factors
        else:
            newsuggestions += [h.singular_name, h.plural_name] + h.products_and_factors
            newsuggestions += [data.plural_name(f) for f in h.products_and_factors]
        try:
            newsuggestions.index(a)
        except ValueError:
            suggestions += newsuggestions
        else:
            return [a]
    inorder = sorted(list(set(suggestions)), key=lambda x: distance(a, x), reverse=distance_reverse)
    return inorder[:3]


def autosuggest(a, data, relative_to=None):
    suffix = '\nYou can learn more about an object or attribute by using `explain(obj/attribute, ...)`'
    try:
        l = _autosuggest(a, data, relative_to)
        string = '\n'.join([f'{i}. {s}' for i, s in enumerate(l, start=1)])
    except ImportError:
        raise AttributeError(f"`{a}` not understood.{suffix}")
    raise AttributeError(f"`{a}` not understood, did you mean one of:\n{string}{suffix}")