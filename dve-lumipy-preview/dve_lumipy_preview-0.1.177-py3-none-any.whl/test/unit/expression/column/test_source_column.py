import unittest

from lumipy.query.expression.column.source_column import SourceColumn
from test.unit.utilities.test_utils import make_test_atlas


class TestSourceColumn(unittest.TestCase):

    def test_source_column_creation(self):

        atlas = make_test_atlas()

        for p_description in atlas.list_providers():
            p_hash = hash(p_description)
            for c_description in p_description.list_columns():
                col = SourceColumn(c_description, p_hash)
                self.assertEqual(
                    col.get_name(), c_description.name,
                    msg=f"Column ({col.get_name()}) name ({col.get_name()}) did not match "
                        f"name from field description ({c_description.name})."
                )
                self.assertEqual(
                    col.source_table_hash(), p_hash,
                    msg=f"Column ({col.get_name()}) source table hash ({col.source_table_hash()}) did not match "
                        f"hash given to its ctor ({p_hash})."
                )
                self.assertEqual(
                    col.is_main(), c_description.is_main,
                    msg=f"Column ({col.get_name()}) is_main value ({col.is_main()}) did not match "
                        f"is_main from field description ({c_description.is_main})."
                )
                self.assertEqual(
                    col.get_sql(),
                    c_description.field_name
                )

    def test_single_conversion_to_source_col_on_new_table(self):

        atlas = make_test_atlas()

        # Single Columns
        for p_description in atlas.list_providers():
            p_hash = hash(p_description)
            for c_description in p_description.list_columns():
                col = SourceColumn(c_description, p_hash)

                new_col = col.as_col_on_new_table("NewTable", hash("NewTable"))

                self.assertEqual(new_col.source_table_hash(), hash("NewTable"))
