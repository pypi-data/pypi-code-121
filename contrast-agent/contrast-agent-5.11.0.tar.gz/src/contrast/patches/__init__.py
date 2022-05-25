# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


from . import (
    cs_io,
    encodings_patch,
    re_patch,
    threading_patch,
    exec_and_eval,
    lxml_patch,
    pathlib_patch,
    sys_patch,
    import_patch,
    cgi_patch,
    concurrent_futures_thread_patch,
)

from .databases import (
    mysql_connector_patch,
    pymysql_patch,
    psycopg2_patch,
    sqlalchemy_patch,
    sqlite3_patch,
)

from .frameworks import (
    bottle_patches,
    django_patches,
    drf_patches,
    falcon_multipart_patch,
    pyramid_patch,
    starlette_patches,
)


COMMON_PATCH_MODULES = (
    pathlib_patch,
    sqlalchemy_patch,
    # our sqlite3_patch also contains the import hook for pysqlite2.dbapi2
    sqlite3_patch,
    mysql_connector_patch,
    pymysql_patch,
    psycopg2_patch,
    concurrent_futures_thread_patch,
)


LIBRARY_READER_PATCHES = (import_patch,)


ASSESS_PATCH_MODULES = (
    threading_patch,
    cs_io,
    encodings_patch,
    re_patch,
    exec_and_eval,
    lxml_patch,
    pyramid_patch,
    django_patches,
    drf_patches,
    bottle_patches,
    falcon_multipart_patch,
    sys_patch,
    import_patch,
    cgi_patch,
    starlette_patches,
)


def register_module_patches(module, patch_group):
    logger.debug("registering %s patches for %s", patch_group, module.__name__)

    try:
        module.register_patches()
    except Exception:
        logger.exception("failed to register patches for %s", module.__name__)


def register_library_patches():
    for module in LIBRARY_READER_PATCHES:
        register_module_patches(module, "library analysis")


def register_common_patches():
    for module in COMMON_PATCH_MODULES:
        register_module_patches(module, "common")


def register_assess_patches():
    for module in ASSESS_PATCH_MODULES:
        register_module_patches(module, "assess")
