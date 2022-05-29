# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['independency']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'independency',
    'version': '1.2',
    'description': 'Dependency injection container',
    'long_description': "# Independency\nIndependency is a DI container library. Unlike many other Python DI containers Independency operates in the local scope. It's inspired by [punq](https://github.com/bobthemighty/punq), so the API is very similar.\n\nIndependency supports generics and other specific typings.\n\n\n## Installation\n\n```bash\npip install independency\n```\n\n## Quick start\nIndependency avoids global state, so you must explicitly create a container in the entrypoint of your application:\n\n```\nimport independency\n\nbuilder = independency.ContainerBuilder()\n# register application dependencies\ncontainer = builder.build()\n```\n\n## Examples\n```python3\nimport requests\n\nfrom independency import Container, ContainerBuilder\n\n\nclass Config:\n    def __init__(self, url: str):\n        self.url = url\n\n\nclass Getter:\n    def __init__(self, config: Config):\n        self.config = config\n\n    def get(self):\n        return requests.get(self.config.url)\n\n\ndef create_container() -> Container:\n    builder = ContainerBuilder()\n    builder.singleton(Config, Config, url='http://example.com')\n    builder.singleton(Getter, Getter)\n    return builder.build()\n\n\ndef main():\n    container = create_container()\n    getter: Getter = container.resolve(Getter)\n    print(getter.get().status_code)\n\n\nif __name__ == '__main__':\n    main()\n```\n\nSuppose we need to declare multiple objects of the same type and use them correspondingly.\n\n```python3\nfrom independency import Container, ContainerBuilder, Dependency as Dep\n\n\nclass Queue:\n    def __init__(self, url: str):\n        self.url = url\n\n    def pop(self):\n        ...\n\n    \nclass Consumer:\n    def __init__(self, q: Queue):\n        self.queue = q\n\n    def consume(self):\n        while True:\n            message = self.queue.pop()\n            # process message\n\n\ndef create_container() -> Container:\n    builder = ContainerBuilder()\n    builder.singleton('first_q', Queue, url='http://example.com')\n    builder.singleton('second_q', Queue, url='http://example2.com')\n    builder.singleton('c1', Consumer, q=Dep('first_q'))\n    builder.singleton('c2', Consumer, q=Dep('second_q'))\n    return builder.build()\n\n\ndef main():\n    container = create_container()\n    consumer: Consumer = container.resolve('c1')\n    consumer.consume()\n\n\nif __name__ == '__main__':\n    main()\n```",
    'author': 'apollon',
    'author_email': 'Apollon76@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Apollon76/di',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
