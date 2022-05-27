# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['RPA', 'RPA.Cloud.Google', 'RPA.Cloud.Google.keywords', 'RPA.scripts']

package_data = \
{'': ['*']}

install_requires = \
['google-api-python-client>=2.2.0,<3.0.0',
 'google-auth-httplib2>=0.1.0,<0.2.0',
 'google-auth-oauthlib>=0.4.4,<0.5.0',
 'google-cloud-language>=2.0.0,<3.0.0',
 'google-cloud-speech>=2.3.0,<3.0.0',
 'google-cloud-storage>=1.37.1,<2.0.0',
 'google-cloud-texttospeech>=2.3.0,<3.0.0',
 'google-cloud-translate>=3.1.0,<4.0.0',
 'google-cloud-videointelligence>=2.1.0,<3.0.0',
 'google-cloud-vision>=2.3.1,<3.0.0',
 'grpcio>=1.37.0,<2.0.0',
 'robotframework-pythonlibcore>=3.0.0,<4.0.0',
 'robotframework>=4.0.0,!=4.0.1,<6.0.0',
 'rpaframework-core>=9.0.0,<10.0.0']

entry_points = \
{'console_scripts': ['rpa-google-oauth = RPA.scripts.google_authenticate:main']}

setup_kwargs = {
    'name': 'rpaframework-google',
    'version': '5.0.0',
    'description': 'Google library for RPA Framework',
    'long_description': 'rpaframework-google\n===================\n\nThis library enables Google Cloud services for `RPA Framework`_\nlibraries, such as Google Sheets and Google Vision.\n\n.. _RPA Framework: https://rpaframework.org\n',
    'author': 'RPA Framework',
    'author_email': 'rpafw@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rpaframework.org/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
