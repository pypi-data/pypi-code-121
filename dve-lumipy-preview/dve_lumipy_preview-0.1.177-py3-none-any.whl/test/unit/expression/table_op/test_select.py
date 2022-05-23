import unittest
from datetime import datetime
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string, assert_locked_lockable


class TestSelect(unittest.TestCase):

    def setUp(self):
        atlas = make_test_atlas()
        self.source = atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 9, 1),
            end_at=datetime(2020, 9, 8)
        )
        self.other = atlas.lusid_logs_requesttrace()
        self.test_select = self.source.select('*')

    def test_select_object_is_immutable(self):
        assert_locked_lockable(self, self.test_select)

    def test_select_failure_with_no_columns(self):
        with self.assertRaises(ValueError) as ve:
            self.source.select()

        msg = str(ve.exception)
        self.assertIn("No columns supplied", msg)

    def test_select_failure_with_alien_columns(self):
        with self.assertRaises(ValueError) as ve:
            self.source.select(self.other.self_time)
        msg = str(ve.exception)
        self.assertIn(self.other.self_time.get_sql(), msg)
        self.assertIn("not a member of the table", msg)

        with self.assertRaises(ValueError) as ve:
            self.source.select(
                *(
                    self.source.get_columns()[:5]
                    + [self.other.self_time]
                )
            )
        msg = str(ve.exception)
        self.assertIn(self.other.self_time.get_sql(), msg)
        self.assertIn("not a member of the table", msg)

    def test_source_table_select_method_select_star(self):

        selected = self.source.select('*')

        self.assertGreater(len(selected.get_columns()), 0)
        self.assertEqual(len(selected.get_columns()), len(self.source.get_columns()))
        self.assertIn('WHERE', selected.get_sql())
        self.assertIn('StartAt', selected.get_sql())
        self.assertIn('EndAt', selected.get_sql())
        for col in self.source.get_columns():
            self.assertIn(col.get_sql(), selected.get_sql())

    def test_source_table_select_method_select_main(self):

        selected = self.source.select('^')

        self.assertGreater(len(selected.get_columns()), 0)
        self.assertEqual(len(selected.get_columns()), len([c for c in self.source.get_columns() if c.is_main()]))
        self.assertIn('WHERE', selected.get_sql())
        self.assertIn('StartAt', selected.get_sql())
        self.assertIn('EndAt', selected.get_sql())
        for col in self.source.get_columns():
            if col.is_main():
                self.assertIn(col.get_sql(), selected.get_sql())

    def test_source_table_select_method_select_tuple_of_cols(self):

        cols = self.source.get_columns()[::2]
        selected = self.source.select(*cols)

        self.assertGreater(len(selected.get_columns()), 0)
        self.assertEqual(len(selected.get_columns()), len(cols))
        self.assertIn('WHERE', selected.get_sql())
        self.assertIn('StartAt', selected.get_sql())
        self.assertIn('EndAt', selected.get_sql())

        for col in cols:
            self.assertIn(col.get_sql(), selected.get_sql())

    def test_source_table_select_method_with_kwargs_mix(self):

        selected = self.source.select(
            '^',
            DurationSeconds=self.source.duration*0.001
        )

        self.assertGreater(len(selected.get_columns()), 0)
        self.assertEqual(len(selected.get_columns()), len([c for c in self.source.get_columns() if c.is_main()])+1)
        self.assertIn('WHERE', selected.get_sql())
        self.assertIn('StartAt', selected.get_sql())
        self.assertIn('EndAt', selected.get_sql())
        for col in self.source.get_columns():
            if col.is_main():
                self.assertIn(col.get_sql(), selected.get_sql())

        self.assertIn('duration_seconds', [c.get_name() for c in selected.get_columns()])
        self.assertIn('DurationSeconds', selected.get_sql())

    def test_table_at_var_select_method_with_kwarg_mix(self):

        table_var = self.source.select(
            '^',
            CallSeconds=self.source.duration*0.001
        ).where(
            self.source.duration > 20000
        ).to_table_var("LongRunning")

        table_var_cols = table_var.get_columns()

        selected = table_var.select('*')
        self.assertGreater(len(selected.get_columns()), 0)
        self.assertEqual(len(selected.get_columns()), len(table_var_cols))
        self.assertIn('call_seconds', [c.get_name() for c in selected.get_columns()])
        self.assertIn('CallSeconds', selected.get_sql())

    def test_select_distinct(self):

        """
        Select distinct will produce a Select expression object which is identical to a normal select
        just with a different select string in the table SQL ('select distinct'). The above tests will
        cover that stuff. This one tests that the distinct select string works.
        """

        selected = self.source.select_distinct(
            '^',
            CallSeconds=self.source.duration * 0.001
        )

        self.assertIn('SELECT DISTINCT', standardise_sql_string(selected.get_sql()))

    def test_can_chain_where_on_select(self):
        where = self.test_select.where(self.source.duration > 1000)
        from lumipy.query.expression.table_op.where_op import WhereTableExpression
        self.assertEqual(type(where), WhereTableExpression)

    def test_can_chain_group_by_on_select(self):
        group_by = self.test_select.group_by(self.source.application)
        from lumipy.query.expression.table_op.group_by_op import GroupBy
        self.assertEqual(type(group_by), GroupBy)

    def test_can_chain_order_by_on_select(self):
        order_by = self.test_select.order_by(self.source.duration.ascending())
        from lumipy.query.expression.table_op.order_by_op import OrderedTableExpression
        self.assertEqual(type(order_by), OrderedTableExpression)

    def test_can_chain_limit_on_select(self):
        limit = self.test_select.limit(100)
        from lumipy.query.expression.table_op.limit_op import LimitTableExpression
        self.assertEqual(type(limit), LimitTableExpression)

    def test_can_chain_union(self):
        other = self.test_select.where(self.source.duration > 100)
        union = self.test_select.union(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(union), RowSetOp)
        self.assertIn(union._set_op_str, 'union')

    def test_can_chain_union_all(self):
        other = self.test_select.where(self.source.duration > 100)
        union = self.test_select.union_all(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(union), RowSetOp)
        self.assertEqual(union._set_op_str, 'union all')

    def test_can_chain_intersect(self):
        other = self.test_select.where(self.source.duration > 100)
        intersect = self.test_select.intersect(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(intersect), RowSetOp)
        self.assertIn(intersect._set_op_str, 'intersect')

    def test_can_chain_except(self):
        other = self.test_select.where(self.source.duration > 100)
        exclude = self.test_select.exclude(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(exclude), RowSetOp)
        self.assertEqual(exclude._set_op_str, 'except')
