from __future__ import unicode_literals

from django.urls import re_path

from .views import Register, Done, OptOut, OptOutDone

urlpatterns = [
    re_path(r'^done/$', Done.as_view(), name='done'),
    re_path(r'^register/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]+)/$',
        Register.as_view(), name='register'),
    re_path(r'^optout/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]+)/$',
        OptOut.as_view(), name='opt-out'),
    re_path(r'^optout/done/$',
        OptOutDone.as_view(), name='opt-out-done'),
]
"""
.. attribute:: ^done/$

    :name: done

.. attribute:: ^register/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]+)/$

    :name: register

.. attribute:: ^optout/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]+)/$

    :name: opt-out

.. attribute:: ^optout/done/$

    :name: opt-out-done
"""
