# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['giant_news', 'giant_news.migrations', 'giant_news.models', 'giant_news.tests']

package_data = \
{'': ['*'],
 'giant_news': ['templates/*',
                'templates/news/*',
                'templates/plugins/related_articles/*']}

install_requires = \
['django-filer', 'giant-mixins', 'swapper>=1.3.0,<2.0.0']

setup_kwargs = {
    'name': 'giant-news',
    'version': '1.0.0b3',
    'description': 'A small reusable package that adds a News app to a project',
    'long_description': '# Giant News\n\nA re-usable package which can be used in any project that requires a generic `News` app.\n\nThis will include the basic formatting and functionality such as model creation via the admin.\n\nSupported Django versions:\n\n- Django 2.2, 3.2\n\nSupported django CMS versions:\n\n- django CMS 3.8, 3.9\n\n> &#x26a0;&#xfe0f; For Django 2.x, use giant-news 0.x\n\n> &#x26a0;&#xfe0f; Release 1.0.0-alpha.1 and above are NOT compatible with\n> versions < 1 due to model name changes and a migration reset. Only upgrade to\n> this version if you are aware of what changes need to be made\n\n## Installation and Configuration\n\nTo install with the package manager, run:\n\n    $ poetry add giant-news\n\nYou should then add `"giant_news", "easy_thumbnails" and "filer"` to the `INSTALLED_APPS` in your settings file.\nThe detail pages in this app use plugins which are not contained within this app. It is recommended that you include a set of plugins in your project, or use the `giant-plugins` app.\n\nIt is highly recommended that you override the base Article model at the start\nof a project, even if you have no intention of immediately changing any fields.\nChanging from a non-swappable model to a swappable model is difficult and will require migration\nhacking.\n\n```\n# models.py\n\nfrom giant_news.models import AbstractArticle\n\n\nclass Article(AbstractArticle):\n    pass\n\n\n# in admin.py\n\nfrom django.contrib import admin\nfrom giant_news.admin import ArticleAdmin\nfrom .models import Article\n\n\nadmin.site.register(Article, ArticleAdmin)\n\n```\n\nWhen the migrations are created for this new model it will need some tweaking as\nDjango will not set this up to use swapper. To do this add the following lines to\nthe initial migration file (this will replace the hardcoded dependency on the\n0002 migration from giant_news)\n\n```\nimport swapper\n\nclass Migration...\n\n    dependencies = [\n        ...\n        (\'giant_news\', \'0001_initial\'),\n        swapper.dependency("giant_news", "Article"),\n    ]\n```\nWe also need to tell it run this migration before any other migration inside the\ngiant_news library as the model needs to be "swapped" before any relations are\ncreated. You can do this with another line just under the `dependencies` list.\n\n```\n    run_before = [\n        (\'giant_news\', \'0002_relatedarticlecardplugin_relatedarticleplugin\'),\n    ]\n```\nOnce you have created a model, and only AFTER you run migrations, you\'ll need to\npoint swapper to this new model. You can do this with the following setting:\n\n    GIANT_NEWS_ARTICLE_MODEL = "appname.Article"\n\n\n\n## Sitemap\n\nIn order to add published articles to your sitemap, import the sitemaps file and add it to your `sitemaps` dict. This is usually contained within the main `urls.py` file.\n\n## URLs\n\nIt is recommended that the application be added to a CMS page via the apphook. However, if you wish to hardcode the URL, you can do so by adding the following to your main `urls.py` file:\n\n```\n\n    path("news/", include("giant_news.urls"), name="news"),\n```\n\nIf you want to customize the urls to include a different path and/or templates, first you must import `from giant_news import views as news_views` in `core.urls` and then you could add the following:\n\n    path("news/", news_views.ArticleIndex.as_view(template_name="news/index.html"), name="index"),\n    path("news/<slug:slug>/", news_views.ArticleDetail.as_view(template_name="news/detail.html"), name="detail"),\n\n# Local development\n\n## Getting setup\n\nTo get started with local development of this library, you will need access to poetry (or another venv manager). You can set up a virtual environment with poetry by running:\n\n    $ poetry shell\n\nNote: You can update which version of python poetry will use for the virtualenv by using:\n\n    $ poetry env use 3.x\n\nand install all the required dependencies (seen in the pyproject.toml file) with:\n\n    $ poetry install\n\n\n## Management commands\n\nAs the library does not come with a `manage.py` file we need to use `django-admin` instead. However, we will need to set our `DJANGO_SETTINGS_MODULE` file in the environment. You can do this with:  \n\n    $ export DJANGO_SETTINGS_MODULE=settings\n\nFrom here you can run all the standard Django management commands such as `django-admin makemigrations`.\n\n## Testing\n\nThis library uses Pytest in order to run its tests. You can do this (inside the shell) by running:\n\n    $ pytest -v\n\nwhere `-v` is to run in verbose mode which, while not necessary, will show which tests errored/failed/passed a bit more clearly. \n\n## Preparing for release\n\nIn order to prep the package for a new release on TestPyPi and PyPi there is one key thing that you need to do. You need to update the version number in the `pyproject.toml`.\nThis is so that the package can be published without running into version number conflicts. The version numbering must also follow the Semantic Version rules which can be found here https://semver.org/.\n\n## Publishing\n\nPublishing a package with poetry is incredibly easy. Once you have checked that the version number has been updated (not the same as a previous version) then you only need to run two commands.\n\n    $ `poetry build`\n\nwill package the project up for you into a way that can be published.\n\n    $ `poetry publish`\n\nwill publish the package to PyPi. You will need to enter the company username (Giant-Digital) and password for the account which can be found in the company password manager\n',
    'author': 'Will-Hoey',
    'author_email': 'will.hoey@giantdigital.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/giantmade/giant-news',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
