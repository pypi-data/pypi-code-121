# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_auth_adfs']

package_data = \
{'': ['*'], 'django_auth_adfs': ['templates/django_auth_adfs/*']}

install_requires = \
['PyJWT>=2.4.0,<3.0.0',
 'cryptography>=1.7,<39.0',
 'requests>=1,<3',
 'urllib3>=1.26.0,<2.0.0']

extras_require = \
{':python_version <= "3.7"': ['django>=2.2,<4'],
 ':python_version >= "3.8"': ['django>=2.2,<5']}

setup_kwargs = {
    'name': 'django-auth-adfs',
    'version': '1.9.7',
    'description': 'A Django authentication backend for Microsoft ADFS and AzureAD',
    'long_description': 'ADFS Authentication for Django\n==============================\n\n.. image:: https://readthedocs.org/projects/django-auth-adfs/badge/?version=latest\n    :target: http://django-auth-adfs.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n.. image:: https://img.shields.io/pypi/v/django-auth-adfs.svg\n    :target: https://pypi.python.org/pypi/django-auth-adfs\n.. image:: https://img.shields.io/pypi/pyversions/django-auth-adfs.svg\n    :target: https://pypi.python.org/pypi/django-auth-adfs#downloads\n.. image:: https://img.shields.io/pypi/djversions/django-auth-adfs.svg\n    :target: https://pypi.python.org/pypi/django-auth-adfs\n.. image:: https://codecov.io/github/snok/django-auth-adfs/coverage.svg?branch=master\n    :target: https://codecov.io/github/snok/django-auth-adfs?branch=master\n\nA Django authentication backend for Microsoft ADFS and Azure AD\n\n* Free software: BSD License\n* Homepage: https://github.com/snok/django-auth-adfs\n* Documentation: http://django-auth-adfs.readthedocs.io/\n\nFeatures\n--------\n\n* Integrates Django with Active Directory on Windows 2012 R2, 2016 or Azure AD in the cloud.\n* Provides seamless single sign on (SSO) for your Django project on intranet environments.\n* Auto creates users and adds them to Django groups based on info received from ADFS.\n* Django Rest Framework (DRF) integration: Authenticate against your API with an ADFS access token.\n\nInstallation\n------------\n\nPython package::\n\n    pip install django-auth-adfs\n\nIn your project\'s ``settings.py`` add these settings.\n\n.. code-block:: python\n\n    AUTHENTICATION_BACKENDS = (\n        ...\n        \'django_auth_adfs.backend.AdfsAuthCodeBackend\',\n        ...\n    )\n\n    INSTALLED_APPS = (\n        ...\n        # Needed for the ADFS redirect URI to function\n        \'django_auth_adfs\',\n        ...\n\n    # checkout the documentation for more settings\n    AUTH_ADFS = {\n        "SERVER": "adfs.yourcompany.com",\n        "CLIENT_ID": "your-configured-client-id",\n        "RELYING_PARTY_ID": "your-adfs-RPT-name",\n        # Make sure to read the documentation about the AUDIENCE setting\n        # when you configured the identifier as a URL!\n        "AUDIENCE": "microsoft:identityserver:your-RelyingPartyTrust-identifier",\n        "CA_BUNDLE": "/path/to/ca-bundle.pem",\n        "CLAIM_MAPPING": {"first_name": "given_name",\n                          "last_name": "family_name",\n                          "email": "email"},\n    }\n\n    # Configure django to redirect users to the right URL for login\n    LOGIN_URL = "django_auth_adfs:login"\n    LOGIN_REDIRECT_URL = "/"\n\n    ########################\n    # OPTIONAL SETTINGS\n    ########################\n\n    MIDDLEWARE = (\n        ...\n        # With this you can force a user to login without using\n        # the LoginRequiredMixin on every view class\n        #\n        # You can specify URLs for which login is not enforced by\n        # specifying them in the LOGIN_EXEMPT_URLS setting.\n        \'django_auth_adfs.middleware.LoginRequiredMiddleware\',\n    )\n\nIn your project\'s ``urls.py`` add these paths:\n\n.. code-block:: python\n\n    urlpatterns = [\n        ...\n        path(\'oauth2/\', include(\'django_auth_adfs.urls\')),\n    ]\n\nThis will add these paths to Django:\n\n* ``/oauth2/login`` where users are redirected to, to initiate the login with ADFS.\n* ``/oauth2/login_no_sso`` where users are redirected to, to initiate the login with ADFS but forcing a login screen.\n* ``/oauth2/callback`` where ADFS redirects back to after login. So make sure you set the redirect URI on ADFS to this.\n* ``/oauth2/logout`` which logs out the user from both Django and ADFS.\n\nYou can use them like this in your django templates:\n\n.. code-block:: html\n\n    <a href="{% url \'django_auth_adfs:logout\' %}">Logout</a>\n    <a href="{% url \'django_auth_adfs:login\' %}">Login</a>\n    <a href="{% url \'django_auth_adfs:login-no-sso\' %}">Login (no SSO)</a>\n\nContributing\n------------\nContributions to the code are more then welcome.\nFor more details have a look at the ``CONTRIBUTING.rst`` file.\n',
    'author': 'Joris Beckers',
    'author_email': 'joris.beckers@gmail.com',
    'maintainer': 'Jonas Krüger Svensson',
    'maintainer_email': 'jonas-ks@hotmail.com',
    'url': 'https://github.com/snok/django-auth-adfs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
