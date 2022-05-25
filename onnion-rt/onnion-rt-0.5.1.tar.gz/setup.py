# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['onnion_runtime']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.8"': ['numpy>=1.19.0,<1.21.5'],
 ':python_version >= "3.8"': ['numpy>=1.19.0,<2.0.0']}

setup_kwargs = {
    'name': 'onnion-rt',
    'version': '0.5.1',
    'description': 'run onnx with only numpy',
    'long_description': '# onnion-rt\n\nNote: This software includes [the work](https://github.com/onnx/onnx) that is distributed in the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.html).\n\n## Installation\n\n```\n$ pip3 install onnion-rt\n```\n\n## Usage\nSee [tutorial](https://github.com/Idein/onnion/tree/master#tutorial).\n\n## Development Guide\n\n```\n$ poetry install\n```\n\n### How to support new operators\n\n1. Add `onnion_runtime/xxx.py`\n  - An onnx operator `Xxx` must correspond to a class `Xxx`.\n  - A class `Xxx` must implement `__init__` and `run` methods.\n  - The parameters of the `__init__` methods must be `self`, `opset_version`, and `kwargs`.\n  - The attributes of the operator must be passed through the `kwargs` of the `__init__` method.\n    - Get the required attributes by `kwargs[\'attr_name\']`.\n    - Get the optional attributes by `kwargs.get(\'attr_name\', default_value)`.\n  - The inputs of the operator must be passed through the arguments of the `run` method.\n  - The `run` method must return the list of `np.array`.\n2. Add `from .xxx import Xxx # noqa: F401` to `onnion_runtime/__init__.py`\n3. Update "Supported Operators" in `README.md`\n4. Add `tests/test_xxx.py`\n5. Run tests `poetry run pytest -v`\n6. Format and lint `poetry run pysen run format && poetry run pysen run lint`\n\n## Supported Operators\nThis runtime supports only below operators.\n\n- Abs\n- Acos\n- Acosh\n- Add\n  - must be from opsetversion >= 7\n- And\n  - must be from opsetversion >= 7\n- ArgMax\n- ArgMin\n- Asin\n- Asinh\n- Atan\n- Atanh\n- BitShift\n- Cast\n  - must be from opsetversion >= 6\n- Ceil\n- Celu\n- Clip\n- Compress\n- Concat\n- ConcatFromSequence\n- Constant\n- ConstantOfShape\n- Cos\n- Cosh\n- DepthToSpace\n- DequantizeLinear\n- Det\n- Div\n  - must be from opsetversion >= 7\n- Dropout\n- DynamicQuantizeLinear\n- Einsum\n- Elu\n- Equal\n  - must be from opsetversion >= 7\n- Erf\n- Exp\n- Expand\n- EyeLike\n- Flatten\n- Floor\n- Gather\n- GatherElements\n- GahterND\n- Gemm\n  - must be from opsetversion >= 7\n- GlobalAveragePool\n- GlobalMaxPool\n- Greater\n  - must be from opsetversion >= 7\n- GreaterOrEqual\n- HardSigmoid\n- HardSwish\n- Hardmax\n- Identity\n- If\n- InstanceNormalization\n- IsInf\n- IsNaN\n- LeakyRelu\n- Less\n  - must be from opsetversion >= 7\n- LessOrEqual\n- Log\n- LogSoftmax\n- Loop\n- MatMul\n- MatMulInteger\n- Max\n- Mean\n- Min\n- Mod\n- Mul\n  - must be from opsetversion >= 7\n- Neg\n- NegativeLogLikelihoodLoss\n- NonMaxSuppression\n- NonZero\n- Not\n- OneHot\n- Or\n  - must be from opsetversion >= 7\n- PRelu\n- Pad\n- Pow\n  - must be from opsetversion >= 7\n- RandomNormal\n- RandomNormalLike\n- RandomUniform\n- RandomUniformLike\n- Range\n- Reciprocal\n- ReduceL1\n- ReduceL2\n- ReduceLogSum\n- ReduceLogSumExp\n- ReduceMax\n- ReduceMean\n- ReduceMin\n- ReduceProd\n- ReduceSum\n- ReduceSumSquare\n- Relu\n- Reshape\n- Round\n- ScatterND\n- Shape\n- Sigmoid\n- Slice\n- Squeeze\n- Sub\n  - must be from opsetversion >= 7\n- Tile\n  - must be from opsetversion >= 6\n- TopK\n- Transpose\n- Unsqueeze\n- Where\n',
    'author': 'Idein Inc.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Idein/onnion/tree/master/runtime',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
