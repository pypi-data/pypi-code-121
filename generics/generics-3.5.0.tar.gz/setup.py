# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['_generics', 'generics']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'generics',
    'version': '3.5.0',
    'description': 'A classy toolkit designed with OOP in mind.',
    'long_description': '# Generics\n\n[![build](https://img.shields.io/github/workflow/status/proofit404/generics/release?style=flat-square)](https://github.com/proofit404/generics/actions/workflows/release.yml?query=branch%3Arelease)\n[![pypi](https://img.shields.io/pypi/v/generics?style=flat-square)](https://pypi.org/project/generics)\n[![python](https://img.shields.io/pypi/pyversions/generics?style=flat-square)](https://pypi.org/project/generics)\n\nA classy toolkit designed with OOP in mind.\n\n**[Documentation](https://proofit404.github.io/generics) |\n[Source Code](https://github.com/proofit404/generics) |\n[Task Tracker](https://github.com/proofit404/generics/issues)**\n\nIn our opinion, main benefits of having objects implemented in the language are\nencapsulation and polymorphous. Classes that could be easily used in a\ncomposition are tricky to write. The `generics` library aims to help you in\nwriting code with high quality.\n\n## Pros\n\n- Real private attributes without loosing the readability\n- Leads to a better design forcing you to use encapsulation properly\n- Makes writing quality code with high cohesion and low coupling easier\n- Guides you to follow SOLID principles\n\n## Example\n\nThe `generics` library gives you an easy way to define private attributes on\nobjects without loosing little nice things like readability.\n\n```pycon\n\n>>> from generics import private\n\n>>> @private\n... class User:\n...     def __init__(self, name):\n...         self.name = name\n...\n...     def greet(self):\n...         return f"Hello, {self.name}"\n\n>>> user = User("Jeff")\n\n>>> user.greet()\n\'Hello, Jeff\'\n\n>>> hasattr(user, "name")\nFalse\n\n```\n\n## Questions\n\nIf you have any questions, feel free to create an issue in our\n[Task Tracker](https://github.com/proofit404/generics/issues). We have the\n[question label](https://github.com/proofit404/generics/issues?q=is%3Aopen+is%3Aissue+label%3Aquestion)\nexactly for this purpose.\n\n## Enterprise support\n\nIf you have an issue with any version of the library, you can apply for a paid\nenterprise support contract. This will guarantee you that no breaking changes\nwill happen to you. No matter how old version you\'re using at the moment. All\nnecessary features and bug fixes will be backported in a way that serves your\nneeds.\n\nPlease contact [proofit404@gmail.com](mailto:proofit404@gmail.com) if you\'re\ninterested in it.\n\n## License\n\n`generics` library is offered under the two clause BSD license.\n\n<p align="center">&mdash; ⭐ &mdash;</p>\n',
    'author': 'Artem Malyshev',
    'author_email': 'proofit404@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/generics',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
