# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qbert', 'qbert.piccolo_migrations']

package_data = \
{'': ['*']}

install_requires = \
['piccolo[orjson,postgres]>=0.74.4,<0.75.0',
 'pydantic>=1.9.1,<2.0.0',
 'ulid-py>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'qbert',
    'version': '0.1.1',
    'description': 'Dead simple task queue backed by PostgreSQL',
    'long_description': '# qbert\n\na dead simple task queue backed by postgres\n\nvery informal testing suggests a max performance around 100 jobs per second per worker on my machine.\n\n## usage\n\nadd `qbert.piccolo_app` to your `APP_REGISTRY` as per [the documentation](https://piccolo-orm.readthedocs.io/en/latest/piccolo/projects_and_apps/piccolo_apps.html).\n\nsee [example.py](example.py) for queue interaction examples.\n',
    'author': 'backwardspy',
    'author_email': 'backwardspy@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
