# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from django.conf.urls import url
from . import views
app_name = 'common'
urlpatterns = [
    url(r'^async_result/(?P<task_id>[\w-]+)/', views.async_result),
]