# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['markdown_toolkit']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'markdown-toolkit',
    'version': '0.3.0',
    'description': 'Utility package for programmatically manipulating markdown documents.',
    'long_description': '# Markdown Toolkit\n![https://raw.githubusercontent.com/dcurtis/markdown-mark/99572b4a4f71b4ea2b1186a30f440ff2fcf66d27/svg/markdown-mark.svg](https://raw.githubusercontent.com/dcurtis/markdown-mark/99572b4a4f71b4ea2b1186a30f440ff2fcf66d27/svg/markdown-mark.svg)\n\n_A python library for creating and manipulating markdown with an object oriented interface._\n\nThis library is split into two aims:\n\n* Generation of markdown with python to create documents or fragments of documents.\n* Injection of static text, file contents, or dynamically generated markdown into existing documents.\n\nDocumentation can be found at the [project documentation](https://danielloader.github.io/markdown-toolkit) site.\n\n### License\n\nThis project is licenced under the terms of the MIT license.',
    'author': 'Daniel Loader',
    'author_email': 'hello@danielloader.uk',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/danielloader/markdown-toolkit/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
