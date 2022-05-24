from __future__ import annotations

from typing import Any, cast

try:
    import sklearn
except ModuleNotFoundError:
    pass  # error message in typing.py

import sarus_data_spec.typing as st

from .utils import one_parent_ops, pandas_or_value


async def sk_fit(
    scalar: st.Scalar, *args: Any, **kwargs: Any
) -> sklearn.svm.SVC:
    (ds_model, X, y), _ = scalar.parents()
    model = await cast(st.Scalar, ds_model).async_value()
    assert isinstance(model, sklearn.svm.SVC)
    X = await pandas_or_value(X)
    y = await pandas_or_value(y)
    fitted_model = model.fit(X, y, *args, **kwargs)
    return fitted_model


@one_parent_ops
async def sk_scale(val: Any, *args: Any, **kwargs: Any) -> Any:
    return sklearn.preprocessing.scale(val, *args, **kwargs)
