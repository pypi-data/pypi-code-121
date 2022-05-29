# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['typeapi']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.0.0']

setup_kwargs = {
    'name': 'typeapi',
    'version': '0.2.0',
    'description': '',
    'long_description': '# typeapi\n\nThis library provides a stable API to introspect Python\'s `typing` and `typing_extensions` type hints.\n\n## Installation\n\n    $ pip install typeapi\n\n## Example\n\n```py\nimport typing, typeapi\nprint(typeapi.of(typing.Mapping[typing.Annotated[str, "key"], typing.Literal[True, None, \'false\']]))\n# Type(collections.abc.Mapping, nparams=2, args=(Annotated(Type(str, nparams=0), \'key\'), Literal(values=(True, None, \'false\'))))\n```\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
