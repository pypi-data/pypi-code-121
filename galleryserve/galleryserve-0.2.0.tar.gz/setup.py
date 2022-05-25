# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['galleryserve',
 'galleryserve.migrations',
 'galleryserve.south_migrations',
 'galleryserve.templatetags']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0']

setup_kwargs = {
    'name': 'galleryserve',
    'version': '0.2.0',
    'description': 'Adapted from imageserve to fit broader gallery needs such as video embedding and content for controls.',
    'long_description': 'Dependencies:\nPIL\n\nTo install:\npip install galleryserve\n\nAdd \'galleryserve\' to INSTALLED_APPS\n\nConfiguration Options:\nGALLERYSERVE_EXCLUDE_FIELDS - This can be added as a list in your settings.py \nfile to exclude certain fields from appearing in the admin.\n\nTemplate tag example:\n{% load gallerytags %}\n\n{% get_gallery name %}\n{% for slide in gallery %}\n<div title="{{ slide.title }} - {{ slide.credit }}">\n{% if slide.url %}<a href="{{ slide.url }}">{% endif %}\n{% if slide.image %}<img src="{{ slide.image.url }}" alt="{{ slide.alt }}" />{% endif %}\n{% if slide.url %}</a>{% endif %}\n{% if slide.video_url %}<a href="{{ slide.video_url }}">{{ slide.title }}</a>{% endif %}\n{{ slide.title }} - {{ slide.credit }}<br />\n{{ slide.content|safe }}\n</div>\n{% endfor %}\n\n\nChanges in 0.1.5 - 06-27-13\nAllow for gallery title to be passed in as context variable instead of always\ntreating it as a string.\n\nChanges in 0.1.3 - 11-02-12\nMoved to git. Added ANTIALIAS to image processing\n\nChanges in 0.1.2 - 10-22-11\nFail silently on gallery not existing\n\nChanges in 0.1.1 - 9-20-11\nAdded random boolean to control whether gallery item sort should be random\npsql command to insert column:\nalter table galleryserve_gallery ADD column random boolean not null default false;\n',
    'author': 'Imagescape',
    'author_email': 'info@imagescape.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ImaginaryLandscape/django-galleryserve',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
