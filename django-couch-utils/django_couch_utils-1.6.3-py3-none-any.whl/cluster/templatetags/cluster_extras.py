# -*- coding: utf-8 -*-

import urlparse
from datetime import datetime

from django import template

register = template.Library()


@register.filter
def hide_url_password(value):
    u = urlparse.urlparse(value)
    if u.hostname:
        # do something only if url is really URL
        if u.username:
            value_format = '%(scheme)s://%(username)s:%(password)s@%(hostname)s%(path)s'
        else:
            value_format = '%(scheme)s://%(hostname)s%(path)s'

        if u.params:
            value_format += '?%(query)s'

        if u.fragment:
            value_format += '#%(fragment)s'


        value = value_format % {
            'scheme': u.scheme,
            'username': u.username,
            'password': '*' * 8,
            'hostname': u.hostname,
            'path': u.path,
            'query': u.query,
            'fragment': u.fragment,
        }
        
    
    return value


@register.filter
def unix(timestamp):
    if isinstance(timestamp, int) or isinstance(timestamp, long) or isinstance(timestamp, float):
        return datetime.fromtimestamp(timestamp)

