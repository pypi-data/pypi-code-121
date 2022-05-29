# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['_dependencies', '_dependencies.objects', 'dependencies']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dependencies',
    'version': '7.2.0',
    'description': 'Constructor injection designed with OOP in mind.',
    'long_description': '# Dependencies [![build](https://img.shields.io/github/workflow/status/proofit404/dependencies/release?style=flat-square)](https://github.com/proofit404/dependencies/actions/workflows/release.yml?query=branch%3Arelease) [![pypi](https://img.shields.io/pypi/v/dependencies?style=flat-square)](https://pypi.org/project/dependencies)\n\nConstructor injection designed with OOP in mind.\n\n**[Documentation](https://proofit404.github.io/dependencies) |\n[Source Code](https://github.com/proofit404/dependencies) |\n[Task Tracker](https://github.com/proofit404/dependencies/issues)**\n\nDependency Injection (or simply DI) is a great technique. By using it you can\norganize responsibilities in you codebase. Define high level policies and system\nbehavior in one part. Delegate control to low level mechanisms in another part.\nSimple and powerful.\n\nWith help of DI you can use different parts of your system independently and\ncombine their behavior really easy.\n\nIf you split logic and implementation into different classes, you will see how\npleasant it becomes to change your system.\n\nThis tiny library helps you to connect parts of your system, in particular - to\ninject low level implementation into high level behavior.\n\n## Pros\n\n- Provide composition instead of inheritance.\n- Solves top-down architecture problems.\n- Boilerplate-free object hierarchies.\n- API entrypoints, admin panels, CLI commands are oneliners.\n\n## Example\n\nDependency injection without `dependencies`\n\n```pycon\n\n>>> from app.robot import Robot, Servo, Amplifier, Controller, Settings\n\n>>> robot = Robot(\n...     servo=Servo(amplifier=Amplifier()),\n...     controller=Controller(),\n...     settings=Settings(environment="production"),\n... )\n\n>>> robot.work()\n\n```\n\nDependency injection with `dependencies`\n\n```pycon\n\n>>> from dependencies import Injector\n\n>>> class Container(Injector):\n...     robot = Robot\n...     servo = Servo\n...     amplifier = Amplifier\n...     controller = Controller\n...     settings = Settings\n...     environment = "production"\n\n>>> Container.robot.work()\n\n```\n\n## Questions\n\nIf you have any questions, feel free to create an issue in our\n[Task Tracker](https://github.com/proofit404/dependencies/issues). We have the\n[question label](https://github.com/proofit404/dependencies/issues?q=is%3Aopen+is%3Aissue+label%3Aquestion)\nexactly for this purpose.\n\n## Enterprise support\n\nIf you have an issue with any version of the library, you can apply for a paid\nenterprise support contract. This will guarantee you that no breaking changes\nwill happen to you. No matter how old version you\'re using at the moment. All\nnecessary features and bug fixes will be backported in a way that serves your\nneeds.\n\nPlease contact [proofit404@gmail.com](mailto:proofit404@gmail.com) if you\'re\ninterested in it.\n\n## License\n\n`dependencies` library is offered under the two clause BSD license.\n\n<p align="center">&mdash; ⭐ &mdash;</p>\n',
    'author': 'Artem Malyshev',
    'author_email': 'proofit404@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/dependencies',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
