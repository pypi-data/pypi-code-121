import unittest
from datetime import datetime

from lumipy.query.expression.column.column_prefix import PrefixedColumn
from lumipy.query.expression.table.table_alias import AliasedTable
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


# noinspection PyPep8Naming
class TestAliasedTable(unittest.TestCase):

    def setUp(self):
        self.atlas = make_test_atlas()
        self.appreq = self.atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 1, 1),
            end_at=datetime(2020, 1, 2)
        )
        self.rtrace = self.atlas.lusid_logs_requesttrace()

    def test_create_alias_table(self):

        aliased = self.rtrace.with_alias('LHS')
        self.assertTrue(isinstance(aliased, AliasedTable))

        for a_col in aliased.get_columns():
            self.assertTrue(isinstance(a_col, PrefixedColumn))
            self.assertEqual(a_col.get_prefix(), aliased.get_alias())

        p_col2 = aliased.get_prefixed_col(self.rtrace.self_time)
        self.assertTrue(isinstance(p_col2, PrefixedColumn))
        self.assertTrue(p_col2.hash_equals(aliased.self_time))

    def test_select_alias_table(self):
        aliased = self.rtrace.with_alias('LHS')
        p_col = aliased.get_prefixed_col(self.rtrace.self_time)

        test_select1 = standardise_sql_string(aliased.select(p_col).get_sql())
        test_select2 = standardise_sql_string(aliased.select(self.rtrace.self_time).get_sql())
        self.assertEqual(test_select1, test_select2)

        test_select3 = aliased.select('*')
        self.assertEqual(len(test_select3.get_columns()), len(self.rtrace.get_columns()))
        test_select4 = aliased.select('^')
        self.assertEqual(
            len(test_select4.get_columns()),
            len([c for c in self.rtrace.get_columns() if c.is_main()])
        )

        test_select5 = aliased.select(self_time_sec=aliased.self_time*0.001).get_sql()
        test_select6 = aliased.select(self_time_sec=self.rtrace.self_time*0.001).get_sql()
        self.assertIn('LHS.', test_select5)
        self.assertEqual(test_select5, test_select6)

    def test_where_alias_table(self):

        aliased = self.rtrace.with_alias('LHS')
        test_qry = aliased.select('^').where(
            (aliased.self_time//aliased.duration) > 0.5
        )
        sql_str = standardise_sql_string(test_qry.get_sql())

        self.assertEqual(
            sql_str,
            'SELECT LHS.[CallId], LHS.[Duration], LHS.[FunctionName], LHS.[ParentCallId], '
            'LHS.[RequestId], LHS.[SelfTime], LHS.[ThreadId] FROM [Lusid.Logs.RequestTrace] AS LHS '
            'WHERE ((LHS.[SelfTime] / LHS.[Duration]) > 0.5)'
        )

    def test_get_prefixed_col_passthrough(self):
        aliased = self.rtrace.with_alias('LHS')
        pass_through = aliased.get_prefixed_col(aliased.self_time)
        self.assertTrue(aliased.self_time.hash_equals(pass_through))

    def test_alias_table_hashes_are_different(self):

        aliased1 = self.appreq.with_alias('LHS')
        aliased2 = self.appreq.with_alias('RHS')
        self.assertNotEqual(hash(aliased1), hash(aliased2))

    def test_alias_table_select_cant_use_col_with_wrong_prefix(self):

        aliased1 = self.appreq.with_alias('LHS')
        aliased2 = self.appreq.with_alias('RHS')

        with self.assertRaises(ValueError) as ve:
            aliased1.select(aliased2.duration)
        self.assertIn("Incompatible column", str(ve.exception))

    def test_table_alias_apply_prefix_chain(self):

        aliased1 = self.rtrace.with_alias('LHS')
        aliased2 = self.appreq.with_alias('RHS')

        expression = (self.appreq.duration-self.rtrace.self_time)*0.001

        prefixed_1 = aliased1.apply_prefix(expression)
        prefixed_1_2 = aliased2.apply_prefix(prefixed_1)
        self.assertEqual(standardise_sql_string(prefixed_1.get_sql()), "([Duration] - LHS.[SelfTime]) * 0.001")
        self.assertEqual(standardise_sql_string(prefixed_1_2.get_sql()), "(RHS.[Duration] - LHS.[SelfTime]) * 0.001")

    def test_degenerate_cols_expression_with_prexisting_prefixes(self):

        atlas = make_test_atlas()
        rtrace = atlas.lusid_logs_requesttrace()
        lhs = rtrace.with_alias('LHS')
        rhs = rtrace.with_alias('RHS')

        req_id = '0HM3R52M8C342:00000009'
        condition = (rhs.request_id == req_id) & (lhs.request_id == req_id) & (lhs.self_time > 0)

        test = lhs.apply_prefix(rhs.apply_prefix(condition))

        self.assertEqual(condition.get_sql(), test.get_sql())
