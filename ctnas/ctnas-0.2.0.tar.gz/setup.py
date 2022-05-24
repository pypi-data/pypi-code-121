# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ctnas']

package_data = \
{'': ['*']}

install_requires = \
['deepstruct>=0.8.0,<0.9.0',
 'joblib>=1.1.0,<2.0.0',
 'networkx>=2.7.1,<3.0.0',
 'pandas>=1.4.1,<2.0.0',
 's3fs>=2022.2.0,<2023.0.0']

setup_kwargs = {
    'name': 'ctnas',
    'version': '0.2.0',
    'description': '',
    'long_description': '# CT-NAS [![PyPI version](https://badge.fury.io/py/ctnas.svg)](https://badge.fury.io/py/ctnas) ![Tests](https://github.com/innvariant/ctnas/workflows/Tests/badge.svg) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)\nThis module contains an API access to a Neural Architecture Search dataset on a search space called "computational themes".\nSuch themes are small directed acyclic graphs (DAGs) with a vertex collapse condition.\nThis condition makes the left and the right graph in the picture being equivalent / isomorphic.\n\nThe dataset contains computations of feed-forward neural networks with different hidden structural priors based on these themes.\nBy this, you can search for connections between graph theoretic properties of the search space and computational properties of the neural network models. \n\n![Computational Themes](res/compthemes-three-examples.drawio.png)\n\n## Installation\nVia *poetry* (**recommended** for projects) using PyPi:\n``poetry add ctnas``\n\nDirectly with *pip* from PyPi:\n```bash\npip install ctnas\n```\n\nVia *conda* in your *environment.yml* (recommended for reproducible experiments):\n```yaml\nname: exp01\nchannels:\n- defaults\ndependencies:\n- pip>=20\n- pip:\n    - ctnas\n```\n\nFrom public GitHub:\n```bash\npip install --upgrade git+ssh://git@github.com:innvariant/ctnas.git\n```\n\n## Usage examples\n```python\nfrom ctnas.api import CTNASApi\n\napi = CTNASApi()\nprint(api.get_datasets())\n# Should give you:\n# [\'spheres-b8c16fd7\', \'mnist\', \'spheres-23aeba4d\', \'spheres-bee36cd9\',\n#  \'spheres-b758e9f4\', \'spheres-0a19afe4\', \'cifar10\', \'spheres-6598864b\']\n```\n\n```python\nfrom ctnas.api import CTNASApi\n\napi = CTNASApi()\nprint(api.get_graph_properties().head())\n```\nGives you s.th. like:\n> test_dev.py .                             graph_uuid  num_nodes  ...  degree_var  undir_ecc_var\n0  6e302aa7-6208-42a9-b1e0-08ce6d9d83ba          6  ...    1.222222       0.222222\n1  ecd9c934-90ae-460c-855f-90c0b24a4150          6  ...    0.666667       0.000000\n2  d111e38f-3ed1-454f-9d0e-8ded0428c9d9          6  ...    1.000000       0.222222\n3  d23cac47-047c-4ec6-aaa4-e393b2ebeccd          5  ...    0.640000       0.240000\n4  c56bb6f8-a9ec-44db-8c17-37b166fb5b06          6  ...    0.888889       0.222222\n> \n> [5 rows x 19 columns]\n\n```python\nimport networkx as nx\nimport matplotlib.pyplot as plt\nfrom ctnas.api import CTNASApi\n\napi = CTNASApi()\ngraph = api.get_graph("0a1ded7d-677a-41f7-9361-c7079c8a34a7")\nnx.draw(graph)\nplt.show()\n```\n\n\n## Cite our work\n```bibtex\n@misc{stier2022ctnas,\n    title={CT-NAS: Analysis of Hidden Structural Priors for Neural Architecture Search},\n    author={Julian Stier and Michael Granitzer},\n    year={2022}\n}\n```\n\n## MinIO Policy\n```json\n{\n  "Version": "2012-10-17",\n  "Statement": [\n    {\n      "Action": [\n        "s3:GetObject"\n      ],\n      "Effect": "Allow",\n      "Resource": [\n        "arn:aws:s3:::homes/stier/ctnas/*"\n      ]\n    }\n  ]\n}\n```\n```json\n{\n  "Version": "2012-10-17",\n  "Statement": [\n    {\n      "Action": [\n        "s3:GetObject"\n      ],\n      "Effect": "Allow",\n      "Principal": {\n        "AWS": [\n          "*"\n        ]\n      },\n      "Resource": [\n        "arn:aws:s3:::homes/stier/ctnas/*"\n      ],\n      "Sid": ""\n    }\n  ]\n}\n```',
    'author': 'Julian Stier',
    'author_email': 'julian.stier@uni-passau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/innvariant/ctnas',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
