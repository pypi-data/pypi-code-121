# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.sql_injection.default_sql_scanner import (
    DefaultSqlScanner,
)


class PostgresSqlScanner(DefaultSqlScanner):
    """
    SQL Scanner for Postgres
    """

    pass
