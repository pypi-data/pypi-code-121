import random
from typing import List,Union,TypeVar,Tuple

import numpy as np

T = TypeVar("T")


def get_list_subset(target: List[T], index_list: List[int]) -> List[T]:
    """
    Get the subset of the target list
    Args:
        target: target list
        index_list: subset items index

    Returns:
        subset of the original list
    """
    return [target[i] for i in index_list if i < len(target)]


def unison_shuffled_copies(a: List[T],
                           b: List[T]) -> Union[Tuple[List[T], ...], Tuple[np.ndarray, ...]]:
    """
    Union shuffle two arrays
    Args:
        a:
        b:

    Returns:

    """
    data_type = type(a)
    assert len(a) == len(b)
    c = list(zip(a, b))
    random.shuffle(c)
    a, b = zip(*c)
    if data_type == np.ndarray:
        return np.array(a), np.array(b)
    return list(a), list(b)


def load_vocab(dict_path, encoding='utf-8', startswith=None):
    """词典文件中读取词典
    """
    token_list = []
    with open(dict_path, encoding=encoding) as reader:
        for line in reader:
            token = line.strip()
            if token:
                token_list.append(token)
    if startswith:
        token_list = startswith + list(set(token_list))
    token_dict = {key:index for index,key in enumerate(token_list)}

    return token_dict