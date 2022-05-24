# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aftership']

package_data = \
{'': ['*']}

modules = \
['CHANGELOG', 'README', 'LICENSE']
install_requires = \
['requests']

setup_kwargs = {
    'name': 'aftership',
    'version': '1.4.0',
    'description': 'The python SDK of AfterShip API',
    'long_description': "====================\naftership-sdk-python\n====================\n\n.. image:: https://github.com/aftership/aftership-sdk-python/actions/workflows/test.yml/badge.svg?branch=master\n    :target: https://github.com/AfterShip/aftership-sdk-python/actions/workflows/test.yml?query=branch%3Amaster\n\n.. image:: https://coveralls.io/repos/github/AfterShip/aftership-sdk-python/badge.svg?branch=master\n    :target: https://coveralls.io/github/AfterShip/aftership-sdk-python?branch=master\n\n\naftership-sdk-python is Python SDK (module) for `AfterShip API <https://www.aftership.com/docs/api/4>`_.\nModule provides clean way to access API endpoints.\n\nIMPORTANT NOTE\n--------------\n\nCurrent version of aftership-sdk-python `>=0.3` not **compatible** with\nprevious version of sdk `<=0.2`.\n\nAlso, version since 1.0 is **not** support Python 2.X anymore. If you want\nto use this SDK under Python 2.X, please use versions `<1.0`.\n\n\nSupported Python Versions\n=========================\n\n- 3.6\n- 3.7\n- 3.8\n- 3.9\n- 3.10\n- pypy3\n\nInstallation\n------------\n\nVia pip\n=======\n\nUse Virtual Environment\n=======================\nWe recommend using a `virtualenv <https://docs.python.org/3/library/venv.html>`_ or `poem <https://python-poetry.org/>`_\nto use this SDK.\n\n.. code-block:: bash\n\n    $ pip install aftership\n\nVia source code\n===============\n\nDownload the code archive, without unzip it, go to the\nsource root directory, then run:\n\n.. code-block:: bash\n\n    $ pip install aftership-sdk-python.zip\n\nUsage\n-----\n\nYou need a valid API key to use this SDK. If you don't have one, please visit https://www.aftership.com/apps/api.\n\nQuick Start\n===========\n\nThe following code gets list of supported couriers\n\n.. code-block:: python\n\n    import aftership\n    aftership.api_key = 'YOUR_API_KEY_FROM_AFTERSHIP'\n    couriers = aftership.courier.list_couriers()\n\nYou can also set API key via setting :code:`AFTERSHIP_API_KEY` environment varaible.\n\n.. code-block:: bash\n\n    export AFTERSHIP_API_KEY=THIS_IS_MY_API_KEY\n\n.. code-block:: python\n\n    import aftership\n    tracking = aftership.get_tracking(tracking_id='your_tracking_id')\n\nThe functions of the SDK will return `data` field value if the API endpoints\nreturn response with HTTP status :code:`2XX`, otherwise will throw an\nexception.\n\nExceptions\n==========\n\n\nExceptions are mapped from https://docs.aftership.com/api/4/errors,\nand this table is the exception attributes mapping.\n\n+------------------+----------------------+\n| API error        | AfterShipError       |\n+==================+======================+\n| http status code | :code:`http_status`  |\n+------------------+----------------------+\n| :code:`meta.code`| :code:`code`         |\n+------------------+----------------------+\n| :code:`meta.type`| :code:`message`      |\n+------------------+----------------------+\n\n\nKeyword arguments\n=================\n\nMost of SDK functions only accept keyword arguments.\n\n\nExamples\n========\n\nGoto `examples <examples>`_ to see more examples.\n",
    'author': 'AfterShip',
    'author_email': 'support@aftership.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://developers.aftership.com',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
