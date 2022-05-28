# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['better_json_widget']

package_data = \
{'': ['*'],
 'better_json_widget': ['static/better_json_widget/js/lib/*',
                        'templates/better_json_widget/*']}

setup_kwargs = {
    'name': 'django-better-json-widget',
    'version': '0.3.0',
    'description': 'Better JSON Widget for Django Admin',
    'long_description': '# django-better-json-widget\n\n[![Build Status](https://github.com/yakimka/django-better-json-widget/workflows/package/badge.svg?branch=master&event=push)](https://github.com/yakimka/django-better-json-widget/actions?query=workflow%3Apackage)\n[![codecov](https://codecov.io/gh/yakimka/django-better-json-widget/branch/master/graph/badge.svg)](https://codecov.io/gh/yakimka/django-better-json-widget)\n[![pypi](https://img.shields.io/pypi/v/django-better-json-widget.svg)](https://pypi.org/project/django-better-json-widget/)\n[![downloads](https://static.pepy.tech/personalized-badge/django-better-json-widget?period=total&units=none&left_color=grey&right_color=blue&left_text=downloads)](https://pepy.tech/project/django-better-json-widget)\n\nBetter JSON Widget for Django Admin\n\n![](contrib/demo.gif)\n\n## Features\n\n- Better Json widget with schema for your Django Admin site\n- Can watch for changes in the given field (`follow_field`) and dynamically update the JSON schema\n- Supports [JSON Schema](https://json-schema.org/)\n- You can edit generated UI fields specified in schema or edit raw JSON\n- Use Vue.js for UI\n- Supports Python 3.8+ and Django 3.2+\n\n## Limitations\n\n- Supports only a small subset of the JSON Schema (integer, number, boolean, string types)\n- Does not support enum, list types (yet) and nested objects (not planned)\n\nSo, PR\'s are welcome!\n\n## Installation\n \nInstall package \n\n```bash\npip install django-better-json-widget\n```\n\nAdd `better_json_widget` to your `INSTALLED_APPS`\n\n## Example\n\n```python\nfrom better_json_widget.widgets import BetterJsonWidget\nfrom django.contrib import admin\nfrom django.forms import ModelForm\n\nfrom .models import TestModel\n\n\nschema_mapping = {\n    "animal": {\n        "$schema": "https://json-schema.org/draft/2020-12/schema",\n        "type": "object",\n        "properties": {\n            "limbs": {\n                "type": "integer",\n                "title": "Number of limbs",\n                "description": "How many limbs does the animal have?",\n            },\n            "color": {"type": "string", "title": "Color"},\n            "herbivore": {\n                "type": "boolean",\n                "title": "Is it herbivore?",\n                "default": True,\n            },\n        },\n        "required": ["limbs", "herbivore"],\n    },\n    "superhero": {\n        "$schema": "https://json-schema.org/draft/2020-12/schema",\n        "type": "object",\n        "properties": {\n            "name": {\n                "type": "string",\n                "title": "Name",\n                "description": "Give a name to your superhero",\n            },\n            "superpower": {"type": "string"},\n        },\n        "required": ["name"],\n    },\n}\n\nclass TestModelAdminForm(ModelForm):\n    class Meta:\n        model = TestModel\n        fields = "__all__"\n        widgets = {\n            "options": BetterJsonWidget(\n                follow_field="type",\n                # `schema_mapping` and `schema` can be callables\n                schema_mapping=schema_mapping,\n            ),\n        }\n\n\n@admin.register(TestModel)\nclass TestModelAdmin(admin.ModelAdmin):\n    form = TestModelAdminForm\n    fields = [\n        "type",\n        "options",  # JsonField\n    ]\n```\n\nAlso, if you don\'t need to dynamically change schema, you can use `schema` option:\n\n```python\nBetterJsonWidget(\n    schema={\n        "$schema": "https://json-schema.org/draft/2020-12/schema",\n        "type": "object",\n        "properties": {\n            ...\n        },\n        "required": [],\n    },\n)\n```\n\n## Settings\n\nIf for some reason you don\'t want to use bundled Vue.js, you can change `BETTER_JSON_WIDGET_VUE_URL` settings:\n\n```python\nBETTER_JSON_WIDGET_VUE_URL = "https://unpkg.com/vue@3"\n```\n\nIf you set this setting to `None`, then bundled Vue.js will not be used.\n\n## TODO\n\n- Improve JSON Schema support\n- Show current field value in UI\n- UI tests\n\n## License\n\n[MIT](https://github.com/yakimka/django-better-json-widget/blob/master/LICENSE)\n\n## Credits\n\nThis project was generated with [`yakimka/cookiecutter-pyproject`](https://github.com/yakimka/cookiecutter-pyproject).\n',
    'author': 'yakimka',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yakimka/django-better-json-widget',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
