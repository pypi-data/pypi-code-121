# -*- coding: utf-8 -*-
""" Created by Safa Arıman on 5/14/22 """
from django.apps import apps as global_apps
from django.core.management.color import no_style
from django.db import DEFAULT_DB_ALIAS, connections, router

from django_tenants import get_tenant_model
from django_tenants import app_settings

__author__ = 'safaariman'


def create_default_tenant(
    app_config,
    verbosity=2,
    interactive=True,
    using=DEFAULT_DB_ALIAS,
    apps=global_apps,
    **kwargs,
):
    try:
        Tenant = get_tenant_model()
    except LookupError:
        return

    if not router.allow_migrate_model(using, Tenant):
        return

    if not Tenant.objects.using(using).exists():
        if verbosity >= 2:
            print("Creating Picatron Tenant object")
        Tenant(
            pk=app_settings.MAIN_TENANT_ID, name="Picatron"
        ).save(using=using)

        sequence_sql = connections[using].ops.sequence_reset_sql(no_style(), [Tenant])
        if sequence_sql:
            if verbosity >= 2:
                print("Resetting sequence")
            with connections[using].cursor() as cursor:
                for command in sequence_sql:
                    cursor.execute(command)
