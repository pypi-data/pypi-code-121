# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deescovery', 'tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'deescovery',
    'version': '1.1.0',
    'description': 'Discover packages and classes in a python project.',
    'long_description': '<!--intro-start-->\n# Deescovery\n\n**Deescovery** is a Python package to find and initialize modules of your Python projects on startup.\n\n- Find and register blueprints in a Flask project.\n- Automatically initialize Flask extensions.\n- Find all SQLAlchemy models to make alembic happy.\n- Find all FastAPI endpoints.\n- Collect all Celery tasks.\n\nInitially designed to initialize Flask applications, it was made generic enough to work with any micro-framework or no framework at all.\n\n## Micro-framework initialization problem\n\nMicro-framework-based projects are clean while they\'re small. Every micro-framework codebase I\'ve seen, has a mess in the project initialization. With time, `create_app()` becomes filled with ad-hoc settings, imports-within-functions, and plug-in initializations.\n\nThe Application Factory Pattern, proposed, for example, in the [official Flask documentation](https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/), and the [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure), legitimize this approach.\n\nThe nature of `create_app()` leaves no place for the [open-closed principle](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html). We update this module every time we add a new plug-in, a new blueprint, or a new package.\n\n```python\n# myproject/__init__.py\n\ndef create_app(config_class=Config):\n    app = Flask(__name__)\n    app.config.from_object(config_class)\n\n    db.init_app(app)\n    migrate.init_app(app, db)\n    login.init_app(app)\n    mail.init_app(app)\n    bootstrap.init_app(app)\n    moment.init_app(app)\n    babel.init_app(app)\n\n    from myproject.errors import bp as errors_bp\n    app.register_blueprint(errors_bp)\n\n    from myproject.auth import bp as auth_bp\n    app.register_blueprint(auth_bp, url_prefix=\'/auth\')\n\n    return app\n```\n\n_A common Flask application. The code is based on the Flask Mega-Tutorial._\n\nWith `deescovery`, you can make the same code shorter, and remove the dependencies from implementation details.\n\n```python\n# file: myproject/app.py\nfrom flask import Flask\nfrom deescovery import discover\nfrom deescovery.flask import get_flask_rules\n\n\ndef create_app():\n    flask_app = Flask(__name__)\n    flask_app.config.from_object("myproject.config")\n    discover("myproject", get_flask_rules("myproject", flask_app))\n    return flask_app\n```\n\n\n<!--intro-end-->\n\n## Read more\n\n- [Usage with Flask](https://imankulov.github.io/deescovery/flask/)\n- [Usage with anything else](https://imankulov.github.io/deescovery/anything_else/)\n- [API](https://imankulov.github.io/deescovery/api/deescovery/)\n',
    'author': 'Roman Imankulov',
    'author_email': 'roman.imankulov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/imankulov/deescovery',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.8,<4.0',
}


setup(**setup_kwargs)
