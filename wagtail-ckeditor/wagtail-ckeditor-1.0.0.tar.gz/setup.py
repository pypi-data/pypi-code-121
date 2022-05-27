# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wagtail_ckeditor']

package_data = \
{'': ['*'], 'wagtail_ckeditor': ['static/wagtail_ckeditor/*']}

install_requires = \
['Django>=3.1.5,<4.0.0', 'wagtail>=2.11.2,<3.0.0']

setup_kwargs = {
    'name': 'wagtail-ckeditor',
    'version': '1.0.0',
    'description': 'Rich-text editor for Django Wagtail CMS',
    'long_description': '# Wagtail CKEditor plugin\n\nThis is a [Wagtail](https://wagtail.io/) plugin, which allows [CKEditor](http://ckeditor.com/) to be used as an internal editor\ninstead of hallo.js or draftail.\n\n## Requirments\n\nWagtail 2+\nDjango 3+\n\n## How to install\n\nInclude `wagtail_ckeditor` in your `INSTALLED_APPS`.\n\nEnsure that you have this entry in your `settings.py` file.\n\n\n    WAGTAILADMIN_RICH_TEXT_EDITORS = {\n        \'default\': {\n            \'WIDGET\': \'wagtail_ckeditor.widgets.CKEditor\'\n        }\n    }\n\nThere are several options you can add to your `settings.py` file.\n\nTo add new fonts and font-weight, font-size, line-height values use settings file.\nExample\n```\nWAGTAIL_CKEDITOR_FONTS = "Inter;Golos;"\nWAGTAIL_CKEDITOR_FONT_SIZES = "96/96px; 128/128px;"\nWAGTAIL_CKEDITOR_LINE_HEIGHT = "32px;36px;"\nWAGTAIL_CKEDITOR_SKIN = "moono-lisa"\nWAGTAIL_CKEDITOR_FONT_WEIGHT = "965;970;"\n```\n  \n  Inspired by:\n\n---\n\nRichard Mitchell (https://github.com/isotoma/wagtailtinymce.git)\nmastnym (https://github.com/mastnym/wagtail-ckeditor)\n',
    'author': 'penkhasoveg',
    'author_email': 'pen.egor2002@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ghettoDdOS/pve-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
