# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nnoir_onnx', 'nnoir_onnx.operators']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4,<5',
 'msgpack>=1,<2',
 'nnoir>=1.0.9,<2.0.0',
 'numpy>=1,<2',
 'onnx<1.12.0',
 'onnxruntime>=1.2.0,<2.0.0',
 'protobuf>=3.8,<4.0']

entry_points = \
{'console_scripts': ['freeze_onnx = nnoir_onnx.freeze:freeze',
                     'onnx2nnoir = nnoir_onnx.onnx2nnoir:main']}

setup_kwargs = {
    'name': 'nnoir-onnx',
    'version': '1.0.15',
    'description': 'ONNX to NNOIR Converter',
    'long_description': '# nnoir-onnx\n\nnnoir-onnx is a converter from ONNX model to NNOIR model.\n\n## Install\n\n```\npip install nnoir-onnx\n```\n\n## Example\n\n~~~~bash\nwget https://www.cntk.ai/OnnxModels/mnist/opset_7/mnist.tar.gz\ntar xvzf mnist.tar.gz\nonnx2nnoir -o model.nnoir mnist/model.onnx\n~~~~\n\n## Supported ONNX Operators\n\n* [Add](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Add)\n* [AveragePool](https://github.com/onnx/onnx/blob/master/docs/Operators.md#AveragePool)\n* [BatchNormalization](https://github.com/onnx/onnx/blob/master/docs/Operators.md#BatchNormalization)\n    * `scale`, `B`, `mean`, and `var` must be `"constant"`\n* [Clip](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Clip)\n    * must be opset version 6 or 11\n    * if opset version is 11\n      * `max` must be `"constant"`\n    * `min` must be 0\n* [Concat](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Concat)\n* [Conv](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Conv)\n    * `W` must be [Constant](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Constant) value or have initializer value\n    * `b` must be [Constant](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Constant) value or have initializer value\n* [Cos](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Cos)\n* [Div](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Div)\n    * 1st input must not be `"constant"`\n* [Dropout](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Dropout)\n    * equivalent identity function\n* [Elu](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Elu)\n* [Exp](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Exp)\n* [Flatten](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Flatten)\n* [Gemm](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Gemm)\n    * `B` must be [Constant](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Constant) value or have initializer value\n    * `C` must be [Constant](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Constant) value or have initializer value\n* [GlobalAveragePool](https://github.com/onnx/onnx/blob/master/docs/Operators.md#GlobalAveragePool)\n* [LeakyRelu](https://github.com/onnx/onnx/blob/master/docs/Operators.md#LeakyRelu)\n* [LRN](https://github.com/onnx/onnx/blob/master/docs/Operators.md#LRN)\n* [LSTM](https://github.com/onnx/onnx/blob/master/docs/Operators.md#lstm)\n    * only `seq_length == 1`\n    * `direction` must be forward\n    * Supported `activations` are below\n        * `Sigmoid`\n        * `Tanh`\n        * `Relu`\n    * Not support `clip` and `input_forget`\n* [MatMul](https://github.com/onnx/onnx/blob/master/docs/Operators.md#MatMul)\n* [MaxPool](https://github.com/onnx/onnx/blob/master/docs/Operators.md#MaxPool)\n    * `ceil_mode = 1` is not supported\n    * `dilations` is not supported\n* [Mul](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Mul)\n* [Pad](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Pad)\n    * `mode` must be `"constant"`\n* [PRelu](https://github.com/onnx/onnx/blob/master/docs/Operators.md#PRelu)\n    * `slope` must be `"constant"` and a single value tensor\n* [ReduceMean](https://github.com/onnx/onnx/blob/master/docs/Operators.md#reducemean)\n* [ReduceSum](https://github.com/onnx/onnx/blob/master/docs/Operators.md#reducesum)\n* [Relu](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Relu)\n* [Reshape](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Reshape)\n* [Resize](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Resize)\n    * must be from opset version >= 11\n    * `mode` must be `"linear"` or `"nearest"`\n    * `nearest_mode` must be `"floor"`\n    * `coordinate_transformation_mode` must be either `"pytorch_half_pixel"` or `"align_corners"` for `"linear"` mode\n    * `coordinate_transformation_mode` must be either `"asymmetric"` for `"nearest"` mode\n* [Sigmoid](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Sigmoid)\n* [Sin](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Sin)\n* [Softmax](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Softmax)\n* [Split](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Split)\n    * must be from opset version >= 13\n    * Second optional parameter `split` is not supported\n* [Squeeze](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Squeeze)\n* [Sub](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Sub)\n    * 1st input must not be `"constant"`\n* [Sum](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Sum)\n    * 2 inputs\n* [Tan](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Tan)\n* [Tanh](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Tanh)\n* [Transpose](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Transpose)\n* [Unsqueeze](https://github.com/onnx/onnx/blob/master/docs/Operators.md#Unsqueeze)\n',
    'author': 'Idein Inc.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Idein/nnoir/tree/master/nnoir-onnx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
