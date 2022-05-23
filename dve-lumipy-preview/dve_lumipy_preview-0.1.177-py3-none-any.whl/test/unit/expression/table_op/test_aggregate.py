import unittest
from datetime import datetime

from test.unit.utilities.test_utils import make_test_atlas, assert_locked_lockable, standardise_sql_string
from lumipy.query.expression.column.column_alias import AliasedColumn
from lumipy.query.expression.column_op.base_aggregation_op import BaseAggregateColumn


class TestGroupAggregation(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.atlas = make_test_atlas()
        self.source = self.atlas.lusid_logs_apprequest(
            start_at=datetime(2020, 1, 1),
            end_at=datetime(2020, 1, 2)
        )

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
        )

    def test_aggregate_object_is_immutable(self):
        assert_locked_lockable(self, self.test_agg)

    def test_group_aggregation_op_construction_from_source_table(self):

        agg = self.test_group_by.aggregate(
            MaxTime=self.source.duration.max(),
            MinTime=self.source.duration.min(),
            Count=self.source.duration.count(),
            TotalTime=self.source.duration.sum(),
        )

        self.assertEqual(len(agg.get_columns()), 14)
        member_names = [c.get_name() for c in agg.get_columns()]

        self.assertIn('max_time', member_names)
        self.assertEqual(type(agg.max_time), AliasedColumn)
        self.assertEqual(agg.max_time.get_alias(), 'MaxTime')
        self.assertTrue(issubclass(type(agg.max_time.get_original()), BaseAggregateColumn))

        self.assertIn('min_time', member_names)
        self.assertEqual(type(agg.min_time), AliasedColumn)
        self.assertEqual(agg.min_time.get_alias(), 'MinTime')
        self.assertTrue(issubclass(type(agg.min_time.get_original()), BaseAggregateColumn))

        self.assertIn('count', member_names)
        self.assertEqual(type(agg.count), AliasedColumn)
        self.assertEqual(agg.count.get_alias(), 'Count')
        self.assertTrue(issubclass(type(agg.count.get_original()), BaseAggregateColumn))

        self.assertIn('total_time', member_names)
        self.assertEqual(type(agg.total_time), AliasedColumn)
        self.assertEqual(agg.total_time.get_alias(), 'TotalTime')
        self.assertTrue(issubclass(type(agg.total_time.get_original()), BaseAggregateColumn))

        sql1 = agg.get_sql()
        sql2 = "SELECT [Application], [Client], [Controller], [Duration], [EventType], [Method], [RequestId], [StatusCode], " \
               "[Timestamp], [User], max([Duration]) AS [MaxTime], min([Duration]) AS [MinTime], " \
               "count([Duration]) AS [Count], total([Duration]) AS [TotalTime] FROM  [Lusid.Logs.AppRequest] " \
               "WHERE  [StartAt] = #2020-01-01 00:00:00.000000# AND [EndAt] = #2020-01-02 00:00:00.000000# " \
               "AND (([Duration] > 1000) AND ([Application] = 'lusid')) GROUP BY [Client], [Method]"

        self.assertEqual(
            standardise_sql_string(sql1),
            standardise_sql_string(sql2)
        )

    def test_group_aggregation_op_construction_from_join_table(self):
        atlas = make_test_atlas()

        pods = atlas.sys_kubernetes_pod()
        pod_logs = atlas.sys_kubernetes_podlog()

        restarted = pods.select('*').where(
            pods.restarts > 0
        ).to_table_var('restart_pods')

        agg = restarted.inner_join(
            pod_logs,
            on=restarted.pod_ip == pod_logs.pod_ip
        ).select('*').where(
            pod_logs.message.str.like('%exception%')
        ).group_by(
            restarted.pod_ip
        ).aggregate(
            NumExceptions=restarted.pod_ip.count()
        )

        self.assertEqual(len(agg.get_columns()), 20)

        member_names = [c.get_name() for c in agg.get_columns()]

        self.assertIn('num_exceptions', member_names)
        self.assertEqual(type(agg.num_exceptions), AliasedColumn)
        self.assertEqual(agg.num_exceptions.get_alias(), 'NumExceptions')
        self.assertTrue(issubclass(type(agg.num_exceptions.get_original()), BaseAggregateColumn))

        sql1 = agg.get_sql()
        sql2 = """@restart_pods = 
                    SELECT
                      [Age], [Container], [HostIP], [Name], [Namespace], [NodeName], [PodIP], [Restarts], [StartTime], 
                      [Status], [StatusDetails] 
                    FROM
                      [Sys.Kubernetes.Pod] 
                    WHERE
                      ([Restarts] > 0);


                    SELECT
                      lhs.[Age], lhs.[Container] AS [Container_lhs], lhs.[HostIP] AS [HostIP_lhs], 
                      lhs.[Name] AS [Name_lhs], lhs.[Namespace] AS [Namespace_lhs], lhs.[NodeName], 
                      lhs.[PodIP] AS [PodIP_lhs], lhs.[Restarts], lhs.[StartTime], lhs.[Status] AS [Status_lhs], 
                      lhs.[StatusDetails], rhs.[Container] AS [Container_rhs], rhs.[HostIP] AS [HostIP_rhs], rhs.[Message], 
                      rhs.[Name] AS [Name_rhs], rhs.[Namespace] AS [Namespace_rhs], rhs.[PodIP] AS [PodIP_rhs], 
                      rhs.[Status] AS [Status_rhs], rhs.[Timestamp], count(lhs.[PodIP]) AS [NumExceptions] 
                    FROM
                      @restart_pods AS lhs 
                    INNER JOIN
                      [Sys.Kubernetes.PodLog] AS rhs
                     ON
                      lhs.[PodIP] = rhs.[PodIP] 
                    WHERE
                      (rhs.[Message] LIKE '%exception%') 
                    GROUP BY
                      lhs.[PodIP]"""
        self.assertEqual(standardise_sql_string(sql1), standardise_sql_string(sql2))

    def test_group_aggregation_fail_non_kwargs(self):

        with self.assertRaises(ValueError) as ve:
            self.test_group_by.aggregate(
                self.source.duration.mean()
            )
        msg = str(ve.exception)
        self.assertIn("only takes keyword arguments", msg)

    def test_can_chain_order_by_on_aggregate(self):

        ordering_agg_mem = self.test_agg.order_by(
            self.test_agg.count.ascending()
        )
        ordering_app_req_mem_expr = self.test_agg.order_by(
            self.source.duration.count().ascending()
        )

        from lumipy.query.expression.table_op.order_by_op import OrderedTableExpression
        self.assertEqual(type(ordering_agg_mem), OrderedTableExpression)
        self.assertEqual(type(ordering_app_req_mem_expr), OrderedTableExpression)
        self.assertEqual(ordering_agg_mem.get_sql(), ordering_app_req_mem_expr.get_sql())

    def test_group_aggregation_can_be_limited(self):

        limit = self.test_agg.limit(125)
        from lumipy.query.expression.table_op.limit_op import LimitTableExpression
        self.assertEqual(type(limit), LimitTableExpression)
        self.assertIn('LIMIT 125', standardise_sql_string(limit.get_sql()))

    def test_group_aggregation_column_membership_checking(self):

        other = self.atlas.lusid_logs_requesttrace()

        with self.assertRaises(ValueError) as ve:
            self.test_group_by.aggregate(
                MaxTime=self.source.duration.max(),
                Wrong=other.self_time
            )
        msg = str(ve.exception)
        self.assertIn('SelfTime', msg)
        self.assertIn("not a member of the table", msg)

    def test_can_chain_having_on_aggregate(self):

        filter_agg = self.test_agg.filter(self.test_agg.count > 5)
        having_agg = self.test_agg.having(self.test_agg.count > 5)
        self.assertEqual(filter_agg.get_sql(), having_agg.get_sql())
        from lumipy.query.expression.table_op.having_op import HavingTableExpression
        self.assertEqual(type(filter_agg), HavingTableExpression)
        self.assertEqual(type(having_agg), HavingTableExpression)

    def test_aggregate_with_scalar_var_in_group_by(self):

        agg = self.source.select(
            '^'
        ).where(
            (self.source.duration > 1000) &
            (self.source.application == 'lusid')
        ).group_by(
            self.source.client,
            self.source.method,
            self.source.duration > self.scalar
        ).aggregate(
            MaxTime=self.source.duration.max(),
            MinTime=self.source.duration.min(),
            Count=self.source.duration.count(),
            TotalTime=self.source.duration.sum(),
        )

        self.assertEqual(len(agg._at_var_dependencies), 1)
        self.assertEqual(len(agg.get_lineage()), 5)

    def test_aggregate_with_scalar_var_in_aggregate(self):
        agg = self.source.select(
            '^'
        ).where(
            (self.source.duration > 1000) &
            (self.source.application == 'lusid')
        ).group_by(
            self.source.client,
            self.source.method,
        ).aggregate(
            MaxTime=self.source.duration.max(),
            MinTime=self.source.duration.min(),
            Count=self.source.duration.count(),
            TotalTime=self.source.duration.sum(),
            FracMean=self.source.duration.mean()/self.scalar
        )

        self.assertEqual(len(agg._at_var_dependencies), 1)
        self.assertEqual(len(agg.get_lineage()), 6)

    def test_can_chain_union_on_where(self):
        other = self.test_agg
        union = self.test_agg.union(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(union), RowSetOp)
        self.assertEqual(union._set_op_str, 'union')

    def test_can_chain_union_all_on_where(self):
        other = self.test_agg
        union = self.test_agg.union_all(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(union), RowSetOp)
        self.assertEqual(union._set_op_str, 'union all')

    def test_can_chain_intersect_on_where(self):
        other = self.test_agg
        intersect = self.test_agg.intersect(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(intersect), RowSetOp)
        self.assertEqual(intersect._set_op_str, 'intersect')

    def test_can_chain_exclude_on_where(self):
        other = self.test_agg
        exclude = self.test_agg.exclude(other)
        from lumipy.query.expression.table_op.row_set_op import RowSetOp
        self.assertEqual(type(exclude), RowSetOp)
        self.assertEqual(exclude._set_op_str, 'except')
