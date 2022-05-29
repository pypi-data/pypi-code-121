# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_aioredis', 'pydantic_aioredis.ext', 'pydantic_aioredis.ext.FastAPI']

package_data = \
{'': ['*']}

install_requires = \
['aioredis>=2.0.0,<3.0.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'pydantic-aioredis',
    'version': '0.5.0',
    'description': 'Use your pydantic models as an ORM, storing data in Redis.',
    'long_description': '# pydantic-aioredis\n\nA simple declarative ORM for Redis, using aioredis. Use your Pydantic\nmodels like an ORM, storing data in Redis!\n\nInspired by\n[pydantic-redis](https://github.com/sopherapps/pydantic-redis) by\n[Martin Ahindura](https://github.com/Tinitto)\n\n<p align="center">\n    <a href="https://github.com/andrewthetechie/pydantic-aioredis" target="_blank">\n        <img src="https://img.shields.io/github/last-commit/andrewthetechie/pydantic-aioredis" alt="Latest Commit">\n    </a>\n        <img src="https://github.com/andrewthetechie/pydantic-aioredis/actions/workflows/run_tests_with_tox.yaml/badge.svg?branch=main">\n        <img src="https://img.shields.io/codecov/c/github/andrewthetechie/pydantic-aioredis">\n    <br />\n    <a href="https://pypi.org/project/pydantic-aioredis" target="_blank">\n        <img src="https://img.shields.io/pypi/v/pydantic-aioredis" alt="Package version">\n    </a>\n    <img src="https://img.shields.io/pypi/pyversions/pydantic-aioredis">\n    <img src="https://img.shields.io/badge/license-MIT-green">\n</p>\n\n## Main Dependencies\n\n- [Python +3.6](https://www.python.org)\n- [aioredis 2.0](https://aioredis.readthedocs.io/en/latest/)\n- [pydantic](https://github.com/samuelcolvin/pydantic/)\n\n## Getting Started\n\n### Examples\n\nExamples are in the [examples/](./examples) directory of this repo.\n\n### Installation\n\nInstall the package\n\n    pip install pydantic-aioredis\n\n### Quick Usage\n\nImport the `Store`, the `RedisConfig` and the `Model` classes and use accordingly\n\n```python\nimport asyncio\nfrom datetime import date\nfrom pydantic_aioredis import RedisConfig, Model, Store\n\n# Create models as you would create pydantic models i.e. using typings\nclass Book(Model):\n    _primary_key_field: str = \'title\'\n    title: str\n    author: str\n    published_on: date\n    in_stock: bool = True\n\n# Do note that there is no concept of relationships here\nclass Library(Model):\n    # the _primary_key_field is mandatory\n    _primary_key_field: str = \'name\'\n    name: str\n    address: str\n\n# Create the store and register your models\nstore = Store(name=\'some_name\', redis_config=RedisConfig(db=5, host=\'localhost\', port=6379),life_span_in_seconds=3600)\nstore.register_model(Book)\nstore.register_model(Library)\n\n# Sample books. You can create as many as you wish anywhere in the code\nbooks = [\n    Book(title="Oliver Twist", author=\'Charles Dickens\', published_on=date(year=1215, month=4, day=4),\n        in_stock=False),\n    Book(title="Great Expectations", author=\'Charles Dickens\', published_on=date(year=1220, month=4, day=4)),\n    Book(title="Jane Eyre", author=\'Charles Dickens\', published_on=date(year=1225, month=6, day=4), in_stock=False),\n    Book(title="Wuthering Heights", author=\'Jane Austen\', published_on=date(year=1600, month=4, day=4)),\n]\n# Some library objects\nlibraries = [\n    Library(name="The Grand Library", address="Kinogozi, Hoima, Uganda"),\n    Library(name="Christian Library", address="Buhimba, Hoima, Uganda")\n]\n\nasync def work_with_orm():\n  # Insert them into redis\n  await Book.insert(books)\n  await Library.insert(libraries)\n\n  # Select all books to view them. A list of Model instances will be returned\n  all_books = await Book.select()\n  print(all_books) # Will print [Book(title="Oliver Twist", author="Charles Dickens", published_on=date(year=1215, month=4, day=4), in_stock=False), Book(...]\n\n  # Or select some of the books\n  some_books = await Book.select(ids=["Oliver Twist", "Jane Eyre"])\n  print(some_books) # Will return only those two books\n\n  # Or select some of the columns. THIS RETURNS DICTIONARIES not MODEL Instances\n  # The Dictionaries have values in string form so you might need to do some extra work\n  books_with_few_fields = await Book.select(columns=["author", "in_stock"])\n  print(books_with_few_fields) # Will print [{"author": "\'Charles Dickens", "in_stock": "True"},...]\n\n  # Update any book or library\n  await Book.update(_id="Oliver Twist", data={"author": "John Doe"})\n\n  # Delete any number of items\n  await Library.delete(ids=["The Grand Library"])\n\n# Now run these updates\nloop = asyncio.get_event_loop()\nloop.run_until_complete(work_with_orm())\n```\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide](./CONTRIBUTING.rst)\n\n## License\n\nLicensed under the [MIT License](./LICENSE)\n',
    'author': 'Andrew Herrington',
    'author_email': 'andrew.the.techie@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrewthetechie/pydantic-aioredis',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
