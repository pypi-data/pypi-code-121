from onnx import ModelProto


def add_metadata_to_onnx(model_onnx: ModelProto, **kwargs: str) -> ModelProto:
    """Add custom metadata to an ONNX graph object (ModelProto).

    Args:
        model_onnx (ModelProto): the ONNX graph (ModelProto) to add custom metadata to.
        **kwargs (str): the metadata string values to add.

    Returns:
        ModelProto: the ONNX graph with the custom metadata added to it.
    """
    for k, v in kwargs.items():
        meta = model_onnx.metadata_props.add()
        meta.key = k
        meta.value = v

    return model_onnx
