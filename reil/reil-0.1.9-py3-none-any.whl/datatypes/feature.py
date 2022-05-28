# -*- coding: utf-8 -*-
'''
Feature, FeatureGenerator, FeatureSet classes
=============================================

`FeatureSet` is The main datatype used to communicate `state`s, `action`s,
and `reward`s, between objects in `reil`. `FeatureSet` is basically a
dictionary that contains instances of `Feature`.
`FeatureGenerator` allows for generating new `Feature` instances. It can
`generate` a new value or turn an input into a `Feature`. It enforces
`categorical` and `numerical` constraints, and produces `normalized` value.
'''
from __future__ import annotations

import dataclasses
import itertools
import random
from copy import copy
from functools import cached_property
from math import isclose
from typing import (Any, Callable, Dict, Generator, Iterable, Iterator, List,
                    Literal, Optional, Tuple, Union)

from reil.serialization import deserialize, full_qualname

MISSING = '__missing_feature__'

MissingType = Literal['__missing_feature__']


@dataclasses.dataclass(frozen=True)
class Feature:
    '''
    Attributes
    ----------
    name:
        Name of the data.

    value:
        Value of the data. Can be one item, or a tuple of items of the same
        type.

    is_numerical:
        Is the value numerical?

    normalized:
        The normal form of the value.

    categories:
        A tuple of categories that the value can take.

    lower:
        The lower limit for numerical values.

    upper:
        The upper limit for numerical values.
    '''
    name: str
    value: Optional[Union[Any, Tuple[Any, ...], MissingType]] = None
    is_numerical: Optional[bool] = dataclasses.field(
        default=None, repr=False, compare=False)
    categories: Optional[Tuple[Any, ...]] = dataclasses.field(
        default=None, repr=False, compare=False)
    lower: Optional[Any] = dataclasses.field(
        default=None, repr=False, compare=False)
    upper: Optional[Any] = dataclasses.field(
        default=None, repr=False, compare=False)
    index: Optional[int] = dataclasses.field(
        default=None, repr=False, compare=False)
    normalized: Optional[
        Union[Tuple[float, ...], Tuple[int, ...]]] = dataclasses.field(
            default=None, repr=False, compare=False)
    dict_fields: Tuple[str, ...] = dataclasses.field(
        default=('name', 'value'), init=False, repr=False, compare=False)

    def __post_init__(self):
        if self.is_numerical is None:
            return

        if self.is_numerical:
            if self.categories is not None:
                raise ValueError('Numerical type cannot have categories.')

            self.__dict__['dict_fields'] = ('name', 'value', 'lower', 'upper')
        else:
            if self.lower is not None and self.upper is not None:
                raise ValueError(
                    'Categorical type cannot have lower and upper.')

            self.__dict__['dict_fields'] = ('name', 'value', 'categories')

    @classmethod
    def numerical(
            cls, name: str,
            value: Optional[Union[Any, Tuple[Any, ...]]] = None,
            lower: Optional[Any] = None, upper: Optional[Any] = None,
            normalized: Optional[Tuple[float, ...]] = None,
            index: Optional[int] = None):
        '''Create a numerical instance of `Feature`.'''
        return cls(
            name=name, value=value, is_numerical=True,
            lower=lower, upper=upper, normalized=normalized, index=index)

    @classmethod
    def categorical(
            cls, name: str,
            value: Optional[Union[Any, Tuple[Any, ...], MissingType]] = None,
            categories: Optional[Tuple[Any, ...]] = None,
            normalized: Optional[Tuple[float, ...]] = None,
            index: Optional[int] = None):
        '''Create a categorical instance of `Feature`.'''
        return cls(
            name=name, value=value, is_numerical=False,
            categories=categories, normalized=normalized, index=index)

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        try:
            is_numerical = config.pop('is_numerical')
            if is_numerical:
                return cls.numerical(**config)
            return cls.categorical(**config)
        except KeyError:
            return cls(**config)

    def get_config(self) -> Dict[str, Any]:
        config = {
            key: value
            for key, value in self.__dict__.items()
            if value is not None}

        del config['dict_fields']

        return config

    @cached_property
    def as_dict(self):
        '''
        Return the data as a dictionary.

        Returns
        -------
        :
            The data as a dictionary.
        '''
        return {field: self.__dict__[field] for field in self.dict_fields}

    def __add__(self, other: Any):
        my_type = type(self)
        if type(other) != my_type:
            raise TypeError(
                "unsupported operand type(s) for +: "
                f"'{my_type}' and '{type(other)}'")

        for k, v in self.__dict__.items():
            if k not in ('value', 'normalized', 'index'):
                if other.__dict__[k] != v:
                    raise TypeError(
                        f'Different {k} values: {v} != {other.__dict__[k]}.')

        new_value = self.__dict__['value'] + other.value
        if self.is_numerical:
            return my_type.numerical(
                name=self.name, value=new_value,
                lower=self.__dict__.get('lower'),
                upper=self.__dict__.get('upper'))
        else:
            return my_type.categorical(
                name=self.name, value=new_value,
                categories=self.__dict__.get('categories'))


NoneFeature = Feature('None')


@dataclasses.dataclass(frozen=True)
class FeatureGenerator:
    '''
    A class to generate `Feature`s.

    Attributes
    ----------
    name:
        Name of the data.

    is_numerical:
        Is the feature to be generated numerical?

    categories:
        A tuple of categories that the value can take.

    probabilities:
        A tuple of probabilities corresponding with each category. This can
        be used to generate new random `Feature` instances.

    mean:
        The mean for numerical values. This can
        be used to generate new random `Feature` instances.

    stdev:
        The standard deviation for numerical values. This can
        be used to generate new random `Feature` instances.

    lower:
        The lower limit for numerical values.

    upper:
        The upper limit for numerical values.

    normalizer:
        For a categorical `FeatureGenerator`, normalizer is a dictionary of
        categories as keys and their corresponding one-hot encodings as values.
        For a numerical `FeatureGenerator`, normalizer is a function that
        accepts the value and returns its normalized value.

    randomized:
        Determines for the `generator`, whether the new `Feature` should be
        randomly generated.

    generator:
        A function that accepts a `FeatureGenerator` instance, and produces
        a value for the new `Feature`.

    allow_missing:
        If `True`, a categorical generator can generate a `MISSING` instance.
        Also the normalized form will have one more categories to account for
        `MISSING`.
    '''
    name: str
    is_numerical: bool = dataclasses.field(
        default=False, repr=False, compare=False)
    categories: Optional[Tuple[Any, ...]] = None
    probabilities: Optional[Tuple[float, ...]] = None
    mean: Optional[Any] = None
    stdev: Optional[Any] = None
    lower: Optional[Any] = None
    upper: Optional[Any] = None
    step: Optional[Any] = None
    normalizer: Optional[Any] = dataclasses.field(
        default=None, init=False, repr=False, compare=False)
    randomized: Optional[bool] = True
    generator: Optional[
        Callable[[FeatureGenerator], Union[Any, Tuple[Any, ...]]]] = None
    allow_missing: bool = False
    count: Optional[int] = dataclasses.field(
        default=None, init=False, repr=False, compare=False)
    recent_value: Tuple[Any, Feature] = dataclasses.field(
        default=(None, Feature('')), init=False, repr=False, compare=False)

    @classmethod
    def continuous(
            cls, name: str,
            mean: Optional[float] = None, stdev: Optional[float] = None,
            lower: Optional[float] = None, upper: Optional[float] = None,
            generator: Optional[Callable[
                [FeatureGenerator], Union[Any, Tuple[Any, ...]]]] = None,
            randomized: Optional[bool] = None):
        return cls(
            name=name, is_numerical=True, lower=lower, upper=upper, mean=mean,
            stdev=stdev, generator=generator, randomized=randomized,
            allow_missing=False)

    @classmethod
    def discrete(
            cls, name: str,
            lower: Optional[float] = None, upper: Optional[float] = None,
            step: float = 1.0,
            generator: Optional[Callable[
                [FeatureGenerator], Union[Any, Tuple[Any, ...]]]] = None,
            randomized: Optional[bool] = None):
        return cls(
            name=name, is_numerical=True, lower=lower, upper=upper, step=step,
            generator=generator, randomized=randomized,
            allow_missing=False)

    @classmethod
    def categorical(
            cls, name: str,
            categories: Optional[Tuple[Any, ...]] = None,
            probabilities: Optional[Tuple[float, ...]] = None,
            generator: Optional[Callable[
                [FeatureGenerator], Union[Any, Tuple[Any, ...]]]] = None,
            randomized: Optional[bool] = None, allow_missing: bool = False):
        return cls(
            name=name, is_numerical=False,
            categories=categories, probabilities=probabilities,
            generator=generator, randomized=randomized,
            allow_missing=allow_missing)

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        step = config.get('step')
        is_numerical = config.pop('is_numerical')
        if is_numerical:
            if step:
                return cls.discrete(**config)
            return cls.continuous(**config)
        return cls.categorical(**config)

    def get_config(self) -> Dict[str, Any]:
        config = {
            key: value
            for key, value in self.__dict__.items()
            if value is not None and key not in ('recent_value', 'normalizer')}

        if 'count' in config:
            del config['count']
        if self.is_numerical:
            del config['allow_missing']

        return config

    def __post_init__(self):
        self.__dict__['recent_value'] = (None, None)

        if self.is_numerical:
            if self.categories is not None:
                raise ValueError('Numerical type cannot have categories.')
            if self.allow_missing:
                raise TypeError(
                    'Only categorical type can accept missing values.')
            if ((self.mean is not None or self.stdev is not None)
                    and self.step is not None):
                raise TypeError(
                    'Variable with mean or stdev cannot have step.')

            self._process_numerical()
        else:
            if (
                    self.lower is not None or
                    self.upper is not None or
                    self.step is not None or
                    self.mean is not None or
                    self.stdev is not None):
                raise ValueError(
                    'Categorical type cannot have any of '
                    'lower, upper, step, mean, or stdev.')

            probabilities = self.probabilities
            categories = self.categories
            if probabilities is not None:
                if not isclose(sum(probabilities), 1.0):
                    raise ValueError(
                        'probabilities should add up to 1.0.'
                        f'Got {sum(probabilities)}')
                if categories is None:
                    raise ValueError(
                        'probabilities cannot be set for None categories.')
                if len(probabilities) != len(categories):
                    raise ValueError(
                        'Size mismatch. '
                        f'{len(categories)} categories vs. '
                        f'{len(probabilities)} probabilities')

            self._process_categorical()

    def __call__(
        self, value: Optional[Union[Any, Tuple[Any, ...], MissingType]] = None
    ) -> Feature:
        if value is None:
            if (gen := self.generator) is None:
                raise RuntimeError('generator not found.')
            _value = gen(self)
        else:
            _value = value

        if _value == self.recent_value[0]:
            return copy(self.recent_value[1])

        if self.is_numerical:
            if _value == MISSING:
                raise ValueError('Numerical feature cannot accept MISSING.')

            return_value = self._call_numerical(_value)  # type: ignore
        else:
            return_value = self._call_categorical(_value)  # type: ignore

        self.__dict__['recent_value'] = (_value, return_value)

        return return_value

    def _process_categorical(self):
        cats = self.categories
        allow_missing = int(self.allow_missing)
        if cats is None:
            return

        self.__dict__['count'] = cat_count = len(cats)

        cat_count = cat_count - 1 + allow_missing
        normalizer = {}
        for i, c in enumerate(cats[:-1]):
            temp = [0] * cat_count
            temp[i] = 1
            normalizer[c] = tuple(temp)

        temp = [0] * cat_count
        temp[-1] = allow_missing
        normalizer[cats[-1]] = tuple(temp)

        if allow_missing:
            normalizer[MISSING] = tuple([0] * cat_count)

        self.__dict__['normalizer'] = normalizer

    def _process_numerical(self):
        lower: Optional[float] = self.lower  # type: ignore
        upper: Optional[float] = self.upper  # type: ignore
        step: Optional[float] = self.step  # type: ignore

        if lower is None or upper is None or upper == lower:
            self.__dict__['normalizer'] = lambda _: None  # type: ignore
        else:
            if lower > upper:
                raise ValueError(
                    f'lower ({lower}) cannot be '
                    f'greater than upper ({upper}).')

            denominator = upper - lower

            def normalizer(x: float) -> float:
                return (x - lower) / denominator  # type: ignore

            self.__dict__['normalizer'] = normalizer

            if (lower is not None and upper is not None and step is not None):
                self.__dict__['count'] = int((upper - lower) / step) + 1

    def _call_categorical(
            self, value: Union[Any, Tuple[Any, ...], MissingType]
    ) -> Feature:
        normalizer = self.normalizer
        categories = self.categories or ()
        try:
            index = categories.index(value)
        except ValueError:
            index = None

        if normalizer is None:
            normalized = None
        elif (value in categories) or (
                self.allow_missing and value == MISSING):
            normalized = normalizer[value]
        else:
            try:
                normalized = tuple(
                    itertools.chain(
                        *(normalizer[d]
                          for d in value)))  # type: ignore
            except KeyError:
                if (value == MISSING and not self.allow_missing):
                    raise ValueError('MISSING is not allowed.')
                else:
                    raise ValueError(
                        f'{value} is not '
                        f'in the categories={categories}.')

        instance = Feature.categorical(
            name=self.name, value=value, categories=self.categories,
            normalized=normalized, index=index)

        return instance

    def _call_numerical(
            self, value: Union[Any, Tuple[Any, ...]]
    ) -> Feature:
        normalizer = self.normalizer
        lower = self.lower
        upper = self.upper
        index = None

        if value is None:
            normalized = None

        elif isinstance(value, tuple):
            if (lower is not None
                    and min(value) < lower):  # type: ignore
                raise ValueError(f'Lower bound ({lower}) violated:\n {value}')

            if (upper is not None
                    and max(value) > upper):  # type: ignore
                raise ValueError(f'Upper bound ({upper}) violated:\n {value}')

            normalized = tuple(normalizer(d) for d in value)  # type: ignore

        else:
            if (lower is not None
                    and value < lower):  # type: ignore
                raise ValueError(f'Lower bound ({lower}) violated:\n {value}')

            if (upper is not None
                    and value > upper):  # type: ignore
                raise ValueError(f'Upper bound ({upper}) violated:\n {value}')

            normalized = normalizer(value)  # type: ignore

            if self.count is not None:
                _index = (value - lower) / self.step
                index = int(_index)
                if index != _index:
                    raise ValueError(
                        f'{value} is not a valid value for this '
                        'discrete variable.')

        instance: Feature = \
            Feature.numerical(
                name=self.name, value=value,   # type: ignore
                lower=lower, upper=upper,
                normalized=normalized, index=index)

        return instance

    def generate_all(
            self, mask_dict: Optional[Dict[Any, Any]] = None,
            exclude_masked_values: bool = False) -> Iterator[Feature]:
        mask = mask_dict or {}
        if self.count is None:
            raise TypeError('Feature is not iterable.')
        if self.is_numerical:
            lower = self.lower
            step = self.step
            count = self.count
            iterator = (
                lower + i * step  # type: ignore
                for i in range(count)
            )
        else:
            iterator = self.categories or ()

        if exclude_masked_values:
            return (
                self.__call__(v)
                for v in iterator
                if v not in mask)

        return (
            self.__call__(mask.get(v, v))
            for v in iterator)

    def generate_indexes(
            self, mask_dict: Optional[Dict[Any, Any]] = None,
            exclude_masked_values: bool = False) -> Iterator[int]:
        mask = mask_dict or {}
        if self.count is None:
            raise TypeError('Feature is not iterable.')
        if self.is_numerical:
            iterator = {
                i * self.step: i  # type: ignore
                for i in range(self.count)
            }
        else:
            iterator = {v: i for i, v in enumerate(self.categories or ())}

        if exclude_masked_values:
            return (i for v, i in iterator.items() if v not in mask)

        return (iterator[mask.get(v, v)] for v in iterator)

    def byindex(self, index: int) -> Feature:
        if self.count is None:
            raise TypeError('The feature is not iterable.')
        if self.lower is None:
            if self.categories is None:
                raise IndexError('No categories defined.')
            else:
                return self.__call__(self.categories[index])

        return self.__call__(self.lower + index * self.step)  # type: ignore


class FeatureSet:
    '''
    The main datatype used to communicate `state`s and `action`s between
    objects in `reil`.
    '''

    def __init__(
            self, data: Union[Feature, Iterable[Feature], FeatureSet],
            index: Optional[int] = None):
        '''
        Arguments
        ---------
        data:
            One or a sequence of `Feature`s.

        index:
            An integer value for the index. If omitted, the index will be a
            tuple of indices of Features of the FeatureSet.
        '''
        temp: Dict[str, Feature] = {}
        _data: Iterable[Any] = (
            data if hasattr(data, '__iter__') else [data])  # type: ignore

        for d in _data:
            if isinstance(d, Feature):
                name = d.name
                if name in temp:
                    raise KeyError(f'Duplicate name ({name}).')

                temp[name] = d
            else:
                raise TypeError(f'Unknown input type {type(d)} for item: {d}')

        self._data = temp
        self._index = index

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(
            data=(
                deserialize(feature)  # type: ignore
                for feature in config.get('data', {})))

    def get_config(self) -> Dict[str, Any]:
        return {'data': [
            {
                'class_name': full_qualname(feature),
                'config': feature.get_config(),
                '__needs_deserialization__': True
            }
            for feature in self._data.values()]}

    @cached_property
    def value(self):
        '''
        Return a dictionary with elements' names as keys and
        their respective values as values.

        Returns
        -------
        :
            Names of the elements and their values.
        '''
        return {name: v.value for name, v in self._data.items()}

    @cached_property
    def index(self):
        '''
        Return a dictionary with elements' names as keys and
        their respective index as values.

        Returns
        -------
        :
            Names of the elements and their indexes.
        '''
        if self._index is not None:
            return {' '.join(name for name in self._data): self._index}

        return {name: v.index for name, v in self._data.items()}

    @cached_property
    def lower(self):
        '''
        Return all `lower` attributes.

        Returns
        -------
        :
            `lower` attribute of all `NumericalData` variables with their names
            as keys.
        '''
        return {name: v.lower for name, v in self._data.items()}

    @cached_property
    def upper(self):
        '''
        Return all `upper` attributes.

        Returns
        -------
        :
            `upper` attribute of all `NumericalData` variables with their names
            as keys.
        '''
        return {name: v.upper for name, v in self._data.items()}

    @cached_property
    def categories(self):
        '''
        Return all `categories` attributes.

        Returns
        -------
        :
            `categories` attribute of all `CategoricalData` variables with
            their names as keys.
        '''
        return {name: v.categories for name, v in self._data.items()}

    @cached_property
    def normalized(self):
        '''
        Normalize all items in the instance.

        Returns
        -------
        :
            A `FeatureSet` of the normalized values of all the items in the
            instance, in the form of numerical `Feature`s.
        '''
        return FeatureSet(
            FeatureGenerator.continuous(name=name, lower=0, upper=1)
            (v.normalized)  # type: ignore
            for name, v in self._data.items())

    @cached_property
    def flattened(self):
        """Combine values of all items in the instance.

        Returns
        -------
        :
            A list that contains all the values of all the items.
        """
        def make_iterable(x: Any) -> Iterable[Any]:
            return x if hasattr(x, '__iter__') else [x]

        return list(
            itertools.chain(
                *[make_iterable(sublist) for sublist in self.value.values()]))

    def update(self, other: FeatureSet):
        self._data.update(other._data)
        for v in (
                'value', 'index', 'lower', 'upper',
                'categories', 'normalized', 'flattened'):
            if v in self.__dict__:
                del self.__dict__[v]

    def get(self, key: str, return_val: Optional[Feature] = None):
        return self._data.get(key, return_val)

    def split(self):
        """Split the `FeatureSet` into a list of `FeatureSet`s.

        Returns
        -------
        :
            All items in the instance as separate `FeatureSet` instances.
        """
        if len(self) == 1:
            d = next(iter(self._data.values()))
            if not isinstance(d.value, (list, tuple)):
                splitted_list = FeatureSet(d)
            else:
                temp = d.as_dict
                cls = type(d)
                value = temp['value']
                del temp['value']
                if 'is_numerical' in temp:
                    del temp['is_numerical']

                splitted_list = [
                    FeatureSet(cls(value=v, **temp))
                    for v in value]

        else:
            splitted_list = list(FeatureSet(v) for v in self._data.values())

        return splitted_list

    def __iter__(self):
        return iter(self._data.values())

    def __getitem__(self, k: str):
        return self._data.__getitem__(k)

    def __len__(self):
        return self._data.__len__()

    def __hash__(self):
        return hash(tuple(self._data.items()))

    def __eq__(self, other: Any):
        return isinstance(other, type(self)) and (self._data == other._data)

    def __add__(self, other: Any):
        if not isinstance(other, FeatureSet):
            new_data = FeatureSet(other)
        else:
            new_data = other

        # if not isinstance(new_data, FeatureSet):
        #     raise TypeError(
        #         'Concatenation of type FeatureSet'
        #         f' and {type(other)} not implemented!')

        overlaps = set(new_data._data).intersection(self._data)
        if overlaps:
            raise ValueError(f'Objects already exist: {overlaps}.')

        return FeatureSet(itertools.chain(
            self._data.values(), new_data._data.values()))

    def __neg__(self):
        temp = [v
                for v in self._data.values()]
        for item in temp:
            if hasattr(item.value, '__neg__'):
                neg_value = -item.value  # type: ignore
                lower: Any = item.__dict__.get('lower') or neg_value
                upper: Any = item.__dict__.get('upper') or neg_value
                if lower <= neg_value <= upper:
                    object.__setattr__(item, 'value', neg_value)
                else:
                    raise ValueError(
                        f'Bounds violated: lower: {lower}, '
                        f'upper: {upper}, '
                        f'negative value: {neg_value}')

        return FeatureSet(temp)  # type: ignore

    def __repr__(self):
        return f'[{super().__repr__()} -> {self._data}]'

    def __str__(self):
        return f"[{', '.join((d.__str__() for d in self._data.items()))}]"


Index = Tuple[int, ...]

FeatureGeneratorType = Generator[
    # Union[
    #     Iterator[FeatureSet],  # return feature
    #     Tuple[Iterator[FeatureSet], ...],  # return feature split
    #     Iterator[Index],  # return index
    #     Tuple[Iterator[int], ...],  # return index split
    #     int,  # return count
    #     Tuple[int, ...],  # return count split | choose index
    #     FeatureSet,  # choose feature | lookup ...
    #     None],
    Any, str, None]


class FeatureGeneratorSet:
    def __init__(
            self, feature_generators: Union[
                FeatureGenerator, Iterable[FeatureGenerator]] = ()):
        '''
        Arguments
        ---------
        feature_generators:
            One or a sequence of `FeatureGenerator`s.
        '''
        temp: Dict[str, FeatureGenerator] = {}
        fgs: Iterable[Any] = (
            feature_generators if hasattr(feature_generators, '__iter__')
            else [feature_generators])  # type: ignore

        for fg in fgs:
            if isinstance(fg, FeatureGenerator):
                name = fg.name
                if name in temp:
                    raise KeyError(f'Duplicate name ({name}).')

                temp[name] = fg
            else:
                raise TypeError(
                    f'Unknown input type {type(fg)} for item: {fg}')

        self._generators = temp
        self._masked_values: Dict[str, Dict[Any, Any]] = {
            name: {} for name in temp
        }

        self.count = tuple(g.count for g in temp.values())

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        instance = cls(
            feature_generators=(
                deserialize(feature_gen)  # type: ignore
                for feature_gen in config.get('feature_generators', [])))
        instance.__dict__.update(config['internal_states'])

        return instance

    def get_config(self) -> Dict[str, Any]:
        return {
            'feature_generators': [
                {
                    'class_name': full_qualname(feature_gen),
                    'config': feature_gen.get_config(),
                    '__needs_deserialization__': True
                }
                for feature_gen in self._generators.values()],
            'internal_states': {'_masked_values': self._masked_values}
        }

    def __call__(
            self, value: Optional[Dict[str, Any]] = None) -> FeatureSet:
        _value = {} if value is None else value

        try:
            return_value = FeatureSet(
                gen(self._masked_values.get(name, {}).get(
                    (v := _value.get(name)), v))
                for name, gen in self._generators.items())
        except TypeError:
            raise RuntimeError(
                'No generator is found for one or some of the features.')

        return return_value

    def mask(self, feature_name: str, mask_dict: Dict[Any, Any]):
        try:
            for k, v in mask_dict.items():
                self._masked_values[feature_name][k] = v
        except KeyError:
            raise ValueError(f'Feature {feature_name} not found.')

    def unmask(self, feature_name: str, values: Optional[List[Any]] = None):
        if feature_name not in self._generators:
            raise ValueError(f'Feature {feature_name} not found.')

        if values is None:
            self._masked_values[feature_name] = {}
        else:
            for v in values:
                del self._masked_values[feature_name][v]

    def generate_all(
            self, exclude_masked_values: bool = False, split: bool = False
    ) -> Union[Iterator[FeatureSet], Tuple[Iterator[FeatureSet], ...]]:
        gens = self._generators
        masked = self._masked_values

        # non_iterables = set(
        #     name for name, gen in gens.items()
        #     if not gen.iterable)
        # if non_iterables:
        #     raise TypeError(
        #         f'These generators are non iterable: {non_iterables}')
        if split:
            return tuple(
                (FeatureSet(x) for x in gen.generate_all(
                    masked.get(name), exclude_masked_values))
                for name, gen in gens.items())
        else:
            return (FeatureSet(x) for x in itertools.product(*(
                tuple(gen.generate_all(
                    masked.get(name), exclude_masked_values))
                for name, gen in gens.items())))

    def generate_indexes(
            self, exclude_masked_values: bool = False, split: bool = False
    ) -> Union[Iterator[Index], Tuple[Iterator[int], ...]]:
        gens = self._generators
        masked = self._masked_values

        # non_iterables = set(
        #     name for name, gen in gens.items()
        #     if not gen.iterable)
        # if non_iterables:
        #     raise TypeError(
        #         f'These generators are non iterable: {non_iterables}')
        if split:
            return tuple(
                (i for i in gen.generate_indexes(
                    masked.get(name), exclude_masked_values))
                for name, gen in gens.items())
        else:
            return itertools.product(*(
                tuple(gen.generate_indexes(
                    masked.get(name), exclude_masked_values))
                for name, gen in gens.items()))

    def make_generator(self) -> FeatureGeneratorType:

        query = yield
        while True:
            parsed_query = self.parse_query(query)
            result = None
            if parsed_query['command'] == 'return':
                item = parsed_query['item']
                exclusive = parsed_query.get('exclusive', False)
                split = parsed_query.get('split', False)
                if item == 'feature':
                    result = self.generate_all(
                        exclude_masked_values=exclusive, split=split)
                elif item == 'index':
                    result = self.generate_indexes(
                        exclude_masked_values=exclusive, split=split)
                else:  # item == 'count'
                    # temp = self.generate_indexes(
                    #     exclude_masked_values=exclusive, split=True)
                    # result = tuple(len(tuple((x))) for x in temp)
                    result = self.count
            elif parsed_query['command'] == 'choose':
                exclusive = parsed_query.get('exclusive', False)
                if parsed_query['item'] == 'feature':
                    result = random.choice(list(self.generate_all(
                        exclude_masked_values=exclusive)))
                else:  # parsed_query['command'] == 'index'
                    result = random.choice(list(self.generate_indexes(
                        exclude_masked_values=exclusive)))
            else:  # parsed_query['command'] == 'lookup'
                result = self.byindex(parsed_query['index'])

            query = yield result

    def byindex(
            self, index: Union[int, Tuple[int, ...], Dict[str, int]]
    ) -> FeatureSet:
        if [x for x in self.count if x is None]:
            raise TypeError('This FeatureGeneratorSet is not iterable.')
        if isinstance(index, int):
            gen = self.generate_all(exclude_masked_values=True)
            for i, v in enumerate(gen):
                if i == index:
                    return FeatureSet(v, index=index)  # type: ignore
            raise IndexError(f'Index out of range {index}.')

        if len(index) != len(self._generators):
            raise IndexError(
                'Number of indexes should match the number of generators.\n'
                f'{len(index)} != {len(self._generators)}')
        elif isinstance(index, dict):
            _ind = index
        else:
            _ind = {
                name: i
                for name, i in zip(self._generators, index)}

        temp = FeatureSet(
            g.byindex(_ind[name])
            for name, g in self._generators.items())

        for name, mask_data in self._masked_values.items():
            if (old_val := temp[name].value) in mask_data:
                temp._data[name] = self._generators[name].__call__(
                    mask_data[old_val])

        return temp

    @staticmethod
    def parse_query(q: str) -> Dict[str, Any]:  # noqa: C901
        _q = q.strip().casefold()
        words = _q.split()
        command = words[0]
        allowed_words = (
            ('return', 'lookup', 'choose', 'help'),
            ('feature', 'index', 'count'),
        )

        parsed: Dict[str, Any] = {'command': command}
        if command == 'return':
            if words[1] not in allowed_words[1]:
                raise RuntimeError(
                    f'Expected {allowed_words[1]}. '
                    f'Received {words[1]}')

            parsed['item'] = words[1]

            length = len(words)
            if length >= 4:
                if words[3] != 'split':
                    raise RuntimeError(f'Unknown parameter: {words[3]}.')
                if words[2] != 'exclusive':
                    raise RuntimeError(f'Unknown parameter: {words[2]}.')
                parsed['split'] = True
                parsed['exclusive'] = True
            elif length == 3:
                if words[2] == 'split':
                    parsed['split'] = True
                    parsed['exclusive'] = False
                elif words[2] == 'exclusive':
                    parsed['split'] = False
                    parsed['exclusive'] = True
                else:
                    raise RuntimeError(f'Unknown parameter: {words[2]}.')

        elif command == 'choose':
            if words[1] not in allowed_words[1][:-1]:
                raise RuntimeError(
                    f'Expected {allowed_words[1][:-1]}. '
                    f'Received {words[1]}')

            parsed['item'] = words[1]

            length = len(words)
            if length >= 3:
                if words[2] != 'exclusive':
                    raise RuntimeError(f'Unknown parameter: {words[2]}.')
                parsed['exclusive'] = True
            else:
                parsed['exclusive'] = False

        elif command == 'lookup':
            temp = _q[6:].replace(
                '(', '').replace(')', '').replace('[', '').replace(']', '')
            lookup_index = tuple(map(int, temp.split(',')))
            if len(lookup_index) == 1 and temp.find(',') == -1:
                lookup_index = lookup_index[0]
            parsed = {'command': 'lookup', 'index': lookup_index}

        elif command == 'help':
            print(
                'Return syntax: '
                'return feature/index/count [exclusive] [split]\n'
                'Choose syntax: '
                'choose feature/index [exclusive]\n'
                'Lookup syntax: '
                'lookup comma_separated_index')
        else:
            raise ValueError(f'Unknown command {command}.')

        return parsed

    def __iter__(self):
        return iter(self._generators.values())

    def __getitem__(self, k: str):
        return self._generators.__getitem__(k)

    def __len__(self):
        return self._generators.__len__()

    def __eq__(self, other: Any):
        return isinstance(other, type(self)) and (
            self._generators == other._generators)

    def __add__(self, other: Any):
        if not isinstance(other, FeatureGeneratorSet):
            new_data = FeatureGeneratorSet(other)
        else:
            new_data = other

        overlaps = set(new_data._generators).intersection(self._generators)
        if overlaps:
            raise ValueError(f'Objects already exist: {overlaps}.')

        return FeatureGeneratorSet(itertools.chain(
            self._generators.values(), new_data._generators.values()))

    def __repr__(self):
        return f'[{super().__repr__()} -> {self._generators}]'

    def __str__(self):
        return f'''[
            {", ".join((d.__str__() for d in self._generators.items()))}
        ]'''


def change_to_missing(feature: Feature) -> Feature:
    if feature.is_numerical:
        raise TypeError('Only categorical features can have missing.')
    categories = feature.categories
    normalized = feature.normalized
    if categories is None:
        raise ValueError('No categories defined!')
    if normalized is None:
        raise ValueError(
            'Cannot generate normal form for a feature '
            'without the normal form.')

    if len(categories) != len(normalized):
        raise TypeError('Feature is not allowed to have MISSING')

    return FeatureGenerator.categorical(  # type: ignore
        name=feature.name, categories=categories, allow_missing=True)(MISSING)


def change_set_to_missing(
        features: FeatureSet, suppress_error: bool = True) -> FeatureSet:
    def try_to_change(feature: Feature) -> Feature:
        try:
            return change_to_missing(feature)
        except (TypeError, ValueError):
            if suppress_error:
                return feature
            raise

    return FeatureSet(try_to_change(f) for f in features)
