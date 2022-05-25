# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deepa2',
 'deepa2.builder',
 'deepa2.metrics',
 'deepa2.preptrain',
 'deepa2.testing']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'datasets>=1.18.0,<2.0.0',
 'networkx>=2.6.3,<3.0.0',
 'numpy>=1.21.5,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'pyarrow>=6.0.1,<7.0.0',
 'requests>=2.27.1,<3.0.0',
 'ttp>=0.8.4,<0.9.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['deepa2 = deepa2.main:app']}

setup_kwargs = {
    'name': 'deepa2',
    'version': '0.1.6',
    'description': 'Cast NLP data as multiangular DeepA2 datasets and integrate these in training pipeline',
    'long_description': '<p align="left">\n    <a href="https://github.com/debatelab/deepa2/actions/workflows/run_pytest.yml">\n        <img alt="unit tests" src="https://github.com/debatelab/deepa2-datasets/actions/workflows/run_pytest.yml/badge.svg?branch=main">\n    </a>\n    <a href="https://github.com/debatelab/deepa2/actions/workflows/code_quality_checks.yml">\n        <img alt="code quality" src="https://github.com/debatelab/deepa2-datasets/actions/workflows/code_quality_checks.yml/badge.svg?branch=main">\n    </a>\n    <a href="https://codeclimate.com/github/debatelab/deepa2">\n        <img alt="Code Climate maintainability" src="https://img.shields.io/codeclimate/maintainability/debatelab/deepa2">\n    </a>\n    <a href="https://pypi.org/project/deepa2/">\n        <img src="https://img.shields.io/pypi/v/deepa2" alt="PyPI version">\n    </a>    \n</p>\n\n# Deep Argument Analysis (`deepa2`)</p>\n\nThis project provides `deepa2`, which\n\n* 🥚 takes NLP data (e.g. NLI, argument mining) as ingredients;\n* 🎂 bakes DeepA2 datatsets conforming to the [Deep Argument Analysis Framework](https://arxiv.org/abs/2110.01509);\n* 🍰 serves DeepA2 data as text2text datasets suitable for training language models.\n\nThere\'s a public collection of 🎂 DeepA2 datatsets baked with `deepa2` at the [HF hub](https://huggingface.co/datasets/debatelab/deepa2).\n\nThe [Documentation](docs/) describes usage options and gives background info on the Deep Argument Analysis Framework.\n\n\n## Quickstart\n\n### Integrating `deepa2` into Your Training Pipeline\n\n1. Install `deepa2` into your ML project\'s virtual environment, e.g.:\n\n```bash\nsource my-projects-venv/bin/activate \npython --version  # should be ^3.7\npython -m pip install deepa2\n```\n\n2. Add `deepa2` preprocessor to your training pipeline. Your training script may look like, for example:\n\n```sh\n#!/bin/bash\n\n# configure and activate environment\n...\n\n# download deepa2 datasets and \n# prepare for text2text training\ndeepa2 serve \\\n    --path some-deepa2-dataset \\    # <<< 🎂\n    --export_format csv \\\n    --export_path t2t \\             # >>> 🍰\n\n# run default training script, \n# e.g., with 🤗 Transformers\npython .../run_summarization.py \\\n    --train_file t2t/train.csv \\    # <<< 🍰\n    --text_column "text" \\\n    --summary_column "target" \\\n    --...\n\n# clean-up\nrm -r t2t\n```\n\n3. That\'s it.\n\n\n### Create DeepA2 datasets with `deepa2` from existing NLP data\n\nInstall [poetry](https://python-poetry.org/docs/#installation). \n\nClone the repository:\n```bash\ngit clone https://github.com/debatelab/deepa2-datasets.git\n```\n\nInstall this package from within the repo\'s root folder:\n```bash\npoetry install\n```\n\nBake a DeepA2 dataset, e.g.:\n```bash\npoetry run deepa2 bake \\\\\n  --name esnli \\\\                   # <<< 🥚\n  --debug-size 100 \\\\\n  --export-path ./data/processed    # >>> 🎂  \n```\n\n## Contribute a DeepA2Builder for another Dataset\n\nWe welcome contributions to this repository, especially scripts that port existing datasets to the DeepA2 Framework. Within this repo, a code module that transforms data into the DeepA2 format contains\n\n1. a Builder class that describes how DeepA2 examples will be constructed and that implements the abstract `builder.Builder` interface (such as, e.g., `builder.entailmentbank_builder.EnBankBuilder`);\n2. a DataLoader which provides a method for loading the raw data as a 🤗 Dataset object (such as, for example, `builder.entailmentbank_builder.EnBankLoader`) -- you may use `deepa2.DataLoader` as is in case the data is available in a way compatible with 🤗 Dataset;\n3. dataclasses which describe the features of the raw data and the preprocessed data, and which extend the dummy classes `deepa2.RawExample` and `deepa2.PreprocessedExample`;\n4. a collection of unit tests that check the concrete Builder\'s methods (such as, e.g., `tests/test_enbank.py`);\n5. a documentation of the pipeline (as for example in `docs/esnli.md`).\n\nConsider **suggesting** to collaboratively construct such a pipeline by opening a [new issue](https://github.com/debatelab/deepa2/issues/new?assignees=&labels=enhancement&template=new_dataset.md&title=%5BDATASET+NAME%5D).\n\n## Citation\n\nThis repository builds on and extends the DeepA2 Framework originally presented in:\n\n```bibtex\n@article{betz2021deepa2,\n      title={DeepA2: A Modular Framework for Deep Argument Analysis with Pretrained Neural Text2Text Language Models}, \n      author={Gregor Betz and Kyle Richardson},\n      year={2021},\n      eprint={2110.01509},\n      archivePrefix={arXiv},\n      primaryClass={cs.CL}\n}\n```\n',
    'author': 'Gregor Betz',
    'author_email': 'gregor.betz@kit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/debatelab/deepa2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
