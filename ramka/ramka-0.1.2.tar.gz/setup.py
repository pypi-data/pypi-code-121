# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ramka',
 'ramka.middleware',
 'ramka.request',
 'ramka.response',
 'ramka.routing',
 'ramka.static',
 'ramka.templates',
 'ramka.test',
 'ramka.views']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'WebOb>=1.8.7,<2.0.0',
 'furo>=2022.4.7,<2023.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'parse>=1.19.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'whitenoise>=6.0.0,<7.0.0']

setup_kwargs = {
    'name': 'ramka',
    'version': '0.1.2',
    'description': 'ramka - a simple Python web framework',
    'long_description': "# ramka\n\n[![Tests](https://github.com/mateuszcisek/ramka/actions/workflows/tests.yaml/badge.svg)](https://github.com/mateuszcisek/ramka/actions/workflows/tests.yaml)\n[![Linting](https://github.com/mateuszcisek/ramka/actions/workflows/linting.yaml/badge.svg)](https://github.com/mateuszcisek/ramka/actions/workflows/linting.yaml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)\n\n\n*ramka* (a Polish word for a small frame) is a very simple web framework written\nin Python. It is based on a very good course \n[Building Your Own Python Web Framework](https://testdriven.io/courses/python-web-framework/)\nby [testdriven.io](https://testdriven.io/) which I highly recommend.\n\nPlease bear in mind that at the moment only very basic functionality is\nimplemented and that this framework is far from being finished. Having said\nthat, I do have some ideas for the future.\n\nAt the moment, you can define some routes and then serve the content (HTML,\ntext, JSON) to the client. You can use dynamic routes and serve templates and\nstatic files (like stylesheets and images). And that's it. A framework is\nprobably a big word for it but there is some potential for it to grow.\n\nAs I said it's still a work in progress. Some features I am planning to add:\n\n* database support - there are no plans to implement custom ORM, but integrating\n  one of the existing ones (like SQLAlchemy) is probably a good start,\n* authentication - it can use databases or some different method,\n* plugins - the goal is to add a plugin mechanism and add more features as\n  installable plugins.\n\nThere will be probably more but it's difficult for me to say at the moment.\nAnyway, I would treat this as a learning project rather than a real framework.\nFeel free to try it out and send me any feedback.\n\n## Documentation\n\nThe documentation is available at https://ramka.readthedocs.io/.\n\n## Installation\n\nTo install the package using `pip`, run the following command:\n\n```bash\npip install ramka\n```\n\nTo add it as a `poetry` dependency, run:\n\n```bash\npoetry add ramka\n```\n\n## License\n\nMIT\n",
    'author': 'Mateusz Cisek',
    'author_email': 'cismat@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mateuszcisek/ramka',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
