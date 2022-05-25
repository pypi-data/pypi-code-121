# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.sql_injection.default_sql_scanner import (
    DefaultSqlScanner,
)


class MysqlSqlScanner(DefaultSqlScanner):
    """
    SQL scanner specifically for MySQL queries
    """

    def start_line_comment(self, char, index, query):
        """
        Valid char is # or subsequent - chars as --
        """
        if char == "#":
            return True

        if char != "-" or not self.query_longer_than_index(query, index, 2):
            return False

        return query[index + 1] == "-"

    def start_block_comment(self, char, index, query):
        """
        Is the current character / sequence of characters the start of a block
        comment. In MySQL, '/*!' is an inline comment that has code that's
        executed, so it does not count as a block comment start
        """

        if char != "/" or not self.query_longer_than_index(query, index, 3):
            return False

        return query[index + 1] == "*" and query[index + 2] != "!"

    def double_quote_escape_in_double_quote(self):
        """
        Indicates if '""' inside of double quotes is the equivalent of '\"'
        """
        return True
