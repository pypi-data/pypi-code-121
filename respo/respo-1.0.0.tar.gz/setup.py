# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['respo', 'respo.fields']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.7.0']

extras_require = \
{'all': ['PyYAML>=5.0', 'SQLAlchemy>=1.4.3', 'click>=6.0.0', 'django>=3.1'],
 'cli': ['PyYAML>=5.0', 'click>=6.0.0'],
 'django': ['django>=3.1'],
 'sqlalchemy': ['SQLAlchemy>=1.4.3']}

entry_points = \
{'console_scripts': ['respo = respo.cli:app']}

setup_kwargs = {
    'name': 'respo',
    'version': '1.0.0',
    'description': 'File based RBAC in Python made easy.',
    'long_description': '<a href="https://codecov.io/gh/rafsaf/respo" target="_blank">\n  <img src="https://img.shields.io/codecov/c/github/rafsaf/respo" alt="Coverage">\n</a>\n\n<a href="https://github.com/psf/black" target="_blank">\n    <img src="https://img.shields.io/badge/code%20style-black-lightgrey" alt="Black">\n</a>\n\n<a href="https://github.com/rafsaf/respo/actions?query=workflow%3ATest" target="_blank">\n    <img src="https://github.com/rafsaf/respo/workflows/Test/badge.svg" alt="Test">\n</a>\n\n<a href="https://github.com/rafsaf/respo/actions?query=workflow%3APublish" target="_blank">\n  <img src="https://github.com/rafsaf/respo/workflows/Publish/badge.svg" alt="Publish">\n</a>\n\n<a href="https://github.com/rafsaf/respo/actions?query=workflow%3AGh-Pages" target="_blank">\n  <img src="https://github.com/rafsaf/respo/workflows/Gh-Pages/badge.svg" alt="Gh-Pages">\n</a>\n\n<a href="https://github.com/rafsaf/respo/blob/main/LICENSE" target="_blank">\n    <img src="https://img.shields.io/github/license/rafsaf/respo" alt="License">\n</a>\n\n<a href="https://pypi.org/project/respo/" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/respo" alt="Python version">\n</a>\n\n## Documentation\n\n**https://rafsaf.github.io/respo/**\n\n## Installation\n\n```\npip install respo[all]\n```\n\n## Introduction\n\n_respo_ states for resource policy and is tiny, user friendly tool for building RBAC systems based on static `yml` file, mainly with FastAPI framework in mind. In most cases – for even large set of roles – single file would be enough to provide restricting system access.\n\nFeatures:\n\n- It provides custom fields for **SQLAlchemy** and **Django** to store users roles in database.\n\n- Implements R. Sandhu Role-based access control [text](https://profsandhu.com/articles/advcom/adv_comp_rbac.pdf).\n\n- Dead simple, fast and can be trusted – 100% coverage.\n\n- **No issues** with mutlithreading and multiprocessing – you just pass around already prepared, compiled respo_model (from file) in your app that is **readonly**.\n\n- Generates your roles, permissions offline and compile it to pickle file for superfast access in an app.\n\n- Detailed documentation and error messages in CLI command.\n\n- 100% autocompletion and typing support with optional code generation for even better typing support.\n\n---\n\n_Note, every piece of code in the docs is a tested python/yml file, feel free to use it._\n\n## Usage in FastAPI\n\nThe goal is to use simple and reusable dependency factory `user_have_permission("some permission")` that will verify just having `User` database instance if user have access to resoruce. Single endpoint must have single permission for it, and thanks to respo compilation step, every "stronger" permissions and roles would include "weaker" so **we don\'t need to have the if statements everywhere around application**.\n\n```python\nfrom .dependencies import user_have_permission\n\n...\n\n\n@router.get("/users/read_all/")\ndef users_read_all(user = Depends(user_have_permission("users.read_all"))):\n    return user\n\n```\n',
    'author': 'rafsaf',
    'author_email': 'rafal.safin@rafsaf.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rafsaf/respo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
