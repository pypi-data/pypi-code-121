from django.conf.urls.defaults import patterns, url

from views import *

urlpatterns = patterns(
    '',
    url(r'^$', nodes, name='nodes'),
    url(r'^config/$', config, name='config'),
    url(r'^-/edit/$', node_edit, name='node_edit'),
    url(r'^([^\/]+)/edit/$', node_edit, name='node_edit'),
    url(r'^([^\/]+)/$', node, name='node'),
    url(r'^([^\/]+)/actions/$', node_actions, name='node_actions'),
)
