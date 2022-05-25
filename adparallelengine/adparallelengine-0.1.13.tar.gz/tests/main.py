import sys
from typing import Union
import pandas as pd
import numpy as np
from transparentpath import Path

from adparallelengine import Engine


class Dummy:
    some_attr = 0


def method_in_processes(a):
    Dummy.some_attr = a


def method(
    element: pd.DataFrame,
    some_other_stuff: Union[float, pd.DataFrame, pd.Series, np.ndarray],
    some_float: float,
):
    assert Dummy.some_attr == 1
    # print("")
    # print("Element\n", element)
    print("Other stuff\n", type(some_other_stuff), some_other_stuff)
    # print("Float\n", some_float)
    # print("Dummy attr\n", Dummy.some_attr)
    to_ret = (
        element * some_other_stuff + some_float + Dummy.some_attr,
        3 * (element * some_other_stuff + some_float + Dummy.some_attr),
    )
    # print("Result 1\n", to_ret[0])
    # print("Result 2\n", to_ret[1])
    return to_ret


if __name__ == "__main__":

    Dummy.some_attr = 1

    dfs = [
        pd.DataFrame([[0, 1], [2, 3]]),
        pd.DataFrame([[4, 5], [6, 7]]),
        pd.DataFrame([[8, 9], [10, 11]]),
        pd.DataFrame([[12, 13], [14, 15]]),
        pd.DataFrame([[16, 17], [18, 19]]),
        pd.DataFrame([[21, 22], [23, 24]]),
    ]
    s = pd.Series([2, 3])
    f = 5.0

    which = sys.argv[1]
    gather = True if sys.argv[2] == "True" else False
    batched = True if sys.argv[3] == "True" else False if sys.argv[3] == "False" else int(sys.argv[3])
    share = True if sys.argv[4] == "True" else False

    if share is True:
        share_kwargs = {"share": {"some_other_stuff": s}}
    else:
        share_kwargs = {"some_other_stuff": s}
    engine = Engine(kind=which, path_shared=Path("tests") / "data" / "shared")
    res = engine(
        method,
        dfs,
        init_method={"method": method_in_processes, "kwargs": {"a": 1}},
        some_float=f,
        gather=gather,
        batched=batched,
        **share_kwargs
    )

    if share is True and which != "serial":
        assert len(list(engine.path_shared.ls())) == 1
    else:
        if engine.path_shared.isdir():
            assert len(list(engine.path_shared.ls())) == 0
    engine.clean_shared()
    assert len(list(engine.path_shared.ls())) == 0

    # print("Results:", res)

    if gather is True:
        # print("gather")
        assert len(res) == 2 * len(dfs)
        for i in range(0, len(dfs), 2):
            # print(i)
            expected = dfs[int(i / 2)] * s + f + Dummy.some_attr
            # print("Expected\n", expected)
            pd.testing.assert_frame_equal(expected, res[i])
            pd.testing.assert_frame_equal(3 * expected, res[i + 1])

    else:
        # print("Don't gather")
        assert len(res) == len(dfs)
        for i in range(len(dfs)):
            # print(i)
            expected = dfs[i] * s + f + Dummy.some_attr
            # print("Expected\n", expected)
            pd.testing.assert_frame_equal(expected, res[i][0])
            pd.testing.assert_frame_equal(3 * expected, res[i][1])
