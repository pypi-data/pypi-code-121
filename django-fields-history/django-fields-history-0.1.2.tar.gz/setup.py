# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fields_history',
 'fields_history.postgres',
 'fields_history.postgres.migrations']

package_data = \
{'': ['*']}

install_requires = \
['addict>=2.2.1,<3.0.0', 'toml>=0.9,<0.10']

setup_kwargs = {
    'name': 'django-fields-history',
    'version': '0.1.2',
    'description': 'Store model fields history',
    'long_description': '# django-fields-history\n\n[![PyPI version](https://badge.fury.io/py/django-fields-history.svg)](https://badge.fury.io/py/django-fields-history)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nA Django app that track history changes in model fields.\n\n__Important note__: currently only one implementation of `FieldsHistory`\nis supported and it\'s with `django.contrib.postgres.fields.JSONField`\nwhich is [`JSONB`](https://www.postgresql.org/docs/9.4/datatype-json.html)\nunder the hood. So only _postgresql_ as database is supported\n\nSimilar projects:\n\n * [django-reversion](https://github.com/etianen/django-reversion)\n * [django-simple-history](https://github.com/treyhunner/django-simple-history)\n * [django-field-history](https://github.com/grantmcconnaughey/django-field-history)\n\nMain difference that those libraries keep track of changes, and this library\ntracks the history change.\n\nSimple explanation:\n\n```python\nfrom field_history.trackers import FieldsHistoryTracker\n\nclass SimpleModel(models.Model):\n    field = models.CharField(max_length=50)\n\n    field_history = FieldsHistoryTracker(fields=[\'field\'])\n\nobj = SimpleModel.objects.create(field=\'value\')\nassert not obj.get_field_history()\n\n\nobj.field = "new_value"\nobj.save()\nassert obj.get_field_history()\nassert obj.get_field_history()[0].value == "value"\n```\n\n\n## QuickStart\n\nInstall `django-fields-history`:\n\n```bash\npip install django-fields-history\n```\n\nAdd `fields_history.postgres` to `INSTALLED_APPS` (currently only\npostgres implementation is supported):\n\n```python\nINSTALLED_APPS = [\n    # rest of apps\n    "fields_history.postgres",\n]\n```\n\nAnd add trackers to your models and specify fields to track:\n\n```python\nfrom field_history.trackers import FieldsHistoryTracker\n\nclass YourModel(models.Model):\n    ...\n\n    history_tracker = FieldsHistoryTracker(fields=["field1", "field2"])\n```\n\nAnd you are done.\n\n\n## Implementation\n\nEvery change of your fields field changes be tracked in\n`fields_history.models.FieldsHistory` in:\n\n * `fields_history.postgres` - `JSONB` postgres field\n\nOne object per save if tracked fields has been changed.\n\n\n## Credits\n\nBasically this project is implemented based on\n[django-field-history](https://github.com/grantmcconnaughey/django-field-history)\nwhich itself used [django-model-utils](https://github.com/jazzband/django-model-utils).\n',
    'author': 'Alex Shalynin',
    'author_email': 'a.shalynin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vishes-shell/django-fields-history',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
