from django.urls import re_path
from wagtail.core import hooks

from .views import chooser_page_data

@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        re_path(r'^choose-page/data/(\d+)/$', chooser_page_data, name='wagtailadmin_choose_page_data')
    ]