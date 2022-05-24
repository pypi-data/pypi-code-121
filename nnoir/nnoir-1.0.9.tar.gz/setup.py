# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nnoir', 'nnoir.functions']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4,<5', 'msgpack>=1,<2', 'numpy>=1,<2']

entry_points = \
{'console_scripts': ['nnoir2dot = nnoir.dot:nnoir2dot',
                     'nnrunner = nnoir.runner:main']}

setup_kwargs = {
    'name': 'nnoir',
    'version': '1.0.9',
    'description': 'API for NNOIR',
    'long_description': "# NNOIR\n\n## Install\n\n```\npip install nnoir\n```\n\n## Example\n\n### Create & Save\n\n```\ninputs  = [nnoir.Value(b'v0', dtype='<f4', shape=(10,10)),\n           nnoir.Value(b'v1', dtype='<f4', shape=(10,10))]\noutputs = [nnoir.Value(b'v2', dtype='<f4', shape=(10,10))]\nnodes = inputs + outputs\ninput_names = [ x.name for x in inputs ]\noutput_names = [ x.name for x in outputs ]\nfunctions = [nnoir.functions.Add(input_names, output_names)]\nresult = nnoir.NNOIR(b'Add', b'add_test', '0.1', input_names, output_names, nodes, functions)\nresult.dump('add.nnoir')\n```\n\n### Load\n\n```\nadd_nnoir = nnoir.load('add.nnoir')\n```\n",
    'author': 'Idein Inc.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Idein/nnoir/tree/master/nnoir',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
