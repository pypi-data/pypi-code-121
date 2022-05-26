# -*- coding:utf-8 -*-
from __future__ import absolute_import

import random


def iter_list_with_size(src_list: list, size: int):
    """
        src_list would be modified when running
    """
    n_part = len(src_list) // size + 1
    while n_part >= 0:
        n_part -= 1
        part_src_list = src_list[:size]
        if part_src_list:
            yield part_src_list
            del src_list[:size]
        else:
            break


def random_choice(src_list, k: int = 1, unique: bool = True):
    if unique is False:
        return random.choices(src_list, k=k)

    assert k <= len(src_list)
    tmp_list = list(src_list)
    random.seed()  # todo: random.seed(0) is wrong here!
    random.shuffle(tmp_list)
    random.shuffle(tmp_list)
    return tmp_list[:k]


__all__ = ("iter_list_with_size", "random_choice")
