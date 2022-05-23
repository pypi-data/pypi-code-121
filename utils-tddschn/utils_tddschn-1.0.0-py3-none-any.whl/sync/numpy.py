#!/usr/bin/env python3


def numpy_arange_element_count(start: float, stop: float, step: float) -> int:
    """
    get the number of elements in np.arange(start, stop, step)
    example
    In [41]: get_num_elements(0, 0.23, 0.004)
    Out[41]: 58

    In [42]: get_num_elements(1, 2, 1)
    Out[42]: 1

    In [43]: get_num_elements(1, 2, 0.01)
    Out[43]: 100

    In [32]: len(np.arange(0, 0.23, 0.004))
    Out[32]: 58

    In [33]: len(np.arange(1, 2, 1))
    Out[33]: 1

    In [36]: len(np.arange(1, 2, 0.01))
    Out[36]: 100
    """
    mod = (stop - start) / step
    return int(mod) + int(mod != int(mod))
