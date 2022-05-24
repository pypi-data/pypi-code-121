from __future__ import annotations

from typing import Any, Dict
import pickle as pkl

try:
    import sklearn
except ModuleNotFoundError:
    pass  # error message in typing.py

import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


async def create_model(scalar: st.Scalar) -> sklearn.svm.SVC:
    model_spec = scalar.protobuf().spec.model

    args = pkl.loads(model_spec.arguments)
    kwargs = pkl.loads(model_spec.named_arguments)

    model_mapping: Dict[sp.Scalar.Model.ModelClass.V, Any] = {
        sp.Scalar.Model.ModelClass.SK_SVC: sklearn.svm.SVC,
    }
    ModelClass = model_mapping[model_spec.model_class]

    return ModelClass(*args, **kwargs)
