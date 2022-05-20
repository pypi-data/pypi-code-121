# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src/py'}

packages = \
['flwr',
 'flwr.client',
 'flwr.client.grpc_client',
 'flwr.common',
 'flwr.dataset',
 'flwr.dataset.generator',
 'flwr.dataset.utils',
 'flwr.proto',
 'flwr.server',
 'flwr.server.grpc_server',
 'flwr.server.strategy',
 'flwr.server.utils',
 'flwr.simulation',
 'flwr.simulation.ray_transport']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.41.0,<2.0.0', 'iterators>=0.0.2,<0.0.3', 'protobuf>=3.19.0,<4.0.0']

extras_require = \
{':python_version < "3.10"': ['numpy>=1.19.0,<1.21.0'],
 ':python_version < "3.8"': ['importlib-metadata>=4.0.0,<5.0.0'],
 ':python_version >= "3.10" and python_version < "4.0"': ['numpy>=1.21,<2.0'],
 'simulation': ['ray[default]>=1.9.2,<1.12.0']}

setup_kwargs = {
    'name': 'flwr-nightly',
    'version': '1.0.0.dev20220520',
    'description': 'Flower - A Friendly Federated Learning Framework',
    'long_description': '# Flower - A Friendly Federated Learning Framework\n\n<p align="center">\n  <a href="https://flower.dev/">\n    <img src="https://flower.dev/_next/image/?url=%2F_next%2Fstatic%2Fmedia%2Fflower_white_border.c2012e70.png&w=640&q=75" width="140px" alt="Flower Website" />\n  </a>\n</p>\n<p align="center">\n    <a href="https://flower.dev/">Website</a> |\n    <a href="https://flower.dev/blog">Blog</a> |\n    <a href="https://flower.dev/docs/">Docs</a> |\n    <a href="https://flower.dev/conf/flower-summit-2021">Conference</a> |\n    <a href="https://flower.dev/join-slack">Slack</a>\n    <br /><br />\n</p>\n\n[![GitHub license](https://img.shields.io/github/license/adap/flower)](https://github.com/adap/flower/blob/main/LICENSE)\n[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/adap/flower/blob/main/CONTRIBUTING.md)\n![Build](https://github.com/adap/flower/workflows/Build/badge.svg)\n![Downloads](https://pepy.tech/badge/flwr)\n[![Slack](https://img.shields.io/badge/Chat-Slack-red)](https://flower.dev/join-slack)\n\nFlower (`flwr`) is a framework for building federated learning systems. The\ndesign of Flower is based on a few guiding principles:\n\n* **Customizable**: Federated learning systems vary wildly from one use case to\n  another. Flower allows for a wide range of different configurations depending\n  on the needs of each individual use case.\n\n* **Extendable**: Flower originated from a research project at the Univerity of\n  Oxford, so it was build with AI research in mind. Many components can be\n  extended and overridden to build new state-of-the-art systems.\n\n* **Framework-agnostic**: Different machine learning frameworks have different\n  strengths. Flower can be used with any machine learning framework, for\n  example, [PyTorch](https://pytorch.org),\n  [TensorFlow](https://tensorflow.org), [Hugging Face Transformers](https://huggingface.co/), [PyTorch Lightning](https://pytorchlightning.ai/), [MXNet](https://mxnet.apache.org/), [scikit-learn](https://scikit-learn.org/), [JAX](https://jax.readthedocs.io/), [TFLite](https://tensorflow.org/lite/), or even raw [NumPy](https://numpy.org/)\n  for users who enjoy computing gradients by hand.\n\n* **Understandable**: Flower is written with maintainability in mind. The\n  community is encouraged to both read and contribute to the codebase.\n\nMeet the Flower community on [flower.dev](https://flower.dev)!\n\n## Federated Learning Tutorial\n\nFlower\'s goal is to make federated learning accessible to everyone. This series of tutorials introduces the fundamentals of federated learning and how to implement them in Flower.\n\n1. **An Introduction to Federated Learning**\n\n   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/adap/flower/blob/main/tutorials/Flower-1-Intro-to-FL-PyTorch.ipynb) (or open the [Jupyter Notebook](https://github.com/adap/flower/blob/main/tutorials/Flower-1-Intro-to-FL-PyTorch.ipynb))\n\n1. **Using Strategies in Federated Learning**\n\n   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/adap/flower/blob/main/tutorials/Flower-2-Strategies-in-FL-PyTorch.ipynb) (or open the [Jupyter Notebook](https://github.com/adap/flower/blob/main/tutorials/Flower-2-Strategies-in-FL-PyTorch.ipynb))\n\n1. **Building Strategies for Federated Learning**\n\n   *--- coming soon ---*\n\n1. **Privacy and Security in Federated Learning**\n\n   *--- coming soon ---*\n\n1. **Scaling Federated Learning**\n\n   *--- coming soon ---*\n\n## Documentation\n\n[Flower Docs](https://flower.dev/docs):\n* [Installation](https://flower.dev/docs/installation.html)\n* [Quickstart (TensorFlow)](https://flower.dev/docs/quickstart-tensorflow.html)\n* [Quickstart (PyTorch)](https://flower.dev/docs/quickstart-pytorch.html)\n* [Quickstart (Hugging Face [code example])](https://flower.dev/docs/quickstart-huggingface.html)\n* [Quickstart (PyTorch Lightning [code example])](https://flower.dev/docs/quickstart-pytorch-lightning.html)\n* [Quickstart (MXNet)](https://flower.dev/docs/example-mxnet-walk-through.html)\n* [Quickstart (JAX [code example])](https://github.com/adap/flower/tree/main/examples/jax_from_centralized_to_federated)\n* [Quickstart (scikit-learn)](https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist)\n* [Quickstart (TFLite on Android [code example])](https://github.com/adap/flower/tree/main/examples/android)\n\n## Flower Baselines\n\nFlower Baselines is a collection of community-contributed experiments that reproduce the experiments performed in popular federated learning publications. Researchers can build on Flower Baselines to quickly evaluate new ideas:\n\n* [FedBN: Federated Learning on non-IID Features via Local Batch Normalization](https://arxiv.org/pdf/2102.07623.pdf):\n  * [Convergence Rate](https://github.com/adap/flower/tree/main/baselines/flwr_baselines/publications/fedbn/convergence_rate)\n* [Adaptive Federated Optimization](https://arxiv.org/pdf/2003.00295.pdf)\n  * [CIFAR-10/100](https://github.com/adap/flower/tree/main/baselines/flwr_baselines/publications/adaptive_federated_optimization)\n\nCheck the Flower documentation to learn more: [Using Baselines](https://flower.dev/docs/using-baselines.html)\n\nThe Flower community loves contributions! Make your work more visible and enable others to build on it by contributing it as a baseline: [Contributing Baselines](https://flower.dev/docs/contributing-baselines.html)\n\n## Flower Usage Examples\n\nA number of examples show different usage scenarios of Flower (in combination\nwith popular machine learning frameworks such as PyTorch or TensorFlow). To run\nan example, first install the necessary extras:\n\n[Usage Examples Documentation](https://flower.dev/docs/examples.html)\n\nQuickstart examples:\n\n* [Quickstart (TensorFlow)](https://github.com/adap/flower/tree/main/examples/quickstart_tensorflow)\n* [Quickstart (PyTorch)](https://github.com/adap/flower/tree/main/examples/quickstart_pytorch)\n* [Quickstart (Hugging Face)](https://github.com/adap/flower/tree/main/examples/quickstart_huggingface)\n* [Quickstart (PyTorch Lightning)](https://github.com/adap/flower/tree/main/examples/quickstart_pytorch_lightning)\n* [Quickstart (MXNet)](https://github.com/adap/flower/tree/main/examples/quickstart_mxnet)\n* [Quickstart (scikit-learn)](https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist)\n* [Quickstart (TFLite on Android)](https://github.com/adap/flower/tree/main/examples/android)\n\nOther [examples](https://github.com/adap/flower/tree/main/examples):\n\n* [Raspberry Pi & Nvidia Jetson Tutorial](https://github.com/adap/flower/tree/main/examples/embedded_devices)\n* [Android & TFLite](https://github.com/adap/flower/tree/main/examples/android)\n* [PyTorch: From Centralized to Federated](https://github.com/adap/flower/tree/main/examples/pytorch_from_centralized_to_federated)\n* [MXNet: From Centralized to Federated](https://github.com/adap/flower/tree/main/examples/mxnet_from_centralized_to_federated)\n* [JAX: From Centralized to Federated](https://github.com/adap/flower/tree/main/examples/jax_from_centralized_to_federated)\n* [Advanced Flower with TensorFlow/Keras](https://github.com/adap/flower/tree/main/examples/advanced_tensorflow)\n* [Advanced Flower with PyTorch](https://github.com/adap/flower/tree/main/examples/advanced_pytorch)\n* [Single-Machine Simulation of Federated Learning Systems](https://github.com/adap/flower/tree/main/examples/simulation)\n\n## Community\n\nFlower is built by a wonderful community of researchers and engineers. [Join Slack](https://flower.dev/join-slack) to meet them, [contributions](#contributing-to-flower) are welcome.\n\n<a href="https://github.com/adap/flower/graphs/contributors">\n  <img src="https://contrib.rocks/image?repo=adap/flower" />\n</a>\n\n## Citation\n\nIf you publish work that uses Flower, please cite Flower as follows: \n\n```bibtex\n@article{beutel2020flower,\n  title={Flower: A Friendly Federated Learning Research Framework},\n  author={Beutel, Daniel J and Topal, Taner and Mathur, Akhil and Qiu, Xinchi and Parcollet, Titouan and Lane, Nicholas D},\n  journal={arXiv preprint arXiv:2007.14390},\n  year={2020}\n}\n```\n\nPlease also consider adding your publication to the list of Flower-based publications in the docs, just open a Pull Request.\n\n## Contributing to Flower\n\nWe welcome contributions. Please see [CONTRIBUTING.md](CONTRIBUTING.md) to get\nstarted!\n',
    'author': 'The Flower Authors',
    'author_email': 'enquiries@flower.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://flower.dev',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
