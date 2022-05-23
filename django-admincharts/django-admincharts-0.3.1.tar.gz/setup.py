# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['admincharts', 'admincharts.migrations']

package_data = \
{'': ['*'],
 'admincharts': ['static/admincharts/*', 'templates/admin/admincharts/*']}

setup_kwargs = {
    'name': 'django-admincharts',
    'version': '0.3.1',
    'description': 'Chart.js integration for Django admin models',
    'long_description': '# django-admincharts\n\nAdd [Chart.js](https://www.chartjs.org/docs/latest/) visualizations to your Django admin using a mixin class.\n\n## Example\n\n![django-admincharts example](https://user-images.githubusercontent.com/649496/124196798-c3ccee80-da92-11eb-9c2a-c0f94171d071.png)\n\n```python\nfrom django.contrib import admin\n\nfrom .models import BillingAccount\nfrom admincharts.admin import AdminChartMixin\nfrom admincharts.utils import months_between_dates\n\n\n@admin.register(BillingAccount)\nclass BillingAccountAdmin(AdminChartMixin, admin.ModelAdmin):\n    def get_list_chart_data(self, queryset):\n        if not queryset:\n            return {}\n\n        # Cannot reorder the queryset at this point\n        earliest = min([x.ctime for x in queryset])\n\n        labels = []\n        totals = []\n        for b in months_between_dates(earliest, timezone.now()):\n            labels.append(b.strftime("%b %Y"))\n            totals.append(\n                len(\n                    [\n                        x\n                        for x in queryset\n                        if x.ctime.year == b.year and x.ctime.month == b.month\n                    ]\n                )\n            )\n\n        return {\n            "labels": labels,\n            "datasets": [\n                {"label": "New accounts", "data": totals, "backgroundColor": "#79aec8"},\n            ],\n        }\n```\n\n## Installation\n\nInstall from [pypi.org](https://pypi.org/project/django-admincharts/):\n\n```console\n$ pip install django-admincharts\n```\n\nAdd `admincharts` to your Django `INSTALLED_APPS`:\n\n```python\nINSTALLED_APPS = [\n    ...\n    "admincharts",\n]\n```\n\nUse the `AdminChartMixin` with an `admin.ModelAdmin` class to add a chart to the changelist view.\n\nOptions can be set directly on the class:\n\n```python\nfrom django.contrib import admin\nfrom admincharts.admin import AdminChartMixin\n\n@admin.register(MyModel)\nclass MyModelAdmin(AdminChartMixin, admin.ModelAdmin):\n    list_chart_type = "bar"\n    list_chart_data = {}\n    list_chart_options = {"aspectRatio": 6}\n    list_chart_config = None  # Override the combined settings\n```\n\nOr by using the class methods which gives you access to the queryset being used for the current view:\n\n```python\nclass MyModelAdmin(AdminChartMixin, admin.ModelAdmin):\n    def get_list_chart_queryset(self, changelist):\n        ...\n\n    def get_list_chart_type(self, queryset):\n        ...\n\n    def get_list_chart_data(self, queryset):\n        ...\n\n    def get_list_chart_options(self, queryset):\n        ...\n\n    def get_list_chart_config(self, queryset):\n        ...\n```\n\nThe `type`, `data`, and `options` are passed directly to Chart.js to render the chart.\n[Look at the Chart.js docs to see what kinds of settings can be used.](https://www.chartjs.org/docs/latest/configuration/)\n\nBy default, the objects in your chart will be the objects that are currently visible in your list view.\nThis means that admin controls like [search](https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields) and [list filter](https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter) will update your chart,\nand you can use the Django [pagination](https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_per_page) [settings](https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_max_show_all) to control how many objects you want in your chart at a time.\nTo ignore pagination but still respect search/filter,\nyou can override the `get_list_chart_queryset` method to return the full queryset:\n\n```python\nclass MyModelAdmin(AdminChartMixin, admin.ModelAdmin):\n    def get_list_chart_queryset(self, changelist):\n        return changelist.queryset\n```\n\nAnd if you want, you can also sidestep the list queryset entirely by using overriding `get_list_chart_queryset` with your own query:\n\n```python\nclass MyModelAdmin(AdminChartMixin, admin.ModelAdmin):\n    def get_list_chart_queryset(self, changelist):\n        return MyModel.objects.all()\n```\n',
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dropseed/django-admincharts',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
