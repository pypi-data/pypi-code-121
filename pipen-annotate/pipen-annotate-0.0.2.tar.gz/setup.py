# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pipen_annotate']
install_requires = \
['pardoc>=0.0,<0.1', 'pipen>=0.3,<0.4']

setup_kwargs = {
    'name': 'pipen-annotate',
    'version': '0.0.2',
    'description': 'Use docstring to annotate pipen processes',
    'long_description': '# pipen-annotate\n\nUse docstring to annotate [pipen](https://github.com/pwwang/pipen) processes\n\n## Installation\n\n```shell\npip install pipen-annotate\n```\n\n## Usage\n\n```python\nfrom pipen import Proc\nfrom pipen_annotate import annotate\n\n@annotate\nclass Process(Proc):\n    """Short description\n\n    Long description\n\n    Input:\n        infile: An input file\n        invar: An input variable\n\n    Output:\n        outfile: The output file\n\n    Args:\n        ncores: Number of cores\n    """\n    input = "infile:file, invar"\n    output = "outfile:file:output.txt"\n    args = {\'ncores\': 1}\n\nprint(Process.annotated)\n# prints:\n{\'args\': {\'ncores\': ParsedItem(name=\'ncores\',\n                               type=None,\n                               desc=\'Number of cores\',\n                               more=[ParsedPara(lines=[\'Default: 1\'])])},\n \'input\': {\'infile\': ParsedItem(name=\'infile\',\n                                type=\'file\',\n                                desc=\'An input file\',\n                                more=[]),\n           \'invar\': ParsedItem(name=\'invar\',\n                               type=\'var\',\n                               desc=\'An input variable\',\n                               more=[])},\n \'long\': [ParsedPara(lines=[\'Long description\'])],\n \'output\': {\'outfile\': ParsedItem(name=\'outfile\',\n                                  type=\'file\',\n                                  desc=\'The output file\',\n                                  more=[ParsedPara(lines=[\'Default: output.txt\'])])},\n \'short\': ParsedPara(lines=[\'Short description\'])}\n```\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
