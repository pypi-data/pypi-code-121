import unittest
from datetime import datetime
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string, assert_locked_lockable


class TestHaving(unittest.TestCase):

    def setUp(self):
        atlas = make_test_atlas()
        self.source = atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 9, 1),
            end_at=datetime(2020, 9, 8)
        )
        self.other = atlas.lusid_logs_requesttrace()

        self.test_group_by = self.source.select(
            '^'
        ).where(
            (self.source.duration > 1000) &
            (self.source.application == 'lusid')
        ).group_by(
            self.source.client,
            self.source.method
        )

        self.scalar = self.source.select(
            mean_duration=self.source.duration.mean()
        ).to_scalar_var("TestScalar")

        self.test_agg = self.test_group_by.aggregate(
            MaxTime=self.source.duration.max(),
            MinTime=self.source.duration.min(),
            Count=self.source.duration.count(),
            TotalTime=self.source.duration.sum(),
            MeanTime=self.source.duration.mean()
        )

        self.test_condition = self.test_agg.count > 10
        self.test_having = self.test_agg.having(self.test_condition)

    def test_having_object_is_immutable(self):
        assert_locked_lockable(self, self.test_having)

    def test_having_condition_validation_non_expression(self):
        with self.assertRaises(TypeError) as te:
            self.test_agg.having(condition=True)

        self.assertIn("must be an expression type", str(te.exception))

    def test_having_condition_validation_non_boolean(self):
        with self.assertRaises(TypeError) as te:
            self.test_agg.having(condition=self.test_agg.count / 2)

        self.assertIn("does not resolve to a boolean", str(te.exception))

    def test_having_condition_validation_non_member_column(self):
        with self.assertRaises(ValueError) as ve:
            self.test_agg.having(self.other.self_time > 1000)

        self.assertIn("is not a member of the table", str(ve.exception))

    def test_having_method_returns_having_expression_object(self):
        from lumipy.query.expression.table_op.having_op import HavingTableExpression
        self.assertEqual(type(self.test_having), HavingTableExpression)

    def test_having_condition_containing_scalar_var(self):
        having = self.test_agg.having(self.test_agg.mean_time > self.scalar)
        sql_str = standardise_sql_string(having.get_sql())

        self.assertIn('@@TestScalar = SELECT', sql_str)
        self.assertIn('> @@TestScalar', sql_str)
        self.assertEqual(len(having._at_var_dependencies), 1)

    def test_having_has_correct_lineage(self):
        self.assertEqual(len(self.test_having.get_lineage()), 2)
        parent_hashes = [hash(p) for p in self.test_having.get_lineage()]
        self.assertIn(hash(self.test_agg), parent_hashes)
        self.assertIn(hash(self.test_condition), parent_hashes)

    def test_condition_built_and_stored(self):
        self.assertEqual(hash(self.test_condition), hash(self.test_having.get_condition()))
        self.assertIn(
            standardise_sql_string(self.test_condition.get_sql()),
            standardise_sql_string(self.test_having.get_sql())
        )

    def test_having_has_correct_number_of_columns(self):
        self.assertEqual(
            len(self.test_agg.get_columns()),
            len(self.test_having.get_columns())
        )

    def test_can_chain_order_by_on_having(self):
        order_by = self.test_having.order_by(
            self.test_agg.count.descending()
        )
        from lumipy.query.expression.table_op.order_by_op import OrderedTableExpression
        self.assertEqual(type(order_by), OrderedTableExpression)

    def test_can_chain_limit_on_having(self):
        limit = self.test_having.limit(100)
        from lumipy.query.expression.table_op.limit_op import LimitTableExpression
        self.assertEqual(type(limit), LimitTableExpression)
