# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wintry',
 'wintry.cli',
 'wintry.cli.commands',
 'wintry.cli.templates',
 'wintry.cli.templates.generate',
 'wintry.drivers',
 'wintry.errors',
 'wintry.ioc',
 'wintry.mqs',
 'wintry.query',
 'wintry.repository',
 'wintry.testing',
 'wintry.transactions',
 'wintry.transporters',
 'wintry.utils']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.35,<2.0.0',
 'aio-pika>=7.2.0,<8.0.0',
 'asyncpg>=0.25.0,<0.26.0',
 'cookiecutter>=1.7.3,<2.0.0',
 'dataclass-wizard>=0.22.0,<0.23.0',
 'fastapi>=0.78.0,<0.79.0',
 'mongomock>=4.0.0,<5.0.0',
 'motor>=2.5.1,<3.0.0',
 'pydantic==1.9.0',
 'typer[all]>=0.4.1,<0.5.0',
 'uvicorn[standard]>=0.17.6,<0.18.0']

extras_require = \
{'redis': ['aioredis>=2.0.1,<3.0.0']}

setup_kwargs = {
    'name': 'wintry',
    'version': '0.1.3',
    'description': 'A modern python web framework. Based on python-3.10, dataclasses and type-hints',
    'long_description': '<img src="docs/img/logo.jpg" />\n\n# ❄️🐧A modern python web framework🐧❄️\n\n\n\n\n![](https://img.shields.io/static/v1?label=code&message=python&color=<blue>&style=plastic&logo=github&logoColor=4ec9b0)\n![](https://img.shields.io/static/v1?label=web&message=framework&color=<blue>&style=plastic&logo=github&logoColor=4ec9b0)\n![](https://img.shields.io/static/v1?label=Tests&message=Passing&color=<blue>&style=plastic&logo=github&logoColor=4ec9b0)\n![](https://img.shields.io/static/v1?label=pypi%20package&message=v0.1.0&color=<blue>&style=plastic&logo=github&logoColor=4ec9b0)\n\n\nHello, friend, welcome to 🐧**Wintry**🐧. You may have stumble with this project searching\nfor a python web framework, well, you got what you want.\n\nPherhaps you know many other frameworks, pherhaps you know Django, or maybe Flask,\nor hopefully FastAPI. And odds are that you are willing to take a new project for a\nride with a new alternative. Well, 🐧**Wintry**🐧 is this, your new alternative, one that\ndo not push you out of your confort zone, but do not take the "written before" path.\n\nBeign accured, if you have used FastAPI, you would feel at home, 🐧**Wintry**🐧 is heavilly\ninspired in FastAPI, it actually uses it whenever it can. But it add a bunch of \n😎\'cool\'🆒 stuff on top.\n\n## Inspirations\n---------------\n\nI have used FastAPI a lot for the last year, and I am absolutely fascinated about it.\nSpeed + Python on the same sentence, that\'s something to really appreciate. I know, a big\nthanks to starlette project which is the real hero on that movie, but, FastAPI adds a ton\nof cool features on top, if I would describe them in one word, it would be: Pydantic.\n\nOk, but, Django has a lot of cool features too, it is even called \'Batteries included\nframework\', and it is true, I mean, who doesn\'t love the Django\'s builtin Admin Interface,\nor Django Forms?, not to mention DjangoRestFramework which is a REAALLY cool piece of software.\n\nEnough flattering, 🐧**Wintry**🐧 will try to be the new Kid in Town, to provide a DDD\nfocused experience, with builtin Dependency Injection system, a dataclasses based\nRepository Pattern implementation, Unit Of Work, Events Driven Components and a lot more.\nActually, I aimed to provide a similar experience with Repositories than that of\nSpring JPA. Just look at the example, it is really easy to write decoupled and modularized\n applications with 🐧**Wintry**🐧.\n\nLet\'s see what 🐧**Wintry**🐧 looks like:\n\n```python\nfrom wintry.models import Model\nfrom wintry.repository import Repository\nfrom wintry.controllers import controller, post, get\nfrom wintry.ioc import provider\nfrom wintry.errors import NotFoundError\nfrom wintry import App\nfrom wintry.settings import BackendOptions, ConnectionOptions, WinterSettings\nfrom dataclasses import field\nfrom uuid import uuid4\nfrom pydantic import BaseModel\n\nclass Hero(Model):\n    id: str = field(default_factory=lambda: uuid4().hex)\n    city: str\n    name: str\n\nclass HeroForm(BaseModel):\n    city: str\n    name: str\n\n@provider\nclass HeroRepository(Repository[Hero, str], entity=Hero):\n    async def get_by_name(self, *, name: str) -> Hero | None:\n        ...\n\n@controller\nclass MarvelController:\n    heroes: HeroRepository\n\n    @post(\'/hero\', response_model=Hero)\n    async def save_hero(self, hero_form: HeroForm = Body(...)):\n        hero = Hero.build(hero_form.dict())\n        await self.heroes.create(hero)\n        return hero\n\n    @get(\'/hero/{name}\', response_model=HeroForm)\n    async def get_villain(self, name: str):\n        hero = await self.heroes.get_by_name(name=name)\n        if hero is None:\n            raise NotFoundError()\n\n        return hero\n\n\nsettings = WinterSettings(\n    backends=[\n        BackendOptions(\n            driver="wintry.drivers.pg",\n            connection_options=ConnectionOptions(\n                url="postgresql+asyncpg://postgres:secret@localhost/tests"\n            )\n        )\n    ],\n)\n\napi = App(settings)\n```\n\nNote that the method **get_by_name** is NOT IMPLEMENTED, but it somehow still works :). \nThe thing is Repositories are query compilers,\nand you dont need to implement them, only learn a very simple\nquery syntax. That\'s not the only thing, the **@provider** decorator\nallows the repositories to be injected inside the marvel controller\nconstructor, just like happens in .NET Core or Java Spring. But you can already\nsee that dependencies can be declared as attributes, making them more declarative.\nActually, the real power of the IoC System of 🐧**Wintry**🐧 is that it allows to\ncombine the power of classical Dependency Injection, with Request-Based Dependency Injection\nachieved by FastAPI, which gives you the ability to re-use dependencies over a whole bunch\nof routes, and still been able to access its results.\n\n```python\n@dataclass\nclass User:\n    name: str\n    password: str\n\n@provider\nclass UserService:\n    def do_something_user(self, user: User):\n        return user.name + " " + user.password\n\n@controller\nclass Controller:\n    service: UserService\n    # This is populated on each request\n    user: User = Depends()\n\n    @get("/user")\n    async def get_user(self):\n        return self.user\n\n    @get("/something")\n    async def get_something(self):\n        return self.service.do_something_user(self.user)\n```\n\nThis is a really powerfull feature that both reduce code duplication and open doors for\na lot of functionalities, like Controller-Scoped authentication, filters, etc.\n\nYou may have noted from the first example, that my Hero entity does not contain anything special, it is merely a dataclass (That\'s the only restriction, models needs to be dataclasses). When using postgres (Or any compatible sqlalchemy database)\n🐧**Wintry**🐧 will do its bests to create a database Schema that best matches your domain model without poisoning it\nwith DataAccess dependencies. If you need a finer control over your database schema when using SQL, then you could\nuse the ```for_model()``` function to map to your model. It looks like this\n\n```python\nUserTable = for_model(\n    User,\n    metadata,\n    Column("id", Integer, primary_key=True),\n    Column("name", String),\n    Column("age", Integer),\n    Column("address_id", Integer, ForeignKey("Addresses.id")),\n    table_name="Users",\n    address=relation(Address, lazy="joined", backref="users"),\n)\n```\n\nFuthermore, if I want to change to use **MongoDB** instead of **Postgres**, is as easy as\nto change the configuration url and the driver \nand THERE IS NO NEED TO CHANGE THE CODE,\nit would just work.\n\n``` python\n.... # rest of the same code\nsettings = WinterSettings(\n    backends=[\n        BackendOptions(\n            driver="wintry.drivers.mongo",\n            connection_options=ConnectionOptions(\n                url="mongodb://localhost/?replicaSet=dbrs"\n            )\n        )\n    ],\n)\n....\n```\n\nOf course, you maybe want to use refs instead of embedded documents, in that case then you need to do\nexactly that, make your model split its objects with refs relations and the simply use it as usual.\n\nYou can look for an example at this [test app](https://github.com/adriangs1996/wintry/tree/master/tuto) or\n[this app](https://github.com/adriangs1996/wintry/tree/master/test_app)\n\nYou can also go and read the [📜documentation, it is still under development, but eventually will cover the whole API, just as FastAPI or Django](https://adriangs1996.github.io/wintry)\n\n## Installation\n---------------\nAs simple as use\n\n```\n$ pip install wintry\n```\n\nor with poetry\n\n```\n$ poetry add wintry\n```\n\n## Features\n-----------\nThere is a lot more to know about Wintry:\n\n* Stack of patterns (RepositoryPattern, UnitOfWork, ProxyPattern,\nMVC, Event-Driven-Desing,\nCQRS, etc.)\n\n* Automatic Relational Database metadata creation.\n\n* Automatic Query Creation.\n\n* Reactive Domain Models.\n\n* Dependency Injection (Next Level).\n\n* Publisher Subscribers.\n\n* Services.\n\n* Domain Model based on dataclasses.\n\n* Short: Focus on what really matters, write less code, get more results.\n\n* Everything from FastAPI in a really confortable way\n\n* Settings based on Pydantic.\n\n* A handy cli for managing projects (Feeling jealous of Rails ?? Not any more): Work in progress.\n\n\n## ROADMAP\n----------\n* Performance similar to FastAPI (When possible, actually FastAPI is a LOWER BOUND) (need benchmarks and identify bottle necks).\n\n* Create documentation\n\n* Add more features to the feature list with links to\nthe corresponding documentation\n\n* Add RPC support (Maybe protobuf, raw TCP, Redis, RabbitMQ, Kafka, etc)\n\n* Ease registration of Middlewares\n\n* Provide Implementation of Authorization Services\n\n* Create CLI for managing project\n\n* Provide Support for migrations (from the cli)\n\n* Templates\n\n* Maybe some ViewEngine (Most likely will be based on Jinja2)\n\n* Implement a builtin Admin (Similar to Django), but taking advantage of the registry system.\nCool stuff here, perhaps we can dynamically create models and manage the databases in the admin\nwith a UI. IDK, maybe, just maybe.\n\n## Contributions\n----------------\n\nEvery single contribution is very appreciated. From ideas, issues,\nPR, criticism, anything you can imagine.\n\nIf you are willing to provide a PR for a feature, just try to\ngive at least some tests for the feature, I do my best\nmantaining a pool of tests that will be growing with time\n\n- [Issue Tracker](https://github.com/adriangs1996/wintry/issues)\n\n- [Fork the repo, change it, and make a PR](https://github.com/adriangs1996/wintry)\n\n## Thanks\n--------\nTo @tiangolo for the amazing [SQLModel](https://github.com/tiangolo/sqlmodel) and [FastAPI](https://github.com/tiangolo/fastapi)\n\nTo the amazing [Django Team](https://github.com/django/django)\n\nTo the Spring Project and [NestJS](https://nestjs.com/) for such amazing frameworks\n\n\nLicense\n-------\n\nThis project is licensed under the MIT License',
    'author': 'adriangs1996',
    'author_email': 'adriangonzalezsanchez1996@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://adriangs1996.github.io/wintry',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
