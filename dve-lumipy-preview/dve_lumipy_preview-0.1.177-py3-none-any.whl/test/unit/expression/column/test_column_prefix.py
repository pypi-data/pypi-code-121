import unittest
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.column.column_prefix import PrefixedColumn
from test.unit.utilities.test_utils import make_test_atlas


class TestPrefixColumns(unittest.TestCase):

    def test_prefix_column_creation_from_source_column(self):

        atlas = make_test_atlas()

        for p_description in atlas.list_providers():
            p_hash = hash(p_description)
            for c_description in p_description.list_columns():
                col = SourceColumn(c_description, p_hash)

                prefix = 'rhs'
                prefix_col = PrefixedColumn(col, prefix)
                self.assertEqual(prefix_col.get_name(), col.get_name())
                self.assertEqual(prefix_col.get_sql(), f"{prefix}.{col.get_sql()}")
                self.assertEqual(prefix_col.source_table_hash(), col.source_table_hash())
                self.assertEqual(hash(prefix_col.get_without_prefix()), hash(col))
