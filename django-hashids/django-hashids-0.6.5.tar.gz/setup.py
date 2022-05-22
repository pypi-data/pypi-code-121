# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_hashids']

package_data = \
{'': ['*']}

install_requires = \
['hashids>=1.0.2']

setup_kwargs = {
    'name': 'django-hashids',
    'version': '0.6.5',
    'description': 'Non-intrusive hashids library for Django',
    'long_description': '# Django Hashids\n[![Github Actions](https://github.com/ericls/django-hashids/workflows/test/badge.svg)](https://github.com/ericls/django-hashids/actions)\n[![Code Coverage](https://codecov.io/gh/ericls/django-hashids/branch/master/graph/badge.svg)](https://codecov.io/gh/ericls/django-hashids)\n[![Python Version](https://img.shields.io/pypi/pyversions/django-hashids.svg)](https://pypi.org/project/django-hashids/)\n[![PyPI Package](https://img.shields.io/pypi/v/django-hashids.svg)](https://pypi.org/project/django-hashids/)\n[![License](https://img.shields.io/pypi/l/django-hashids.svg)](https://github.com/ericls/django-hashids/blob/master/LICENSE)\n\ndjango-hashids is a simple and non-intrusive hashids library for Django. It acts as a model field, but it does not touch the database or change the model.\n\n# Features\n- Proxy the internal model `pk` field without storing the value in the database.\n- Allows lookups and filtering by hashid string.\n- Can be used as sort key\n- Allows specifying a salt, min_length and alphabet globally\n- Supports custom salt, min_length, and alphabet per field\n- Supports Django REST Framework Serializers\n- Supports exact ID searches in Django Admin when field is specified in search_fields.\n- Supports common filtering lookups, such as __iexact, __contains, __icontains, though matching is the same as __exact.\n- Supports other lookups: isnull, gt, gte, lt and lte.\n\n# Install\n\n```bash\npip install django-hashids\n```\n\n`django-hashids` is tested with Django 1.11, 2.2, 3.0, 3.1, 3.2, 4.0 and python 3.6, 3.7, 3.8, 3.9, 3.10.\n\n# Usage\n\nAdd `HashidsField` to any model\n\n```python\nfrom django_hashids import HashidsField\n\nclass TestModel(Model):\n    hashid = HashidsField(real_field_name="id")\n```\n\n`TestModel.hashid` field will proxy `TestModel.id` field but all queries will return and receive hashids strings. `TestModel.id` will work as before.\n\n## Examples\n\n```python\ninstance = TestModel.objects.create()\ninstance2 = TestModel.objects.create()\ninstance.id  # 1\ninstance2.id  # 2\n\n# Allows access to the field\ninstance.hashid  # \'1Z\'\ninstance2.hashid  # \'4x\'\n\n# Allows querying by the field\nTestModel.objects.get(hashid="1Z")\nTestModel.objects.filter(hashid="1Z")\nTestModel.objects.filter(hashid__in=["1Z", "4x"])\nTestModel.objects.filter(hashid__gt="1Z")  # same as id__gt=1, would return instance 2\n\n# Allows usage in queryset.values\nTestModel.objects.values_list("hashid", flat=True) # ["1Z", "4x"]\nTestModel.objects.filter(hashid__in=TestModel.objects.values("hashid"))\n\n```\n\n## Config\n\nThe folloing attributes can be added in settings file to set default arguments of `HashidsField`:\n1. `DJANGO_HASHIDS_SALT`: default salt\n2. `DJANGO_HASHIDS_MIN_LENGTH`: default minimum length\n3. `DJANGO_HASHIDS_ALPHABET`: default alphabet\n\n`HashidsField` does not reqiure any arguments but the followinig arguments can be supplied to modify its behavior.\n\n| Name               |                        Description                        |\n| ------------------ | :-------------------------------------------------------: |\n| `real_field_name`  |                  The proxied field name                   |\n| `hashids_instance` | The hashids instance used to encode/decode for this field |\n| `salt`             |     The salt used for this field to generate hashids      |\n| `min_length`       |  The minimum length of hashids generated for this field   |\n| `alphabet`         |    The alphabet used by this field to generate hashids    |\n\nThe argument `hashids_instance` is mutually exclusive to `salt`, `min_length` and `alphabet`. See [hashids-python](https://github.com/davidaurelio/hashids-python) for more info about the arguments.\n\nSome common Model arguments such as `verbose_name` are also supported.\n',
    'author': 'Shen Li',
    'author_email': 'dustet@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4',
}


setup(**setup_kwargs)
