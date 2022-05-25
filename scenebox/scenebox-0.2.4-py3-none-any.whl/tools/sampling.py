"""Miscellaneous (catch all) tools Copyright 2020 Caliber Data Labs."""

#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
import random
from typing import List, Union, Tuple


def random_sample(items_list: List[str],
                  sample_size: int,
                  return_sample_and_index: bool = False,
                  ) -> Union[List[str], Tuple[List[str], List[str]]]:
    if not return_sample_and_index:
        sampled_items = random.sample(items_list, sample_size)
    else:
        sampled_items = random.sample(list(enumerate(items_list)), sample_size)
    return sampled_items
