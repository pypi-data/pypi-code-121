import unittest
from datetime import datetime

from lumipy.query.expression.column.column_literal import LiteralColumn


class TestLiteralColumns(unittest.TestCase):

    def test_create_column_from_literal(self):

        values = [3.1415, 'arrakis', 1989, datetime(year=1989, month=7, day=9)]
        sql_values = ['3.1415', "'arrakis'", '1989', '#1989-07-09 00:00:00.000000#']
        for i, value in enumerate(values):
            literal_col = LiteralColumn(value)
            self.assertEqual(literal_col.get_sql(), sql_values[i])
