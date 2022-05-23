import unittest

from lumipy.query.expression.column.column_ordering import AscendingOrder, DescendingOrder
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.sql_value_type import SqlValType, numerics
from test.unit.utilities.test_utils import make_test_atlas


class TestColumnOrdering(unittest.TestCase):

    def test_ordering_on_provider_columns(self):

        atlas = make_test_atlas()

        for p_description in atlas.list_providers():
            for c_description in p_description.list_columns():
                col = SourceColumn(c_description, hash(p_description))

                # ASCENDING
                col_asc = col.ascending()
                self.assertEqual(type(col_asc), AscendingOrder)
                self.assertTrue(col_asc, f"{col.get_sql()} ASC")
                self.assertEqual(col_asc._type, SqlValType.Ordering)

                # DESCENDING
                col_desc = col.descending()
                self.assertEqual(type(col_desc), DescendingOrder)
                self.assertTrue(col_desc, f"{col.get_sql()} DESC")
                self.assertEqual(col_desc._type, SqlValType.Ordering)

    def test_ordering_on_derived_column(self):

        atlas = make_test_atlas()

        test_ops = {
            'mul': lambda x, y: x * y,
            'div': lambda x, y: x / y,
            'add': lambda x, y: x + y,
            'sub': lambda x, y: x - y,
            'mod': lambda x, y: x % y,
        }

        for p_description in atlas.list_providers():
            numeric_cols = [
                SourceColumn(c, hash(p_description))
                for c in p_description.list_columns()
                if c.data_type in numerics
            ]

            for c1 in numeric_cols:
                for c2 in numeric_cols:
                    for name, op in test_ops.items():
                        derived = op(c1, c2)

                        # ASCENDING
                        derived_asc = derived.ascending()
                        self.assertEqual(type(derived_asc), AscendingOrder)
                        self.assertTrue(derived_asc, f"{derived.get_sql()} ASC")
                        self.assertEqual(derived_asc._type, SqlValType.Ordering)

                        # DESCENDING
                        derived_desc = derived.descending()
                        self.assertEqual(type(derived_desc), DescendingOrder)
                        self.assertTrue(derived_desc, f"{derived.get_sql()} DESC")
                        self.assertEqual(derived_desc._type, SqlValType.Ordering)

    def test_ordering_on_column_index(self):

        for i in range(1, 5):
            asc_col = AscendingOrder(i)
            desc_col = DescendingOrder(i)
            self.assertEqual(asc_col.get_sql(), f'{i} ASC')
            self.assertEqual(desc_col.get_sql(), f'{i} DESC')

    def test_ordering_on_column_index_fails_with_zero(self):

        with self.assertRaises(ValueError):
            AscendingOrder(0)
        with self.assertRaises(ValueError):
            DescendingOrder(0)

    def test_ordering_on_aliased_column(self):

        atlas = make_test_atlas()

        for p_description in atlas.list_providers():
            for c_description in p_description.list_columns():
                col = SourceColumn(c_description, hash(p_description))
                aliased = col.with_alias('TestAlias')

                aliased_asc = aliased.ascending()
                aliased_desc = aliased.descending()

                self.assertEqual(aliased_asc.get_sql(), col.ascending().get_sql())
                self.assertEqual(aliased_desc.get_sql(), col.descending().get_sql())


