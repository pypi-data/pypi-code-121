import unittest
from test.unit.utilities.test_utils import make_test_atlas
from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.common.string_utils import to_snake_case


class TestAliasedColumns(unittest.TestCase):

    def test_alias_on_provider_column(self):
        atlas = make_test_atlas()
        for p_description in atlas.list_providers():

            for c_description in p_description.list_columns():
                dummy_hash = hash(p_description)
                col = SourceColumn(c_description, dummy_hash)

                alias = 'AliasedColumn'
                alias_col = col.with_alias(alias)
                self.assertEqual(alias_col.get_name(), to_snake_case(alias))
                self.assertEqual(alias_col.get_sql(), f"{col.get_sql()} AS [{alias}]")
                self.assertEqual(alias_col.source_table_hash(), col.source_table_hash())

    def test_column_alias_handling_as_col_on_new_table(self):

        atlas = make_test_atlas()
        for p_description in atlas.list_providers():
            for c_description in p_description.list_columns():
                alias = 'AliasForColumn'

                dummy_hash = hash(p_description)

                col = SourceColumn(c_description, dummy_hash)
                aliased_col = col.with_alias(alias)
                new_col = aliased_col.as_col_on_new_table("@table", hash("@table"))

                self.assertEqual(new_col.get_name(), to_snake_case(alias))
                self.assertEqual(new_col.get_sql(), f"[{alias}]")
                self.assertEqual(new_col.source_table_hash(), hash("@table"))

    def test_ops_on_aliased_columns_removes_alias(self):

        atlas = make_test_atlas()
        rhs = atlas.lusid_logs_requesttrace()
        cond = rhs.self_time // (rhs.duration.with_alias('duration_rhs'))

        self.assertTrue('AS duration_rhs' not in cond.get_sql())
        self.assertEqual(cond.get_sql(), '[SelfTime] / [Duration]')

    def test_aliasing_an_aliased_column_fails(self):

        atlas = make_test_atlas()
        rhs = atlas.lusid_logs_requesttrace()
        aliased = rhs.duration.with_alias('duration_rhs')

        with self.assertRaises(TypeError):
            aliased.with_alias("AnotherAlias")

    def test_aliasing_prefixed_column(self):

        atlas = make_test_atlas()
        rhs = atlas.lusid_logs_requesttrace().with_alias('RHS')
        aliased = rhs.duration.with_alias('duration_rhs')

        sql_str = aliased.get_sql()
        self.assertEqual('RHS.[Duration] AS [duration_rhs]', sql_str)
