from skl2onnx import convert_sklearn
from onnx.onnx_ml_pb2 import ModelProto
from skl2onnx.common.data_types import FloatTensorType, StringTensorType, Int64TensorType
from lumipy.ml.onnx.common import add_metadata_to_onnx
import numpy as np
import pandas as pd


def _build_input_schema(data):

    def _make_input_tensor(exemplar, d):
        if isinstance(exemplar, int):
            return Int64TensorType([None, d])
        elif isinstance(exemplar, float) or isinstance(exemplar, np.float32):
            return FloatTensorType([None, d])
        else:
            return StringTensorType([None, d])

    if isinstance(data, pd.DataFrame) and len(set(data.dtypes)) == 1:
        # Homogeneous type pandas dataframe
        tensor = _make_input_tensor(data.iloc[0][0], data.shape[1])
        return [('input_tensor', tensor)]

    elif isinstance(data, pd.DataFrame):
        # Heterogeneous type pandas dataframe
        tensors = []
        for c in data.columns:
            tensor = _make_input_tensor(data[c].iloc[0], 1)
            name = "".join([ch if ch.isalnum() else "_" for ch in c])
            tensors.append((name, tensor))
        return tensors

    elif isinstance(data, np.ndarray) and data.dtype == object:
        # Heterogeneous type numpy array
        tensors = []
        for i in range(data.shape[1]):
            tensor = _make_input_tensor(data[0, i], 1)
            tensors.append((f'Feature_{i}', tensor))
        return tensors

    elif isinstance(data, np.ndarray):
        # Homogeneous type numpy ndarray
        tensor = _make_input_tensor(data[0, 0], data.shape[1])
        return [('input_tensor', tensor)]
    else:
        raise TypeError(
            f"Unsupported data type: {type(data).__name__}. Input tensor schema build is only supported for "
            f"pandas dataframes or numpy ndarrays."
        )


def sklearn_to_onnx(model, data) -> ModelProto:
    """Convert an sklearn transformer, estimator or pipeline to ONNX graph (ModelProto).

    Args:
        model (Union[BaseEstimator, TransformerMixin]): sklearn estimator, transformer or pipeline to convert.
        data (Union[DataFrame, ndarray]): data that the model was trained on - used to determine the input tensor
        schema.

    Returns:
        ModelProto: the resulting ONNX graph object.
    """
    schema = _build_input_schema(data)

    # Set option to return class probs as tensor not as dict (if it's a classifier).
    if hasattr(model, 'predict_proba'):
        options = {id(model): {'zipmap': False}}
    else:
        options = {id(model): {}}

    try:
        model_onnx = convert_sklearn(model, initial_types=schema, options=options)
    except RuntimeError as re:
        msg = str(re)
        if not msg.startswith('Isolated variables exist'):
            raise re
        schema = [(name, tensor) for name, tensor in schema if name not in msg]
        model_onnx = convert_sklearn(model, initial_types=schema, options=options)

    order_meta = {f"{name}_index": str(i) for i, (name, _) in enumerate(schema)}
    model_onnx = add_metadata_to_onnx(model_onnx, **order_meta)

    return model_onnx
