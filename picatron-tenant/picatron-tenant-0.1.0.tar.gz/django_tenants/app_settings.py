# -*- coding: utf-8 -*-
""" Created by Safa Arıman on 5/14/22 """
from django.conf import settings

__author__ = 'safaariman'


ORIGINAL_BACKEND = getattr(settings, 'ORIGINAL_BACKEND', 'django.contrib.gis.db.backends.postgis')

TENANT_MODEL = getattr(settings, 'TENANT_MODEL', 'django_tenants.Tenant')
DOMAIN_MODEL = getattr(settings, 'DOMAIN_MODEL', 'django_tenants.Domain')

MAIN_TENANT_ID = getattr(settings, 'MAIN_TENANT_ID', 1)
