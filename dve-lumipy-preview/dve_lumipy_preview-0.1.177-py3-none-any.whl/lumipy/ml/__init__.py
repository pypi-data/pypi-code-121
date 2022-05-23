from importlib.util import find_spec


if find_spec('onnx') is None:
    raise ImportError(
        "\nThe lumipy.ml module requires extra dependencies which were not found: onnxruntime and skl2onnx."
        + "\nThey can be installed individually or by running the following pip command"
        + "\n\tpip install dve-lumipy-preview[onnx]"
    )
else:
    from lumipy.ml.onnx.sklearn_to_onnx import sklearn_to_onnx

