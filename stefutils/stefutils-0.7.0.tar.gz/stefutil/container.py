"""
container operations, including functional, deep dictionary syntactic sugar
"""

import itertools
from typing import Tuple, List, Dict, Iterable, Callable, TypeVar, Any, Union
from functools import reduce
from collections import OrderedDict

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import torch


__all__ = [
    'get', 'set_', 'it_keys',
    'list_is_same_elms', 'chain_its', 'join_it', 'group_n', 'list_split', 'lst2uniq_ids', 'compress',
    'np_index', 'df_col2cat_col', 'pt_sample'
]


T = TypeVar('T')
K = TypeVar('K')


def get(dic: Dict, ks: str):
    """
    :param dic: Potentially multi-level dictionary
    :param ks: Potentially `.`-separated keys
    """
    ks = ks.split('.')
    return reduce(lambda acc, elm: acc[elm], ks, dic)


def set_(dic, ks, val):
    ks = ks.split('.')
    node = reduce(lambda acc, elm: acc[elm], ks[:-1], dic)
    node[ks[-1]] = val


def it_keys(dic, prefix=''):
    """
    :return: Generator for all potentially-nested keys
    """
    def _full(k_):
        return k_ if prefix == '' else f'{prefix}.{k_}'
    for k, v in dic.items():
        if isinstance(v, dict):
            for k__ in it_keys(v, prefix=_full(k)):
                yield k__
        else:
            yield _full(k)


def list_is_same_elms(lst: List[T]) -> bool:
    return all(l == lst[0] for l in lst)


def chain_its(its: Iterable[Iterable[T]]) -> Iterable[T]:
    """
    Chain multiple iterables
    """
    out = itertools.chain()
    for it in its:
        out = itertools.chain(out, it)
    return out


def join_it(it: Iterable[T], sep: T) -> Iterable[T]:
    """
    Generic join elements with separator element, like `str.join`
    """
    it = iter(it)

    curr = next(it, None)
    if curr is not None:
        yield curr
        curr = next(it, None)
    while curr is not None:
        yield sep
        yield curr
        curr = next(it, None)


def group_n(it: Iterable[T], n: int) -> Iterable[Tuple[T]]:
    """
    Slice iterable into groups of size n (last group included) by iteration order
    """
    # Credit: https://stackoverflow.com/a/8991553/10732321
    it = iter(it)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def list_split(lst: List[T], call: Callable[[T], bool]) -> List[List[T]]:
    """
    :return: Split a list by locations of elements satisfying a condition
    """
    return [list(g) for k, g in itertools.groupby(lst, call) if k]


def lst2uniq_ids(lst: List[T]) -> List[int]:
    """
    Each unique element in list assigned a unique id, in increasing order of iteration
    """
    elm2id = {v: k for k, v in enumerate(OrderedDict.fromkeys(lst))}
    return [elm2id[e] for e in lst]


def compress(lst: List[T]) -> List[Tuple[T, int]]:
    """
    :return: A compressed version of `lst`, as 2-tuple containing the occurrence counts
    """
    if not lst:
        return []
    return ([(lst[0], len(list(itertools.takewhile(lambda elm: elm == lst[0], lst))))]
            + compress(list(itertools.dropwhile(lambda elm: elm == lst[0], lst))))


def np_index(arr, idx):
    return np.where(arr == idx)[0][0]


def df_col2cat_col(df: pd.DataFrame, col_name: str, categories: List[str]) -> pd.DataFrame:
    """
    Enforced ordered categories to a column, the dataframe is modified in-place
    """
    cat = CategoricalDtype(categories=categories, ordered=True)  # Enforce order by definition
    df[col_name] = df[col_name].astype(cat, copy=False)
    return df


def pt_sample(d: Dict[K, Union[float, Any]]) -> K:
    """
    Sample a key from a dict based on confidence score as value
        Keys with confidence evaluated to false are ignored

    Internally uses `torch.multinomial`
    """
    d_keys = {k: v for k, v in d.items() if v}  # filter out `None`s
    keys, weights = zip(*d_keys.items())
    return keys[torch.multinomial(torch.tensor(weights), 1, replacement=True).item()]
