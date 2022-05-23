import unittest
from datetime import datetime
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string, assert_locked_lockable


class TestOrderBy(unittest.TestCase):

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

        self.test_parents = [self.source.select('^'), self.source.select('*'), self.test_agg, self.test_having]

        self.test_order_by = self.source.select('^').order_by(self.source.duration.ascending())

    def test_order_by_object_is_immutable(self):
        assert_locked_lockable(self, self.test_order_by)

    def test_order_by_validation_empty(self):
        with self.assertRaises(ValueError):
            self.source.select('^').order_by()

    def test_order_by_validation_non_ordering(self):
        with self.assertRaises(TypeError) as te:
            self.source.select('^').order_by(self.source.duration)
        self.assertIn("wasn't an ordering", str(te.exception))

    def test_order_by_validation_alien_column(self):
        with self.assertRaises(ValueError) as ve:
            self.source.select('^').order_by(self.other.self_time.ascending())
        self.assertIn("is not a member of the table", str(ve.exception))

    def test_order_by_containing_scalar_var(self):
        order = self.source.select('^').order_by(
            (self.source.duration//self.scalar).descending()
        )
        self.assertEqual(len(order._at_var_dependencies), 1)
        self.assertEqual(len(order.get_lineage()), 2)

        sql_str = standardise_sql_string(order.get_sql())
        self.assertIn(standardise_sql_string('@@TestScalar = SELECT'), sql_str)
        self.assertIn(standardise_sql_string('/ @@TestScalar'), sql_str)

    def test_order_by_with_multiple_columns(self):
        orders = [
            self.source.duration.ascending(),
            self.source.method.descending()
        ]
        order_by = self.source.select('^').order_by(*orders)
        sql_str = order_by.get_sql()
        for order in orders:
            self.assertIn(order.get_sql(), sql_str)
        self.assertEqual(len(order_by.get_lineage()), 3)

    def test_order_by_has_correct_number_of_cols(self):
        for parent in self.test_parents:
            qry = parent.order_by(parent.get_columns()[-1].ascending())
            qry_hashes = [hash(c) for c in qry.get_columns()]
            parent_hashes = [hash(c) for c in parent.get_columns()]
            self.assertEqual(set(qry_hashes), set(parent_hashes))

    def test_can_chain_limit_on_order_by(self):
        limit = self.test_order_by.limit(100)
        from lumipy.query.expression.table_op.limit_op import LimitTableExpression
        self.assertEqual(type(limit), LimitTableExpression)
