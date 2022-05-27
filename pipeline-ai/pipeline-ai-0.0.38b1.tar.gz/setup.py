# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipeline',
 'pipeline.api',
 'pipeline.docker',
 'pipeline.exceptions',
 'pipeline.objects',
 'pipeline.objects.huggingface',
 'pipeline.schemas',
 'pipeline.schemas.redis',
 'pipeline.util']

package_data = \
{'': ['*']}

install_requires = \
['dill>=0.3.4,<0.4.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyhumps>=3.0.2,<4.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.26.0,<3.0.0',
 'setuptools>=59.2.0,<60.0.0',
 'tqdm>=4.62.3,<5.0.0']

extras_require = \
{'docker': ['PyYAML>=6.0,<7.0']}

setup_kwargs = {
    'name': 'pipeline-ai',
    'version': '0.0.38b1',
    'description': 'Pipelines for machine learning workloads.',
    'long_description': '# [Pipeline](https://pipeline.ai) [![Production workflow](https://github.com/neuro-ai-dev/pipeline/actions/workflows/prod-wf.yml/badge.svg?branch=main)](https://github.com/neuro-ai-dev/pipeline/actions/workflows/prod-wf.yml) [![Version](https://img.shields.io/pypi/v/pipeline-ai)](https://pypi.org/project/pipeline-ai) ![Size](https://img.shields.io/github/repo-size/neuro-ai-dev/pipeline) ![Downloads](https://img.shields.io/pypi/dm/pipeline-ai) [![License](https://img.shields.io/crates/l/ap)](https://www.apache.org/licenses/LICENSE-2.0) [![Hiring](https://img.shields.io/badge/hiring-apply%20here-brightgreen)](https://jobs.lever.co/Neuro) [![Discord](https://img.shields.io/badge/discord-join-blue)](https://discord.gg/eJQRkBdEcs)\n\n[_powered by neuro_](https://getneuro.ai)\n\n# Table of Contents\n\n- [About](#about)\n- [Usage](#usage)\n  * [Huggingface Transformers](#huggingface-transformers)\n- [Installation instructions](#installation-instructions)\n  * [Linux, Mac (intel)](#linux--mac--intel-)\n  * [Mac (arm/M1)](#mac--arm-m1-)\n- [Development](#development)\n- [License](#license)\n\n# About\n\nPipeline is a python library that provides a simple way to construct computational graphs for AI/ML. The library is suitable for both development and production environments supporting inference and training/finetuning. This library is also a direct interface to [Pipeline.ai](https://pipeline.ai) which provides a compute engine to run pipelines at scale and on enterprise GPUs.\n\nThe syntax used for defining AI/ML pipelines shares some similarities in syntax to sessions in [Tensorflow v1](https://www.tensorflow.org/api_docs/python/tf/compat/v1/InteractiveSession), and Flows found in [Prefect](https://github.com/PrefectHQ/prefect). In future releases we will be moving away from this syntax to a C based graph compiler which interprets python directly (and other languages) allowing users of the API to compose graphs in a more native way to the chosen language.\n\n# Usage\n\n## Huggingface Transformers\n\n```\nfrom pipeline import Pipeline, Variable, pipeline_function, for_loop\nfrom pipeline.model.transformer_models import TransformersModel\n\n\nwith Pipeline(pipeline_name="GPTNeo") as pipeline:\n    input_str = Variable(variable_type=str, is_input=True)\n\n    hf_model = TransformersModel("EleutherAI/gpt-neo-125M", "EleutherAI/gpt-neo-125M")\n    output_str = hf_model.predict(input_str)\n\n    pipeline.output(output_str)\n\noutput_pipeline = Pipeline.get_pipeline("GPTNeo")\n\nprint(output_pipeline.run("Hello"))\n```\n\n# Installation instructions\n\n## Linux, Mac (intel)\n\n```\npip install -U pipeline-ai\n```\n\n## Mac (arm/M1)\n\nDue to the ARM architecture of the M1 core it is necessary to take additional steps to install Pipeline, mostly due to the transformers library. We recoomend running inside of a conda environment as shown below.\n\n1. Make sure Rosetta2 is disabled.\n2. From terminal run:\n\n```\nxcode-select --install\n```\n\n3. Install Miniforge, instructions here: [https://github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge) or follow the below:\n   1. Download the Miniforge install script here: [https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh)\n   2. Make the shell executable and run\n   ```\n   sudo chmod 775 Miniforge3-MacOSX-arm64.sh\n   ./Miniforge3-MacOSX-arm64.sh\n   ```\n4. Create a conda based virtual env and activate:\n\n```\nconda create --name pipeline-env python=3.9\nconda activate pipeline-env\n```\n\n5. Install tensorflow\n\n```\nconda install -c apple tensorflow-deps\npython -m pip install -U pip\npython -m pip install -U tensorflow-macos\npython -m pip install -U tensorflow-metal\n```\n\n6. Install transformers\n\n```\nconda install -c huggingface transformers -y\n```\n\n7. Install pipeline\n\n```\npython -m pip install -U pipeline-ai\n```\n# Development\n\nThis project is made with poetry, [so firstly setup poetry on your machine](https://python-poetry.org/docs/#installation).\n\nOnce that is done, please run\n\n    sh setup.sh\n\nWith this you should be good to go. This sets up dependencies, pre-commit hooks and\npre-push hooks.\n\n\nYou can manually run pre commit hooks with\n\n    pre-commit run --all-files\n\nTo run tests manually please run\n\n    pytest\n\n# License\n\nPipeline is licensed under [Apache Software License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).\n',
    'author': 'Paul Hetherington',
    'author_email': 'ph@mystic.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
