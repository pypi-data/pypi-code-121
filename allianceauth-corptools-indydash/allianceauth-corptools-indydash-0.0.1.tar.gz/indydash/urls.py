from django.urls import path
from django.urls import re_path

from . import views

from .api import api

app_name = 'indydash'

urlpatterns = [
    re_path(r'^$', views.react_bootstrap, name='view'),
    re_path(r'^api/', api.urls),
]