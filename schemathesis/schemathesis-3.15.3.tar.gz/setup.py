# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['schemathesis',
 'schemathesis.cli',
 'schemathesis.cli.output',
 'schemathesis.extra',
 'schemathesis.fixups',
 'schemathesis.runner',
 'schemathesis.runner.impl',
 'schemathesis.service',
 'schemathesis.specs',
 'schemathesis.specs.graphql',
 'schemathesis.specs.openapi',
 'schemathesis.specs.openapi.expressions',
 'schemathesis.specs.openapi.negative',
 'schemathesis.specs.openapi.stateful']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<7.0',
 'attrs>=19.2,<=21.4',
 'click>=7.0,<9.0',
 'colorama>=0.4,<0.5',
 'curlify>=2.2.1,<3.0.0',
 'hypothesis>=6.13.3,<7.0.0',
 'hypothesis_graphql>=0.9.0,<0.10.0',
 'hypothesis_jsonschema>=0.22.0,<0.23.0',
 'jsonschema>=4.3.2,<5.0.0',
 'junit-xml>=1.9,<2.0',
 'pytest-subtests>=0.2.1,<0.8.0',
 'pytest>4.6.4,<8',
 'requests>=2.22,<2.28.0',
 'starlette>=0.13,<1',
 'tomli-w>=1.0.0,<2.0.0',
 'tomli>=2.0.1,<3.0.0',
 'typing-extensions>=3.7,<5',
 'werkzeug>=0.16.0,<2.2',
 'yarl>=1.5,<2.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=1.1,!=3.8,<5']}

entry_points = \
{'console_scripts': ['schemathesis = schemathesis.cli:schemathesis',
                     'st = schemathesis.cli:schemathesis'],
 'pytest11': ['schemathesis = schemathesis.extra.pytest_plugin']}

setup_kwargs = {
    'name': 'schemathesis',
    'version': '3.15.3',
    'description': 'Property-based testing framework for Open API and GraphQL based apps',
    'long_description': 'Schemathesis\n============\n\n|Build| |Coverage| |Version| |Python versions| |Docs| |Chat| |License|\n\nSchemathesis is a modern API testing tool for web applications built with Open API and GraphQL specifications.\n\nIt reads the application schema and generates test cases, which will ensure that your application is compliant with its schema (read more about how it works in `our research paper <https://arxiv.org/abs/2112.10328>`_).\n\nThe application under test could be written in any language; the only thing you need is a valid API schema in a supported format.\n\nSimple to use and yet powerful to uncover hard-to-find errors thanks to the property-based testing approach backed by state-of-the-art `Hypothesis <http://hypothesis.works/>`_ library.\n\n🚀 Schemathesis is available as a `service <https://schemathesis.io/?utm_source=github>`_, standalone CLI, or a Python library 🚀\n\nThe service enables you to verify your API schema in a few clicks, CLI gives more control.\nSchemathesis.io has a free tier, so you can combine the CLI flexibility with rich visuals by uploading your test results there.\n\n`Signup to reveal all issues on a dashboard <https://app.schemathesis.io/auth/sign-up/?utm_source=oss_readme>`_.\n\nFeatures\n--------\n\n- Content-Type, schema, and status code conformance checks for Open API;\n- Testing of explicit examples from the input schema;\n- Stateful testing via Open API links;\n- Concurrent test execution;\n- Targeted testing;\n- Storing and replaying network requests;\n- Built-in ASGI / WSGI application support;\n- Code samples for easy failure reproduction;\n- Ready-to-go Docker image;\n- Configurable with user-defined checks, string formats, hooks, and targets.\n\nCLI installation\n----------------\n\nTo install Schemathesis via ``pip`` run the following command:\n\n.. code:: bash\n\n    pip install schemathesis\n\nThis command installs the ``schemathesis`` entrypoint + ``st`` as its alias.\n\nYou can also use our Docker image without installing Schemathesis as a Python package.\n\nUsage\n-----\n\nYou can use Schemathesis in the command line directly (``st`` is an alias to ``schemathesis``):\n\n.. code:: bash\n\n  st run --checks all https://example.schemathesis.io/openapi.json\n\nOr via Docker:\n\n.. code:: bash\n\n  docker run schemathesis/schemathesis:stable \\\n      run --checks all https://example.schemathesis.io/openapi.json\n\n.. image:: https://raw.githubusercontent.com/schemathesis/schemathesis/master/img/schemathesis.gif\n\nOr in your Python tests:\n\n.. code:: python\n\n    import schemathesis\n\n    schema = schemathesis.from_uri("https://example.schemathesis.io/openapi.json")\n\n\n    @schema.parametrize()\n    def test_api(case):\n        case.call_and_validate()\n\nCLI is simple to use and requires no coding; the in-code approach gives more flexibility.\n\nBoth examples above will run hundreds of requests against the API under test and report all found failures and inconsistencies along with instructions to reproduce them.\n\n💡 See a complete working example project in the ``/example`` directory. 💡\n\nContributing\n------------\n\nAny contribution to development, testing, or any other area is highly appreciated and useful to the project.\nFor guidance on how to contribute to Schemathesis, see the `contributing guidelines <https://github.com/schemathesis/schemathesis/blob/master/CONTRIBUTING.rst>`_.\n\nSupport this project\n--------------------\n\nHi, my name is Dmitry! I started this project during my work at `Kiwi.com <https://kiwi.com/>`_. I am grateful to them for all the support they\nprovided to this project during its early days and for the opportunity to evolve Schemathesis independently.\n\nIn order to grow the community of contributors and users, and allow me to devote more time to this project, please `donate today <https://github.com/sponsors/Stranger6667>`_.\n\nAlso, I occasionally write posts about Schemathesis in `my blog <https://dygalo.dev/>`_.\n\nLinks\n-----\n\n- **Documentation**: https://schemathesis.readthedocs.io/en/stable/\n- **Releases**: https://pypi.org/project/schemathesis/\n- **Code**: https://github.com/schemathesis/schemathesis\n- **Issue tracker**: https://github.com/schemathesis/schemathesis/issues\n- **Chat**: https://discord.gg/R9ASRAmHnA\n\nAdditional content:\n\n- Research paper: `Deriving Semantics-Aware Fuzzers from Web API Schemas <https://arxiv.org/abs/2112.10328>`_ by **@Zac-HD** and **@Stranger6667**\n- `An article <https://dygalo.dev/blog/schemathesis-property-based-testing-for-api-schemas/>`_ about Schemathesis by **@Stranger6667**\n- `Effective API schemas testing <https://youtu.be/VVLZ25JgjD4>`_ from DevConf.cz by **@Stranger6667**\n- `A video <https://www.youtube.com/watch?v=9FHRwrv-xuQ>`_ from EuroPython 2020 by **@hultner**\n- `Schemathesis tutorial <https://appdev.consulting.redhat.com/tracks/contract-first/automated-testing-with-schemathesis.html>`_  with an accompanying `video <https://www.youtube.com/watch?v=4r7OC-lBKMg>`_ by Red Hat\n- `Using Hypothesis and Schemathesis to Test FastAPI <https://testdriven.io/blog/fastapi-hypothesis/>`_ by **@amalshaji**\n\nNon-English content:\n\n- `A tutorial <https://habr.com/ru/company/oleg-bunin/blog/576496/>`_ (RUS) about Schemathesis by **@Stranger6667**\n\nLicense\n-------\n\nThe code in this project is licensed under `MIT license`_.\nBy contributing to Schemathesis, you agree that your contributions will be licensed under its MIT license.\n\n.. |Build| image:: https://github.com/schemathesis/schemathesis/workflows/build/badge.svg\n   :target: https://github.com/schemathesis/schemathesis/actions\n.. |Coverage| image:: https://codecov.io/gh/schemathesis/schemathesis/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/schemathesis/schemathesis/branch/master\n   :alt: codecov.io status for master branch\n.. |Version| image:: https://img.shields.io/pypi/v/schemathesis.svg\n   :target: https://pypi.org/project/schemathesis/\n.. |Python versions| image:: https://img.shields.io/pypi/pyversions/schemathesis.svg\n   :target: https://pypi.org/project/schemathesis/\n.. |License| image:: https://img.shields.io/pypi/l/schemathesis.svg\n   :target: https://opensource.org/licenses/MIT\n.. |Chat| image:: https://img.shields.io/discord/938139740912369755\n   :target: https://discord.gg/R9ASRAmHnA\n   :alt: Discord\n.. |Docs| image:: https://readthedocs.org/projects/schemathesis/badge/?version=stable\n   :target: https://schemathesis.readthedocs.io/en/stable/?badge=stable\n   :alt: Documentation Status\n\n.. _MIT license: https://opensource.org/licenses/MIT\n',
    'author': 'Dmitry Dygalo',
    'author_email': 'dadygalo@gmail.com',
    'maintainer': 'Dmitry Dygalo',
    'maintainer_email': 'dadygalo@gmail.com',
    'url': 'https://github.com/schemathesis/schemathesis',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
