import unittest
from datetime import datetime
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string, assert_locked_lockable


class TestRowSetOpExpressions(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.atlas = make_test_atlas()
        self.rtrace = self.atlas.lusid_logs_requesttrace()
        self.app_req = self.atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 1, 1),
            end_at=datetime(2020, 1, 2)
        )

        self.test_top = self.app_req.select(*self.app_req.get_columns()[:4])
        self.test_bottom = self.rtrace.select(*self.rtrace.get_columns()[:4])
        self.test_union_all = self.test_top.union_all(self.test_bottom)
        self.test_union = self.test_top.union(self.test_bottom)

    def test_union_immutability(self):
        assert_locked_lockable(self, self.test_union)
        assert_locked_lockable(self, self.test_union_all)

    def test_union_validation_column_number_matching(self):
        top = self.rtrace.select('*')
        bottom = self.app_req.select('*')

        with self.assertRaises(ValueError) as ve:
            top.union(bottom)
        self.assertIn('must have the same number of columns', str(ve.exception))

    def test_union_validation_supported_input_types(self):
        top = self.rtrace.select('*')
        with self.assertRaises(TypeError) as te:
            top.union_all(self.app_req)
        self.assertIn('input to union all was not a supported type', str(te.exception))

    def test_union_all_correct_columns_and_sql_str(self):

        union_all = self.test_top.union_all(self.test_bottom)

        # Test columns are correct on union object
        union_hashes = [hash(c) for c in union_all.get_columns()]
        top_hashes = [hash(c) for c in self.test_top.get_columns()]
        self.assertEqual(set(union_hashes), set(top_hashes))

        top_sql = standardise_sql_string(self.test_top.get_table_sql())
        bottom_sql = standardise_sql_string(self.test_bottom.get_table_sql())
        union_sql = standardise_sql_string(union_all.get_sql())

        self.assertIn(top_sql, union_sql)
        self.assertIn(bottom_sql, union_sql)
        self.assertIn('UNION ALL', union_sql)

    def test_union_op_str_fields(self):
        union_all = self.test_top.union_all(self.test_bottom)
        self.assertEqual('union all', union_all._set_op_str)
        union = self.test_top.union(self.test_bottom)
        self.assertEqual('union', union._set_op_str)

    def test_union_all_table_vars(self):

        table_var1 = self.test_top.to_table_var("Test1")
        table_var2 = self.test_bottom.to_table_var("Test2")

        table_var1_sel = table_var1.select('*')
        table_var2_sel = table_var2.select('*')

        union_all = table_var1_sel.union_all(table_var2_sel)
        self.assertEqual(len(union_all._at_var_dependencies), 2)

        union_all_sql = standardise_sql_string(union_all.get_sql())
        self.assertIn(standardise_sql_string('@Test1 ='), union_all_sql)
        self.assertIn(standardise_sql_string('@Test2 ='), union_all_sql)

    def test_can_chain_order_by_on_union(self):
        order_by = self.test_union.order_by(self.test_union.get_columns()[0].descending())
        from lumipy.query.expression.table_op.order_by_op import OrderedTableExpression
        self.assertEqual(type(order_by), OrderedTableExpression)

    def test_can_chain_limit_on_union(self):
        limit = self.test_union.limit(100)
        from lumipy.query.expression.table_op.limit_op import LimitTableExpression
        self.assertEqual(type(limit), LimitTableExpression)

    def test_can_chain_union_on_union(self):
        union = self.test_union.union(self.test_bottom)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(union), RowSetOp)

    def test_can_chain_union_all_on_union(self):
        union_all = self.test_union_all.union_all(self.test_bottom)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(union_all), RowSetOp)

    def test_union_identical_input(self):
        other = self.app_req.select(*self.app_req.get_columns()[:4])
        double = self.test_top.union(other)
        self.assertEqual(
            standardise_sql_string(double.get_sql()),
            standardise_sql_string(f"{other.get_sql()} UNION {other.get_sql()}")
        )

    def test_combination_of_row_set_ops(self):

        union = self.test_top.union_all(self.test_bottom)
        intersection = self.test_top.intersect(self.test_bottom)
        exclusive_or = union.exclude(intersection)
        sql_str = exclusive_or.get_sql()
        expected = """
               SELECT
                 [AppDomainId], [AppVersion], [Application], [AwsInstanceId]
               FROM
                 [Lusid.Logs.AppRequest]
               WHERE
                 [StartAt] = #2020-01-01 00:00:00.000000#
                 AND [EndAt] = #2020-01-02 00:00:00.000000#
                 UNION ALL
               SELECT
                 [CallId], [CloseTime], [CompressedEventBytes], [DecompressedEventBytes]
               FROM
                 [Lusid.Logs.RequestTrace]
                 EXCEPT
               SELECT
                 [AppDomainId], [AppVersion], [Application], [AwsInstanceId]
               FROM
                 [Lusid.Logs.AppRequest]
               WHERE
                 [StartAt] = #2020-01-01 00:00:00.000000#
                 AND [EndAt] = #2020-01-02 00:00:00.000000#
                 INTERSECT
               SELECT
                 [CallId], [CloseTime], [CompressedEventBytes], [DecompressedEventBytes]
               FROM
                 [Lusid.Logs.RequestTrace]
             """
        self.assertEqual(
            standardise_sql_string(sql_str),
            standardise_sql_string(expected)
        )
