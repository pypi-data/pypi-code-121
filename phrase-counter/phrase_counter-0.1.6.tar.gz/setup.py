# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['phrase_counter']

package_data = \
{'': ['*'], 'phrase_counter': ['static/*']}

install_requires = \
['PyICU>=2.8.1,<3.0.0',
 'beautifulsoup4',
 'cleaning-utils>=0.1.5,<0.2.0',
 'pandas',
 'polyglot',
 'pycld2>=0.41,<0.42',
 'requests',
 'scikit-learn']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=4.5.0,<5.0.0']}

setup_kwargs = {
    'name': 'phrase-counter',
    'version': '0.1.6',
    'description': 'Counting stop words.',
    'long_description': '# Common Phrase Detection\n[![coverage report](assets/images/coverage.svg)](.logs/coverage.txt)\n[![static analysis](assets/images/mypy.svg)](.logs/mypy.txt)\n[![lint report](assets/images/pylint.svg)](.logs/pylint-log.txt)\n[![maintainability](assets/images/maintainability.svg)](.logs/maintainability.txt)\n[![complexity](assets/images/complexity.svg)](.logs/complexity.txt)\n[![Code style: black](assets/images/codestyle.svg)](https://github.com/psf/black)\n[![Pre-commit](assets/images/precommits.svg)](.pre-commit-config.yaml)\n[![license](assets/images/licence.svg)](https://github.com/rezashabrang/common-phrase-detection)\n\nThis is an API python library which is developed for detecting stop phrases.\n\n\n## Table of Contents\n\n- [Background](#background)\n- [Install](#install)\n- [API](#api)\n- [Maintainers](#maintainers)\n\n## Background\nNLP (Natural Language Processing) techniques is very helpful in various applications such as sentiment analysis, chatbots and other areas. For developing NLP models a need for a large & clean corpus for learning words relations is indisputable. One of the challanges in achieving a clean corpus is stop phrases. Stop phrases usually does not contain much information about the text and so must be identified and removed from the text.\n<br>\nThis is the aim of this repo to provide a structure for processing HTML pages (which are a valuable source of text for all languages) and finding a certain number of possible combinations of words and using human input for identifying stop phrases.\n\n## Install\n\n1. Make sure you have `docker`,`docker-compose` and `python 3.8` and above installed.\n\n2. create a `.env` file with desired values based on `.env.example` file.\n\n3. After cloning the project, go to the project directory and run below command.\n```bash\ndocker-compose -f docker-compose-dev.yml build\n```\n\n4. After the images are built successfully, run below command for starting the project.\n```bash\ndocker-compose -f docker-compose-dev.yml up -d\n```\n\n5. We need to create a database and collection in mongo in order to use the API. First run mongo bash.\n```\ndocker exec -it db bash\n```\n6. Authenticate in mongo container.\n```\nmongo -u ${MONGO_INITDB_ROOT_USERNAME} -p ${MONGO_INITDB_ROOT_PASSWORD} -- authenticationDatabase admin\n```\n7. Create the database and collection based on `MONGO_PHRASE_DB` and `MONGO_PHRASE_COL` names you provided in step `2`.\n```\nuse phrasedb;  # Database creation\ndb.createCollection("common_phrase");  # Collection creation\n```\n8. Now you\'re ready yo use the API section.\n\n## API\n\nThis API has three endpoints. <br>\n\n### Document Process\n\nHere you can pass a HTML text in request body to process it.\n\nThe process stages are:\n\n* Fetching all H1-H6 and p tags\n\n* Cleaning text\n* Finding bags (from 1 to 5 bags of word)\n* Counting the number of occurences in text\n* Integrating results in database\n(Updating count field of the phrase if already exists, otherwise inserting a\nnew record)\n\n### Status Updater\n\nUpdates statuses. <br>\n\nChanging the status of a phrase to either **stop** or **highlight**.\n\n### Data Fetcher\n\nFetching data from database based on the statuses.\nHere you can fetch phrases based on 4 different situation for statuses:\n\n* Stop phrases\n\n* Highlight phrases\n\n* Phrases that have status (either stop or highlight)\n\n* Phrases which statuses are not yet determined\n\n### API details\n\n* API Base URL\n```\n127.0.0.1:8000\n```\n* API Swagger UI\n```\n127.0.0.1:8000/docs\n```\nFor futher details and how to make request to each endpoint refer to the swagger of the API.\n\n## Maintainers\n[Maani Beygi](https://github.com/MaaniBeigy)<br>\n[Reza Shabrang](https://github.com/rezashabrang)\n',
    'author': 'aasaam',
    'author_email': 'rezashabrang.m@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rezashabrang/stop-word-counter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
