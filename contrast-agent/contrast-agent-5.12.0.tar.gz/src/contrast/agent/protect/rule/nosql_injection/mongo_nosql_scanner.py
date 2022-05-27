# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.sql_injection.default_sql_scanner import (
    DefaultSqlScanner,
)


class MongoNoSqlScanner(DefaultSqlScanner):
    LEFT_ANGLE = "<"

    def start_line_comment(self, char, index, query):
        if char == self.SLASH_CHAR and query[index + 1] == self.SLASH_CHAR:
            return True

        if (
            char == self.LEFT_ANGLE
            and query[index + 1] == self.DASH_CHAR
            and query[index + 2] == self.DASH_CHAR
        ):
            return True

        return False

    def start_block_comment(self, char, index, query):
        return False

    def double_quote_escape_in_double_quote(self):
        return True
