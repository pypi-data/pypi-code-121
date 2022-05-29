# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bevy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bevy',
    'version': '1.2.3',
    'description': 'Python Dependency Inversion made simple so you can focus on creating amazing code.',
    'long_description': '# Bevy\nBevy makes using *Dependency Injection* a breeze so that you can focus on creating amazing code.\n\n## Installation\n```shell script\npip install bevy\n```\n\n**[Documentation](docs/documentation.md)**\n\n## Dependency Injection\nPut simply, *Dependency Injection* is a design pattern where the objects that your class depends on are instantiated outside of the class. Those dependencies are then injected into your class when it is instantiated.\nThis promotes loosely coupled code where your class doesn’t require direct knowledge of what classes it depends on or how to create them. Instead your class declares what class interface it expects and an outside framework handles the work of creating the class instances with the correct interface.\n\n## Interfaces\nPython doesn’t have an actual interface implementation like many other languages. Class inheritance, however, can be used in a very similar way since subclasses will likely have the same fundamental interface as their base class. \n\n## Why Do I Care?\n*Dependency Injection* and its reliance on abstract interfaces makes your code easier to maintain:\n- Changes can be made without needing to alter implementation details in unrelated code, so long as the interface isn’t modified in a substantial way.\n- Tests can provide mock implementations of dependencies without needing to jump through hoops to inject them. They can provide the mock to the context and Bevy will make sure it is used where appropriate.\n\n## How It Works\nBevy is an object oriented *dependency injection* framework. Similar to Pydantic, it relies on Python 3\'s class\nannotations, using them to determine what dependencies a class has.\n\n**Example**\n```py\nfrom bevy.injection import AutoInject, detect_dependencies\n@detect_dependencies\nclass Example(AutoInject):\n    dependency: Dependency\n```\nEach dependency when instantiated is added to a context repository for reuse. This allows many classes to share the same\ninstance of each dependency. This is handy for sharing things like database connections, config files, or authenticated\nAPI sessions.\n\n## Bevy Constructors\n\nTo instantiate classes and have Bevy inject their dependencies it is necessary to bind them to a \n`bevy.injection.Context`. This will give a callable that will build instances that are bound to the context.\n\n**Example**\n```py\nimport bevy.injection\ncontext = bevy.injection.Context()\nbuilder = context.bind(Example)\nexample = builder()  # An instance of Example will be created\n```\n### Configuring Dependencies\n\nWhen the `Context` encounters a dependency that is not in its repository it will attempt to create the\ndependency. The approach is very naive, it will just call the dependency with no arguments. If it succeeds it will be\nadded to the repository for later use and injected into the class.\n\nThis behavior can be changed by passing an instantiated dependency to `Context.add`.\n**Example**\n```py\ncontext.add(Dependency("foobar"))\n```\n\n### Getting Instances\nYou can get an instance of a class by using `Context.get` or `Context.get_or_create`. `get_or_create` will naively create an instance of the requested class if it is not found.\n**Example**\n```python\ninst = context.get(Dependency)\n```\n',
    'author': 'Zech Zimmerman',
    'author_email': 'hi@zech.codes',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ZechCodes/Bevy',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
