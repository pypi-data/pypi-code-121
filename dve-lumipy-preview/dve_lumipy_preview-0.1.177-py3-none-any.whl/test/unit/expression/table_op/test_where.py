import unittest
from datetime import datetime
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string, assert_locked_lockable


class TestWhere(unittest.TestCase):

    def setUp(self):
        atlas = make_test_atlas()
        self.source = atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 9, 1),
            end_at=datetime(2020, 9, 8)
        )
        self.other = atlas.lusid_logs_requesttrace()

        self.test_select = self.source.select('*')

        self.scalar = self.source.select(
            mean_duration=self.source.duration.mean()
        ).to_scalar_var("TestScalar")

        self.test_condition = (self.source.duration > 1000) & (
              (self.source.application == 'lusid') |
              (self.source.application == 'shrine')
        )
        self.test_where = self.test_select.where(self.test_condition)

    def test_where_condition_validation_non_expression(self):
        with self.assertRaises(TypeError) as te:
            self.test_select.where(condition=True)

        self.assertIn("must be a column expression type", str(te.exception))

    def test_where_condition_validation_non_boolean(self):
        with self.assertRaises(TypeError) as te:
            self.test_select.where(condition=self.test_select.duration / 2)

        self.assertIn("does not resolve to a boolean", str(te.exception))

    def test_where_condition_validation_non_member_column(self):
        with self.assertRaises(ValueError) as ve:
            self.test_select.where(self.other.self_time > 1000)

        self.assertIn("is not a member of the table", str(ve.exception))

    def test_where_method_returns_where_expression_object(self):
        from lumipy.query.expression.table_op.where_op import WhereTableExpression
        self.assertEqual(type(self.test_where), WhereTableExpression)

    def test_where_condition_containing_scalar_var(self):
        where = self.test_select.where(self.source.duration > self.scalar)
        sql_str = standardise_sql_string(where.get_sql())

        self.assertIn('@@TestScalar = SELECT', sql_str)
        self.assertIn('> @@TestScalar', sql_str)

    def test_where_condition_with_non_selected_cols(self):
        select = self.source.select(self.source.method)
        where = select.where(self.source.duration > 1000)

        sql_str = standardise_sql_string(where.get_sql())
        expected = '''
        SELECT [Method] FROM [Lusid.Logs.AppRequest] WHERE 
        [StartAt] = #2020-09-01 00:00:00.000000# AND 
        [EndAt] = #2020-09-08 00:00:00.000000# AND 
        ([Duration] > 1000)
        '''
        self.assertEqual(sql_str, standardise_sql_string(expected))

    def test_where_clause_is_built_and_stored_correctly(self):
        condition_sql = standardise_sql_string(self.test_condition.get_sql())
        where_sql = standardise_sql_string(self.test_where.get_sql()).split('where')[-1]
        self.assertTrue(self.test_condition.hash_equals(self.test_where.get_condition()))
        self.assertIn(condition_sql, where_sql)

    def test_filter_alias_gives_same_result(self):
        filter_output = self.test_select.filter(self.test_condition)
        self.assertEqual(hash(filter_output), hash(self.test_where))
        self.assertEqual(filter_output.get_sql(), self.test_where.get_sql())

    def test_where_object_is_immutable(self):
        assert_locked_lockable(self, self.test_where)

    def test_where_object_includes_provider_params(self):
        where_sql = standardise_sql_string(self.test_where.get_sql()).split('where')[-1]
        self.assertIn('[StartAt] = #', where_sql)
        self.assertIn('[EndAt] = #', where_sql)

    def test_where_object_has_correct_columns(self):
        star_where = self.test_select.where(self.test_condition)
        self.assertEqual(len(star_where.get_columns()), len(self.test_select.get_columns()))

        main_where = self.source.select('^').where(self.test_condition)
        self.assertEqual(
            len(main_where.get_columns()),
            len([c for c in self.test_select.get_columns() if c.is_main()])
        )

        cols = self.source.get_columns()[::2]
        explicit_where = self.source.select(
            *cols,
            MaxDuration=self.source.duration.max()
        ).where(self.test_condition)
        self.assertEqual(len(explicit_where.get_columns()), len(cols) + 1)

    def test_where_object_has_correct_lineage(self):
        condition = self.test_condition
        select = self.test_select
        where = select.where(condition)
        lineage_hashes = [hash(p) for p in where.get_lineage()]

        self.assertIn(hash(select), lineage_hashes)
        self.assertIn(hash(condition), lineage_hashes)
        self.assertEqual(len(lineage_hashes), 2)

    def test_where_object_has_correct_select_string(self):
        select = self.source.select(self.source.application).where(self.test_condition)
        distinct = self.source.select_distinct(self.source.application).where(self.test_condition)
        self.assertIn('SELECT [', standardise_sql_string(select.get_sql()))
        self.assertIn('SELECT DISTINCT [', standardise_sql_string(distinct.get_sql()))

    def test_can_chain_group_by_on_where(self):
        group_by = self.test_where.group_by(self.source.method)
        from lumipy.query.expression.table_op.group_by_op import GroupBy
        self.assertEqual(type(group_by), GroupBy)

    def test_can_chain_order_by_on_where(self):
        order_by = self.test_where.order_by(self.source.application.ascending())
        from lumipy.query.expression.table_op.order_by_op import OrderedTableExpression
        self.assertEqual(type(order_by), OrderedTableExpression)

    def test_can_chain_limit_on_where(self):
        limit = self.test_where.limit(100)
        from lumipy.query.expression.table_op.limit_op import LimitTableExpression
        self.assertEqual(type(limit), LimitTableExpression)

    def test_can_chain_union_on_where(self):
        other = self.test_select.where(~self.test_condition)
        union = self.test_where.union(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(union), RowSetOp)
        self.assertEqual(union._set_op_str, 'union')

    def test_can_chain_union_all_on_where(self):
        other = self.test_select.where(~self.test_condition)
        union = self.test_where.union_all(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(union), RowSetOp)
        self.assertEqual(union._set_op_str, 'union all')

    def test_can_chain_intersect_on_where(self):
        other = self.test_select.where(~self.test_condition)
        intersect = self.test_where.intersect(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(intersect), RowSetOp)
        self.assertEqual(intersect._set_op_str, 'intersect')

    def test_can_chain_exclude_on_where(self):
        other = self.test_select.where(~self.test_condition)
        exclude = self.test_where.exclude(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(exclude), RowSetOp)
        self.assertEqual(exclude._set_op_str, 'except')
