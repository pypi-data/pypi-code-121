import unittest
from datetime import datetime

from test.unit.utilities.test_utils import make_test_atlas, assert_locked_lockable


class TestGroupBy(unittest.TestCase):

    def setUp(self):
        self.atlas = make_test_atlas()
        self.source = self.atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 9, 1),
            end_at=datetime(2020, 9, 8)
        )
        self.scalar = self.source.select(
            mean_duration=self.source.duration.mean()
        ).to_scalar_var("TestScalar")

    def test_group_by_object_is_immutable(self):
        assert_locked_lockable(self, self.source.select('*').group_by(self.source.method))

    def test_group_by_column_select_explicit(self):

        qry = self.source.select(
            self.source.application, self.source.method
        ).group_by(
            self.source.controller
        )

        cols = qry.get_select_columns()
        self.assertEqual(len(cols), 3)

        col_names = {col.get_name() for col in cols}
        self.assertEqual(col_names, {'controller', 'method', 'application'})

    def test_group_by_column_select_main(self):

        qry = self.source.select(
            '^'
        ).group_by(
            self.source.controller
        )

        cols = qry.get_select_columns()
        self.assertEqual(len(cols), 10)

        col_names = [col.get_name() for col in self.source.get_columns() if col.is_main()]
        col_names += ['controller']
        self.assertEqual(set([c.get_name() for c in cols]), set(col_names))

    def test_group_by_multiple_columns(self):
        qry = self.source.select(
            '^'
        ).group_by(
            self.source.method,
            self.source.controller,
            self.source.application
        )

        group_cols = qry.get_group_columns()
        select_cols = qry.get_select_columns()

        select_hashes = [hash(c) for c in select_cols]
        self.assertEqual(len(group_cols), 3)
        for gc in group_cols:
            self.assertIn(hash(gc), select_hashes)
        self.assertEqual(len(select_cols), 10)

    def test_group_by_with_column_op_group_by_col(self):
        groups = [self.source.method, self.source.duration > 1000]
        qry = self.source.select(
            '^'
        ).group_by(*groups)

        group_cols = qry.get_group_columns()
        select_cols = qry.get_select_columns()

        self.assertEqual(len(qry.get_lineage()), 3)
        parent_hashes = [hash(p) for p in qry.get_lineage()]
        self.assertIn(hash(self.source.select('^')), parent_hashes)

        self.assertEqual(len(group_cols), 2)

        self.assertEqual(len(select_cols), 10)

        self.assertEqual(len(qry._at_var_dependencies), 0)

    def test_group_by_with_scalar_var_in_group_by_op_col(self):
        groups = [self.source.method, self.source.duration > self.scalar]
        qry = self.source.select(
            '^'
        ).group_by(*groups)

        group_cols = qry.get_group_columns()
        select_cols = qry.get_select_columns()

        self.assertEqual(len(group_cols), 2)
        self.assertEqual(len(select_cols), 10)

        self.assertEqual(len(qry.get_lineage()), 3)
        self.assertEqual(len(qry._at_var_dependencies), 1)

    def test_group_by_with_literal(self):

        source = self.atlas.sys_aws_billing_costanduse()

        with self.assertRaises(TypeError) as te:
            source.select(
                '*'
            ).group_by(
                source.dimension1_value,
                source.dimension2_value,
                'tr_byte_costs'
            )

        self.assertIn("Literals are not allowed", str(te.exception))

    def test_can_chain_aggregate_on_group_by(self):

        agg = self.source.select('^').group_by(
            self.source.method,
            self.source.controller
        ).aggregate(
            MeanDuration=self.source.duration.mean()
        )
        from lumipy.query.expression.table_op.group_aggregate_op import GroupByAggregation
        self.assertEqual(type(agg), GroupByAggregation)
