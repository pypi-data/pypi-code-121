# coding=utf-8
from __future__ import absolute_import, print_function

import itertools

from suanpan.arguments import Int, String
from suanpan.proxy import Proxy
from suanpan import error

# try:
#     from suanpan.dw import hive, mysql, postgres  # odps
# except ImportError:
#     from suanpan.dw import mock
#     hive = mysql = postgres = mock  # odps


class DataWarehouseProxy(Proxy):
    # MAPPING = {
    #     "hive": hive.DataWarehouse,
    #     # "odps": odps.DataWarehouse,
    #     "postgres": postgres.DataWarehouse,
    #     "mysql": mysql.DataWarehouse,
    # }
    DEFAULT_ARGUMENTS = [String("dw-type", default="odps")]
    HIVE_ARGUMENTS = [
        String("dw-hive-host", default="localhost"),
        Int("dw-hive-port", default=10000),
        String("dw-hive-database", default="default"),
        String("dw-hive-username"),
        String("dw-hive-password"),
        String("dw-hive-auth"),
    ]

    ODPS_ARGUMENTS = [
        String("dw-odps-access-id"),
        String("dw-odps-access-key"),
        String(
            "dw-odps-endpoint", default="http://service.cn.maxcompute.aliyun.com/api"
        ),
        String("dw-odps-project"),
    ]

    POSTGRES_ARGUMENTS = [
        String("dw-postgres-host", default="localhost"),
        Int("dw-postgres-port", default=5432),
        String("dw-postgres-database"),
        String("dw-postgres-username"),
        String("dw-postgres-password"),
    ]

    MYSQL_ARGUMENTS = [
        String("dw-mysql-host", default="localhost"),
        Int("dw-mysql-port", default=3306),
        String("dw-mysql-database"),
        String("dw-mysql-username"),
        String("dw-mysql-password"),
    ]

    ARGUMENTS = list(
        itertools.chain(
            DEFAULT_ARGUMENTS,
            HIVE_ARGUMENTS,
            ODPS_ARGUMENTS,
            POSTGRES_ARGUMENTS,
            MYSQL_ARGUMENTS,
        )
    )

    def importBackend(self, backendType):
        try:
            if backendType == "hive":
                from suanpan.dw import hive
                return hive.DataWarehouse
            elif backendType == "postgres":
                from suanpan.dw import postgres
                return postgres.DataWarehouse
            elif backendType == "mysql":
                from suanpan.dw import mysql
                return mysql.DataWarehouse
            else:
                raise error.ProxyError(
                    f"{self.name} don't supported backend type {backendType}"
                )
        except ImportError:
            from suanpan.dw import mock
            return mock.DataWarehouse


dw = DataWarehouseProxy()
