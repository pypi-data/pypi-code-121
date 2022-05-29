# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fittrackee',
 'fittrackee.application',
 'fittrackee.cli',
 'fittrackee.emails',
 'fittrackee.migrations',
 'fittrackee.migrations.versions',
 'fittrackee.users',
 'fittrackee.users.utils',
 'fittrackee.workouts',
 'fittrackee.workouts.utils']

package_data = \
{'': ['*'],
 'fittrackee': ['dist/*',
                'dist/img/*',
                'dist/img/icons/*',
                'dist/img/weather/*',
                'dist/img/workouts/*',
                'dist/static/css/*',
                'dist/static/fonts/*',
                'dist/static/img/*',
                'dist/static/js/*'],
 'fittrackee.emails': ['templates/*',
                       'templates/account_confirmation/en/*',
                       'templates/account_confirmation/fr/*',
                       'templates/email_update_to_current_email/en/*',
                       'templates/email_update_to_current_email/fr/*',
                       'templates/email_update_to_new_email/en/*',
                       'templates/email_update_to_new_email/fr/*',
                       'templates/password_change/en/*',
                       'templates/password_change/fr/*',
                       'templates/password_reset_request/en/*',
                       'templates/password_reset_request/fr/*']}

install_requires = \
['SQLAlchemy==1.4.36',
 'dramatiq[redis]>=1.13,<2.0',
 'flask-bcrypt>=1.0,<2.0',
 'flask-dramatiq>=0.6.0,<0.7.0',
 'flask-migrate>=3.1,<4.0',
 'flask>=2.1,<3.0',
 'gpxpy==1.3.4',
 'gunicorn>=20.1,<21.0',
 'humanize>=4.1,<5.0',
 'psycopg2-binary>=2.9,<3.0',
 'pyOpenSSL>=22.0,<23.0',
 'pyjwt>=2.4,<3.0',
 'python-forecastio>=1.4,<2.0',
 'pytz>=2022.1,<2023.0',
 'shortuuid>=1.0.9,<2.0.0',
 'staticmap>=0.5.4,<0.6.0',
 'ua-parser>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['fittrackee = fittrackee.__main__:main',
                     'fittrackee_set_admin = fittrackee.__main__:set_admin',
                     'fittrackee_upgrade_db = fittrackee.__main__:upgrade_db',
                     'fittrackee_worker = flask_dramatiq:worker',
                     'ftcli = fittrackee.cli:cli']}

setup_kwargs = {
    'name': 'fittrackee',
    'version': '0.6.6',
    'description': 'Self-hosted outdoor workout/activity tracker',
    'long_description': '# FitTrackee\n**A simple self-hosted workout/activity tracker.**  \n\n[![PyPI version](https://img.shields.io/pypi/v/fittrackee.svg)](https://pypi.org/project/fittrackee/) \n[![Python Version](https://img.shields.io/badge/python-3.7+-brightgreen.svg)](https://python.org)\n[![Flask Version](https://img.shields.io/badge/flask-2.1-brightgreen.svg)](http://flask.pocoo.org/) \n[![code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black) \n[![type check: mypy](https://img.shields.io/badge/type%20check-mypy-blue)](http://mypy-lang.org/)  \n[![Vue Version](https://img.shields.io/badge/vue-3.2-brightgreen.svg)](https://v3.vuejs.org/) \n[![Typescript Version](https://img.shields.io/npm/types/typescript)](https://www.typescriptlang.org/) \n[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)  \n[![pipeline status](https://github.com/SamR1/FitTrackee/actions/workflows/.tests-python.yml/badge.svg)](https://github.com/SamR1/FitTrackee/actions/workflows/.tests-python.yml)\n[![pipeline status](https://github.com/SamR1/FitTrackee/actions/workflows/.tests-javascript.yml/badge.svg)](https://github.com/SamR1/FitTrackee/actions/workflows/.tests-javascript.yml)\n\n\n---\n\nThis web application allows you to track your outdoor activities (workouts) from gpx files and keep your data on your own server.  \nNo mobile app is developed yet, but several existing mobile apps can store workouts data locally and export them into a gpx file.  \nExamples for Android (non-exhaustive list):  \n* [Runner Up](https://github.com/jonasoreland/runnerup) (GPL v3)  \n* [ForRunners](https://gitlab.com/brvier/ForRunners) (GPL v3)  \n* [OpenTracks](https://github.com/OpenTracksApp/OpenTracks) (Apache License)  \n* [FitoTrack](https://codeberg.org/jannis/FitoTrack) (GPL v3)  \n\nMaps are displayed using [Open Street Map](https://www.openstreetmap.org).  \nIt is also possible to add a workout without a gpx file.\n\n**Still under heavy development (some features may be unstable).**  \n(see [issues](https://github.com/SamR1/FitTrackee/issues) and [documentation](https://samr1.github.io/FitTrackee) for more information)  \n\n![FitTrackee Dashboard Screenshot](https://samr1.github.io/FitTrackee/_images/fittrackee_screenshot-01.png)\n',
    'author': 'SamR1',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SamR1/FitTrackee',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
