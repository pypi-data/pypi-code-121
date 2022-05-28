# -*- coding: utf-8 -*-
# type: ignore
'''
ReilData class
==============

The main datatype used to communicate `state`s, `action`s, and `reward`s,
between objects in `reil`. `ReilData` is basically a tuple that contains
instances of `BaseData`, `CategoricalData`, and `NumericalData`.
'''
from __future__ import annotations

import dataclasses
import itertools
from dataclasses import field
from typing import (Any, Callable, Dict, Generic, Iterable, Iterator, List,
                    Literal, Mapping, Optional, Sequence, Tuple, TypeVar,
                    Union, cast, overload)

T = TypeVar('T')

Categorical = TypeVar('Categorical')
Numerical = TypeVar('Numerical', int, float)

Normal = Union[Literal[0], Literal[1], float]
Normalized = Union[Normal, Sequence[Normal], None]
Normalizer = Callable[..., Normalized]


@dataclasses.dataclass(frozen=True)
class BaseData(Generic[T]):
    '''
    The base class for `ReilData` elements.

    Attributes
    ----------
    name:
        Name of the data.

    value:
        Value of the data. Can be one item or a sequence.

    normalizer:
        A function that gets a `BaseData` object and returns its normalized
        form.

    lazy_evaluation:
        Whether normalization should be done at the point of instantiation
        (False) or at the access time (True).


    :meta private:
    '''
    name: str
    value: Optional[Union[T, Sequence[T]]] = None
    normalizer: Optional[Normalizer] = lambda _: None
    lazy_evaluation: Optional[bool] = field(default=None, compare=False)
    is_numerical: Optional[bool] = field(
        default=None, init=False, repr=False, compare=False)
    _normalized: Normalized = field(
        default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        # if not isinstance(self.value, Hashable):
        #     warnings.warn('Non-hashable object!')
        self._validate(self)
        if self.normalizer is None:
            object.__setattr__(self, 'normalizer',
                               self._default_normalizer)
        if not self.lazy_evaluation:
            object.__setattr__(self, '_normalized',
                               self.normalizer(self))

    @staticmethod
    def _validate(data: BaseData[T]) -> None:
        '''
        Validate the input data.

        Arguments
        ---------
        data:
            An instance to be validated.

        Raises
        ------
        ValueError:
            if `data.value` does not match the validation criteria.


        :meta public:
        '''
        pass

    @staticmethod
    def _default_normalizer(data: BaseData[T]) -> Normalized:
        '''
        Normalize the data.

        Arguments
        ---------
        data:
            An instance to be normalized.

        Returns
        -------
        :
            The normalized form of `data.value`.
        '''
        return None

    @property
    def normalized(self) -> Normalized:
        if self._normalized is None:
            object.__setattr__(self, '_normalized',
                               self.normalizer(self))

        return self._normalized

    def as_dict(self) -> Dict[str, Any]:
        '''
        Return the data as a dictionary.

        Returns
        -------
        :
            The data as a dictionary.
        '''
        return {'name': self.name, 'value': self.value}


@dataclasses.dataclass(frozen=True)
class CategoricalData(BaseData[Categorical]):
    '''
    A datatype for categorical data.

    Attributes
    ----------
    name:
        Name of the data.

    value:
        Value of the data. Can be one item or a sequence.

    normalizer:
        A function that gets a `BaseData` object and returns its normalized
        form.

    lazy_evaluation:
        Whether normalization should be done at the point of instantiation
        (False) or at the access time (True).

    categories:
        A list of all categories.
    '''
    categories: Optional[Tuple[Categorical, ...]] = None

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'is_numerical', False)

    @staticmethod
    def _default_normalizer(data: CategoricalData) -> Normalized:
        value = data.value
        categories = data.categories
        if categories is None or value is None:
            return None

        if isinstance(value, type(categories[0])):
            return tuple(int(x_i == value)
                         for x_i in categories)

        return tuple(int(x_i == v)
                     for v in value
                     for x_i in categories)

    @staticmethod
    def _validate(data: CategoricalData) -> None:
        value = data.value
        if value is not None:
            is_sequence = isinstance(value, (list, tuple))

            categories = data.categories
            if categories is not None:
                if ((not is_sequence and value not in categories) or
                        (is_sequence and any(v not in categories
                                             for v in value))):
                    raise ValueError(
                        f'value={value} is '
                        f'in the categories={categories}.')

    def as_dict(self) -> Dict[str, Any]:
        return {'name': self.name, 'value': self.value,
                'categories': self.categories,
                'is_numerical': self.is_numerical}


@dataclasses.dataclass(frozen=True)
class NumericalData(BaseData[Numerical]):
    '''
    A datatype for numerical data.

    Attributes
    ----------
    name:
        Name of the data.

    value:
        Value of the data. Can be one item or a sequence.

    normalizer:
        A function that gets a `BaseData` object and returns its normalized
        form.

    lazy_evaluation:
        Whether normalization should be done at the point of instantiation
        (False) or at the access time (True).

    lower:
        The lower bound of value.

    upper:
        The upper bound of value.
    '''
    lower: Optional[Numerical] = None
    upper: Optional[Numerical] = None

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, 'is_numerical', True)

    @staticmethod
    def _default_normalizer(data: NumericalData) -> Normalized:
        value = data.value
        lower = data.lower
        upper = data.upper
        if value is None or lower is None or upper is None:
            return None

        denominator = upper - lower

        sequence_check = isinstance(value, (list, tuple))
        try:
            if sequence_check:
                return tuple((v - lower) / denominator
                             for v in value)
            else:
                return (value - lower) / denominator
        except ZeroDivisionError:
            return [1] * len(value) if sequence_check else 1

    @staticmethod
    def _validate(data: NumericalData) -> None:
        value = data.value
        lower = data.lower
        upper = data.upper
        if value is not None:
            is_sequence = isinstance(value, (list, tuple))

            if lower is not None:
                if ((not is_sequence and value < lower) or
                        (is_sequence and any(v < lower
                                             for v in value))):
                    raise ValueError(
                        f'value={value} is less than lower={lower}.')

            if upper is not None:
                if ((not is_sequence and value > upper) or
                        (is_sequence and any(v > upper
                                             for v in value))):
                    raise ValueError(
                        f'value={value} is '
                        f'greater than upper={upper}.')

    def as_dict(self) -> Dict[str, Any]:
        return {'name': self.name, 'value': self.value,
                'lower': self.lower, 'upper': self.upper,
                'is_numerical': self.is_numerical}


ReilDataInput = Union[Mapping[str, Any],
                      BaseData[Any],
                      CategoricalData[Categorical],
                      NumericalData[Numerical]]


class ReilData(Sequence[ReilDataInput], Generic[Categorical, Numerical]):
    '''
    The main datatype used to communicate `state`s, `action`s, and `reward`s,
    between objects in `reil`.
    '''

    def __init__(self,
                 data: Union[ReilDataInput,
                             Sequence[ReilDataInput],
                             Iterator[ReilDataInput]],
                 lazy_evaluation: Optional[bool] = None):
        '''
        Arguments
        ---------
        data:
            One or a sequence of `BaseData`, `CategoricalData`,
            `NumericalData`, or dicts that include 'name'. Other attributes are
            optional. If none of `categories`, `lower` and `upper` are
            provided, the object is assumed `BaseData`.

        lazy_evaluation:
            Whether to compute normalized value at the time of instantiation or
            at the time of the first access. If not provided, `ReilData` looks
            for `lazy_evaluation` in each item. If failed, True is assumed.
        '''
        temp: List[Union[BaseData[Any],
                         CategoricalData[Categorical],
                         NumericalData[Numerical]]] = []
        _data = data if isinstance(data, (Sequence, Iterator)) else [data]
        for d in _data:
            if isinstance(d, BaseData):
                temp.append(d)
            elif isinstance(d, dict):
                name = d['name']
                value = d.get('value')
                normalizer = d.get('normalizer')
                l_e = lazy_evaluation if lazy_evaluation is not None \
                    else d.get('lazy_evaluation', True)

                if 'categories' in d:
                    temp.append(CategoricalData(
                        name=name,
                        value=value,
                        categories=d['categories'],
                        normalizer=normalizer,
                        lazy_evaluation=l_e))
                elif 'lower' in d or 'upper' in d:
                    temp.append(NumericalData(
                        name=name,
                        value=value,
                        lower=d.get('lower'),
                        upper=d.get('upper'),
                        normalizer=normalizer,
                        lazy_evaluation=l_e))
                else:
                    temp.append(BaseData(
                        name=name,
                        value=value,
                        normalizer=normalizer,
                        lazy_evaluation=l_e))
            else:
                raise TypeError(f'Unknow input type {type(d)} for item: {d}')

        self._data = tuple(temp)
        self._clear_temps()

    @classmethod
    def single_base(
            cls,
            name: str,
            value: Optional[Union[T, Sequence[T]]] = None,
            normalizer: Optional[Normalizer] = None,
            lazy_evaluation: Optional[bool] = None) -> ReilData:
        '''
        Create a `ReilData` instance.

        Arguments
        ---------
        name:
            Name of the instance.

        value:
            The value to store.

        normalizer:
            A function that accepts a `BaseData` object and returns the
            normalized value.

        lazy_evaluation:
            Whether normalization should be done at the point of instantiation
            (False) or at the access time (True).
        '''
        instance = cls([])
        instance._data = (
            BaseData(name=name,
                     value=value,
                     normalizer=normalizer,
                     lazy_evaluation=lazy_evaluation),)

        return instance

    @classmethod
    def single_categorical(
            cls,
            name: str,
            value: Optional[Union[Categorical, Sequence[Categorical]]] = None,
            normalizer: Optional[Normalizer] = None,
            lazy_evaluation: Optional[bool] = None,
            categories: Optional[Tuple[Categorical, ...]] = None) -> ReilData:
        '''
        Create a `ReilData` instance.

        Arguments
        ---------
        name:
            Name of the instance.

        value:
            The value to store.

        categories:
            A list of categories if the object is categorical

        normalizer:
            A function that accepts a `BaseData` object and returns the
            normalized value.

        lazy_evaluation:
            Whether normalization should be done at the point of instantiation
            (False) or at the access time (True).
        '''
        instance = cls([])
        instance._data = (
            CategoricalData(
                name=name,
                value=value,
                categories=categories,
                normalizer=normalizer,
                lazy_evaluation=lazy_evaluation),)

        return instance

    @classmethod
    def single_numerical(
            cls,
            name: str,
            value: Optional[Union[Numerical, Sequence[Numerical]]] = None,
            normalizer: Optional[Normalizer] = None,
            lazy_evaluation: Optional[bool] = None,
            lower: Optional[Numerical] = None,
            upper: Optional[Numerical] = None) -> ReilData:
        '''
        Create a `ReilData` instance.

        Arguments
        ---------
        name:
            Name of the instance.

        value:
            The value to store.

        lower:
            The lower bound of value if data is numerical

        upper:
            The upper bound of the value is numerical

        normalizer:
            A function that accepts a `BaseData` object and returns the
            normalized value.

        lazy_evaluation:
            Whether normalization should be done at the point of instantiation
            (False) or at the access time (True).
        '''
        instance = cls([])
        instance._data = (
            NumericalData(
                name=name,
                value=value,
                lower=lower,
                upper=upper,
                normalizer=normalizer,
                lazy_evaluation=lazy_evaluation),)

        return instance

    @classmethod
    def single_item(
            cls,
            name: str,
            value: Optional[Union[
                Numerical, Sequence[Numerical],
                Categorical, Sequence[Categorical]]] = None,
            normalizer: Optional[Normalizer] = None,
            lazy_evaluation: Optional[bool] = None,
            categories: Optional[Tuple[Categorical, ...]] = None,
            lower: Optional[Numerical] = None,
            upper: Optional[Numerical] = None) -> ReilData:
        '''
        Create a `ReilData` instance.

        Arguments
        ---------
        name:
            Name of the instance.

        value:
            The value to store.

        categories:
            A list of categories if the object is categorical

        lower:
            The lower bound of value if data is numerical

        upper:
            The upper bound of the value is numerical

        normalizer:
            A function that accepts a `BaseData` object and returns the
            normalized value.

        lazy_evaluation:
            Whether normalization should be done at the point of instantiation
            (False) or at the access time (True).
        '''
        instance = cls([])
        if lower is not None or upper is not None:
            instance._data = (
                NumericalData(
                    name=name,
                    value=value,  # type: ignore
                    lower=lower,
                    upper=upper,
                    normalizer=normalizer,
                    lazy_evaluation=lazy_evaluation),)
        elif categories is not None:
            instance._data = (
                CategoricalData(
                    name=name,
                    value=value,
                    categories=categories,
                    normalizer=normalizer,
                    lazy_evaluation=lazy_evaluation),)
        else:
            instance._data = (
                CategoricalData(
                    name=name,
                    value=value,
                    categories=categories,
                    normalizer=normalizer,
                    lazy_evaluation=lazy_evaluation),)

        return instance

    def _clear_temps(self):
        self._value: Optional[Dict[str, Any]] = None
        self._lower: Optional[Dict[str, Numerical]] = None
        self._upper: Optional[Dict[str, Numerical]] = None
        self._categories: Optional[Dict[str, Tuple[Categorical, ...]]] = None
        self._is_numerical: Optional[Dict[str, bool]] = None

    def index(self, value: Any,
              start: int = 0, stop: Optional[int] = None) -> int:
        _stop = stop if stop is not None else len(self._data)
        if isinstance(value, BaseData):
            for i in range(start, _stop):
                if self._data[i] == value:
                    return i

            raise ValueError(f'{value} is not on the list.')

        elif isinstance(value, type(self._data[0].name)):
            for i in range(start, _stop):
                if self._data[i].name == value:
                    return i

            raise ValueError(f'{value} is not on the list.')

        else:
            raise ValueError(f'{value} is not on the list.')

    @property
    def value(self) -> Dict[str, Any]:
        '''
        Return a dictionary with elements' names as keys and
        their respective values as values.

        Returns
        -------
        :
            Names of the elements and their values.
        '''
        if self._value is None:
            self._value = {v.name: v.value
                           for v in self._data}

        return self._value

    @property
    def lower(self) -> Dict[str, Numerical]:
        '''
        Return all `lower` attributes.

        Returns
        -------
        :
            `lower` attribute of all `NumericalData` variables with their names
            as keys.
        '''
        if self._lower is None:
            self._lower = {v.name: cast(Numerical, v.lower)  # type: ignore
                           for v in self._data
                           if hasattr(v, 'lower')}

        return self._lower

    @property
    def upper(self) -> Dict[str, Numerical]:
        '''
        Return all `upper` attributes.

        Returns
        -------
        :
            `upper` attribute of all `NumericalData` variables with their names
            as keys.
        '''
        if self._upper is None:
            self._upper = {v.name: cast(Numerical, v.upper)  # type: ignore
                           for v in self._data
                           if hasattr(v, 'upper')}

        return self._upper

    @property
    def categories(self) -> Dict[str, Tuple[Categorical, ...]]:
        '''
        Return all `categories` attributes.

        Returns
        -------
        :
            `categories` attribute of all `CategoricalData` variables with
            their names as keys.
        '''
        if self._categories is None:
            self._categories = {v.name:
                                cast(Tuple[Categorical, ...],
                                     v.categories)  # type: ignore
                                for v in self._data
                                if hasattr(v, 'categories')}

        return self._categories

    @property
    def normalized(self) -> ReilData:
        '''
        Normalize all items in the instance.

        Returns
        -------
        :
            A `ReilData` consist of normalized values of all the items in the
            instance, in the form of `NumericalData` objects.
        '''
        return ReilData(
            NumericalData(name=v.name, value=v.normalized,
                          lower=0, upper=1, lazy_evaluation=True)
            for v in self._data)

    def flatten(self) -> List[BaseData]:
        """Combine values of all items in the instance.

        Returns
        -------
        :
            A list that contains all the values of all the items.
        """
        def make_iterable(x: T) -> Iterable[T]:
            return x if isinstance(x, Iterable) else [x]

        return list(itertools.chain(*[make_iterable(sublist)
                                      for sublist in self.value.values()]))

    def split(self) -> Union[ReilData, List[ReilData]]:
        """Split the `ReilData` into a list of `ReilData`.

        Returns
        -------
        :
            All items in the instance as separate `ReilData` instances.
        """
        if len(self) == 1:
            d = self._data[0]
            if not isinstance(d.value, (list, tuple)):
                splitted_list = ReilData(self._data)
            else:
                temp = d.as_dict()
                cls = type(d)
                value = temp['value']
                del temp['value']
                if 'is_numerical' in temp:
                    del temp['is_numerical']

                splitted_list = [
                    ReilData(cls(
                        value=v,
                        **temp))
                    for v in value]

        else:
            splitted_list = cast(List[ReilData], list(self._data))

        return splitted_list

    @overload
    def __getitem__(self, i: int) -> BaseData:
        ...

    @overload
    def __getitem__(self, s: slice) -> Tuple[BaseData, ...]:
        ...

    def __getitem__(self, x):
        return self._data.__getitem__(x)

    def __len__(self) -> int:
        return self._data.__len__()

    def __hash__(self) -> int:
        return hash(tuple(self._data))

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and (self._data == other._data)

    def __add__(self, other: Union[BaseData[T], ReilData]) -> ReilData:
        if isinstance(other, BaseData):
            if other.name in self._data:
                raise ValueError(
                    'Cannot have items with same names.'
                    ' Use update() if you need to update an item.')
            new_data = [other]
        elif isinstance(other, ReilData):
            for k in other:
                if k in self._data:
                    raise ValueError(
                        'Cannot have items with same names.'
                        ' Use update() if you need to update an item.')
            new_data = other._data
        else:
            raise TypeError(
                'Concatenation of type ReilData'
                f' and {type(other)} not implemented!')

        return ReilData(itertools.chain(self._data, new_data))

    def __neg__(self) -> ReilData:
        temp = [v.as_dict()
                for v in self._data]
        for item in temp:
            item['value'] = -item['value']

        return ReilData(temp)

    def __repr__(self) -> str:
        return f'[{super().__repr__()} -> {self._data}]'

    def __str__(self) -> str:
        return f"[{', '.join((d.__str__() for d in self._data))}]"


if __name__ == "__main__":
    # from timeit import timeit

    def f1():
        t1 = ReilData.single_categorical(name='test A', value=['a', 'b'],
                                         categories=('a', 'b'))
        t1 = ReilData.single_numerical(name='test A', value=[1, 2])
        t1 = ReilData.single_base(name='test A', value=['a', 'b'])
        return t1

    def f2():
        t2 = ReilData(({'name': x, 'value': x,
                        'categories': list('abcdefghijklmnopqrstuvwxyz')}
                       for x in 'abcdefghijklmnopqrstuvwxyz'),
                      lazy_evaluation=True)
        return t2.normalized.flatten()

    def f3():
        t2 = ReilData([{'name': 'A', 'value': 'a', 'categories': ['a', 'b']},
                       {'name': 'B', 'value': [10, 20],
                        'lower': 0, 'upper': 100}], lazy_evaluation=True)
        return t2

    # t1 = f1()
    # t2 = ReilData(t1)
    print(f1() + f3())
    # test = f1().split()
    # print(test)
    # print(timeit(f1, number=1000))
    # print(timeit(f2, number=100))
    # print(timeit(f3, number=1000))
    # print(f2().normalized.as_list())
    # print(a.values)
    # print(a.lower)
    # print(a.categories)
    # a.values = {'test A':'b'}
