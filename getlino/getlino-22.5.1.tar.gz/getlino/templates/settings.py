# -*- coding: UTF-8 -*-
from {{app_settings_module}} import *
from {{local_prefix}}.settings import *

# import logging
# logging.getLogger('weasyprint').setLevel("ERROR") # see #1462


class Site(Site):
    title = "{{prjname}}"
    server_url = "{{server_url}}"
    {% if webdav %}
    webdav_protocol = 'wdav'
    {% endif %}
    {% if languages %}
    languages = '{{languages}}'
    {% endif %}
    use_linod = True
    default_ui = '{{front_end}}'
    show_internal_field_names = True

    def get_plugin_configs(self):
        yield super(Site, self).get_plugin_configs()
        # example of local plugin settings:
        # yield ('ledger', 'start_year', 2018)
        yield ('help', 'make_help_pages', True)

SITE = Site(globals())

{% if server_domain == "localhost" %}
DEBUG = True
# ALLOWED_HOSTS = ['{{server_domain}}']
{% else %}
DEBUG = False  # "{{server_domain}}"
ALLOWED_HOSTS = ['{{server_domain}}']
{% endif %}

SECRET_KEY = '{{secret_key}}'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{{db_engine}}',
        'NAME': '{{db_name}}',
        {%- if db_engine != "sqlite3" %}
            'USER': '{{db_user}}',
            'PASSWORD': '{{db_password}}',
            'HOST': '{{db_host}}',
            'PORT': {{db_port}},
        {% endif -%}
        {%- if db_engine == "mysql" %}
        'OPTIONS': {
           "init_command": "SET default_storage_engine=MyISAM",
        }
        {% endif -%}
    }
}

EMAIL_SUBJECT_PREFIX = '[{{prjname}}] '
