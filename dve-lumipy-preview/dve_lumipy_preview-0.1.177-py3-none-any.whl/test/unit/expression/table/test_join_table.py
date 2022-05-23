import unittest
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string
from datetime import datetime, timedelta


# noinspection PyPep8Naming
class TestJoinTableClass(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()

    def test_inner_join_construction_two_providers(self):

        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        rhs = RTrace()

        join = lhs.inner_join(rhs, on=rhs.request_id == lhs.request_id)
        join_col_names = [c.get_name() for c in join.get_columns()]
        input_col_names = [c.get_name() for c in lhs.get_columns() + rhs.get_columns()]
        join_missing = [n for n in join_col_names if n not in input_col_names]
        input_missing = [n for n in input_col_names if n not in join_col_names]
        self.assertEqual(
            len(join_col_names), len(input_col_names),
            msg=f"Columns set mismatch between join table and it's rhs/lhs "
                f"parents: ({', '.join(join_missing)}) ({', '.join(input_missing)})."
        )

        col_hashes = [hash(c) for c in join.get_columns()]
        missing_cols = [c for c in join.select('*').get_columns() if hash(c) not in col_hashes]
        self.assertEqual(
            len(missing_cols), 0,
            msg=f'Missing columns in select * on join. ({",".join(c.get_sql() for c in missing_cols)})'
        )

        # Test Default Prefixes
        join_sql = join.select('*').get_sql()
        for col in lhs.get_columns():
            prefixed_col = f'lhs.{col.get_sql()}'
            self.assertTrue(prefixed_col in join_sql, msg=f"{prefixed_col} not found in join table SQL string.")
        for col in rhs.get_columns():
            prefixed_col = f'rhs.{col.get_sql()}'
            self.assertTrue(prefixed_col in join_sql, msg=f"{prefixed_col} not found in join table SQL string.")

    def test_inner_join_construction_one_provider_one_table_var(self):

        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        lhs_var = lhs.select('*').where(lhs.duration > 100).to_table_var("test_var")
        rhs = RTrace()

        join = lhs_var.inner_join(
            rhs,
            on=rhs.request_id == lhs_var.request_id
        )
        join_col_names = [c.get_name() for c in join.get_columns()]
        input_col_names = [c.get_name() for c in lhs.get_columns() + rhs.get_columns()]
        join_missing = [n for n in join_col_names if n not in input_col_names]
        input_missing = [n for n in input_col_names if n not in join_col_names]
        self.assertEqual(
            len(join_col_names), len(input_col_names),
            msg=f"Columns set mismatch between join table and it's rhs/lhs "
                f"parents: ({', '.join(join_missing)}) ({', '.join(input_missing)})."
        )

        col_hashes = [hash(c) for c in join.get_columns()]
        missing_cols = [c for c in join.select('*').get_columns() if hash(c) not in col_hashes]
        self.assertEqual(
            len(missing_cols), 0,
            msg=f'Missing columns in select * on join. ({",".join(c.get_sql() for c in missing_cols)})'
        )

        # Test Default Prefixes
        join_sql = join.select('*').get_sql()
        for col in lhs.get_columns():
            prefixed_col = f'lhs.{col.get_sql()}'
            self.assertTrue(prefixed_col in join_sql, msg=f"{prefixed_col} not found in join table SQL string.")
        for col in rhs.get_columns():
            prefixed_col = f'rhs.{col.get_sql()}'
            self.assertTrue(prefixed_col in join_sql, msg=f"{prefixed_col} not found in join table SQL string.")

    def test_inner_join_select(self):

        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        rhs = RTrace()

        join = lhs.inner_join(rhs, on=rhs.request_id == lhs.request_id)

        select_main = join.select('^')
        # Check all the expected columns are present and only those
        mains = [c for c in lhs.get_columns() if c.is_main()]
        mains += [c for c in rhs.get_columns() if c.is_main()]
        self.assertEqual(
            len(select_main.get_columns()),
            len(mains)
        )

        # Check duplicates are handled correctly (request_id and duration)
        self.assertIn("duration_rhs", [c.get_name() for c in select_main.get_columns()])
        self.assertIn("request_id_rhs", [c.get_name() for c in select_main.get_columns()])

        select_star = join.select('*')
        # Check all of the columns are present
        all_cols = lhs.get_columns() + rhs.get_columns()
        self.assertEqual(len(select_star.get_columns()), len(all_cols))
        # Check duplicates are handled correctly (request_id and duration)
        self.assertIn("duration_rhs", [c.get_name() for c in select_star.get_columns()])
        self.assertIn("request_id_rhs", [c.get_name() for c in select_star.get_columns()])

        # Test select with parent table columns
        select_parent_col = join.select(
            lhs.request_id,
            rhs.request_id,
            lhs.duration,
            rhs.duration,
            rhs.self_time,
            lhs.method,
            lhs.application
        )
        # Check duplicates are handled correctly (request_id and duration)
        self.assertIn("duration_rhs", [c.get_name() for c in select_parent_col.get_columns()])
        self.assertIn("request_id_rhs", [c.get_name() for c in select_parent_col.get_columns()])
        # Check all of the columns are present
        self.assertEqual(len(select_parent_col.get_columns()), 7)

        # Test select with explicit columns equivalent to the above
        select_join_col = join.select(
            join.request_id_lhs,
            join.request_id_rhs,
            join.duration_lhs,
            join.duration_rhs,
            join.self_time,
            join.method,
            join.application
        )
        # Check all of the columns are present
        self.assertEqual(len(select_join_col.get_columns()), 7)

        # Assert that they resolve to the same sql string
        self.assertEqual(
            select_parent_col.get_sql(), select_join_col.get_sql(),
            msg="Select on Join table using equivalent columns from join table or parents resolved to different SQL."
        )

        # All of the following should work...
        self.assertTrue(join.contains_column(rhs.duration))
        self.assertTrue(join.contains_column(lhs.duration))
        self.assertTrue(join.contains_column(join.duration_lhs))
        self.assertTrue(join.contains_column(join.duration_rhs))

    def test_inner_join_select_aggregates(self):

        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        rhs = RTrace()

        join = lhs.inner_join(rhs, on=rhs.request_id == lhs.request_id)

        # Test aggregates and scalar expression of columns
        join_select_aggregates = join.select(
            duration_min_lhs=join.duration_lhs.min(),
            duration_min_rhs=join.duration_rhs.min()
        )
        self.assertEqual(len(join_select_aggregates.get_columns()), 2)
        join_col_sql_str = join_select_aggregates.get_sql()
        self.assertIn('AS [duration_min_rhs]', join_col_sql_str)

        join_select_aggregates_via_parents = join.select(
            duration_min_lhs=lhs.duration.min(),
            duration_min_rhs=rhs.duration.min()
        )
        self.assertEqual(len(join_select_aggregates_via_parents.get_columns()), 2)
        parent_col_sql_str = join_select_aggregates_via_parents.get_sql()
        self.assertIn('AS [duration_min_rhs]', parent_col_sql_str)

        self.assertEqual(join_select_aggregates.get_sql(), join_select_aggregates_via_parents.get_sql())

    def test_inner_join_where(self):

        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        rhs = RTrace()

        join = lhs.inner_join(rhs, on=rhs.request_id == lhs.request_id)

        select_main = join.select('^')

        complex_where_join_cols = select_main.where(
            (join.duration_lhs > 1000) &
            join.application.is_in(['lusid', 'shrine']) &
            (join.self_time > 500) &
            (join.duration_rhs > 1000)
        )
        complex_where_main = select_main.where(
            (lhs.duration > 1000) &
            lhs.application.is_in(['lusid', 'shrine']) &
            (rhs.self_time > 500) &
            (rhs.duration > 1000)
        )
        # Where using parent table columns and join table columns should match
        self.assertEqual(
            standardise_sql_string(complex_where_join_cols.get_sql()),
            standardise_sql_string(complex_where_main.get_sql())
        )

    def test_inner_join_order_by(self):

        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        rhs = RTrace()

        join = lhs.inner_join(rhs, on=rhs.request_id == lhs.request_id)

        select_main = join.select('^')

        # Test order by with join cols
        # Simple single order by
        order_by_join_col_asc = select_main.order_by(join.duration_lhs.ascending())
        order_by_join_col_desc = select_main.order_by(join.duration_lhs.descending())
        # Multiple simple order by
        multi_order_by_join_col_asc = select_main.order_by(join.duration_lhs.ascending(), join.duration_rhs.ascending())

        # Order by with a derived column
        derived = (join.duration_rhs - join.self_time) / join.duration_lhs
        derived_order_by_join_cols = select_main.order_by(
            derived.ascending()
        )

        # Test order by with parent cols
        order_by_parent_col_asc = select_main.order_by(lhs.duration.ascending())
        order_by_parent_col_desc = select_main.order_by(lhs.duration.descending())
        # Multiple simple order by
        multi_order_by_parent_col_asc = select_main.order_by(lhs.duration.ascending(), rhs.duration.ascending())

        # Order by with a derived column
        derived = (rhs.duration - rhs.self_time) / lhs.duration
        derived_order_by_parent_cols = select_main.order_by(
            derived.ascending()
        )

        self.assertEqual(order_by_join_col_asc.get_sql(), order_by_parent_col_asc.get_sql())
        self.assertEqual(order_by_join_col_desc.get_sql(), order_by_parent_col_desc.get_sql())
        self.assertEqual(multi_order_by_join_col_asc.get_sql(), multi_order_by_parent_col_asc.get_sql())
        self.assertEqual(derived_order_by_join_cols.get_sql(), derived_order_by_parent_cols.get_sql())

    def test_inner_join_group_and_aggregate(self):

        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        rhs = RTrace()

        join = lhs.inner_join(rhs, on=rhs.request_id == lhs.request_id)

        group_by = join.select('^', TrBytes='tr_bytes').group_by(join.function_name, join.method)

        aggregate = group_by.aggregate(
            SumSelfTime=join.self_time.sum(),
            MeanApiDuration=join.duration_lhs.mean(),
            MeanChildTime=(join.duration_rhs - join.self_time).mean()
        )
        self.assertEqual(
            len(aggregate.get_columns()),
            21
        )

    def test_inner_join_group_and_aggregate_with_table_var(self):

        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        rhs = RTrace()

        rids = lhs.select('*').where(lhs.duration > 1000).to_table_var('rids')

        join_qry = rids.inner_join(
            rhs,
            on=rids.request_id == rhs.request_id
        ).select('^').group_by(
            rhs.function_name
        ).aggregate(
            SumSelfTime=rhs.self_time.sum(),
            MeanChildTime=(rhs.duration - rhs.self_time).mean()
        )

        sql = join_qry.get_sql()
        self.assertIn('SumSelfTime', sql)
        self.assertIn('MeanChildTime', sql)
        self.assertIn(
            "GROUP BY rhs.[FunctionName]",
            standardise_sql_string(sql)
        )
        self.assertEqual(
            len(join_qry.get_columns()),
            19
        )

    def test_self_join_with_aliases(self):

        rtrace = self.atlas.lusid_logs_requesttrace()

        rt1 = rtrace.with_alias('lhs')
        rt2 = rtrace.with_alias('rhs')

        join_table = rt1.inner_join(
            rt2,
            on=(rt1.thread_id == rt2.thread_id) & (rt1.parent_call_id == rt2.call_id)
        )
        qry = join_table.select(rt1.request_id, rt1.function_name, rt2.function_name)

        self.assertEqual(len(qry.get_columns()), 3)

        sql_str = standardise_sql_string(qry.get_sql())
        self.assertEqual(
            'SELECT lhs.[RequestId] AS [RequestId_lhs], lhs.[FunctionName] AS [FunctionName_lhs], rhs.[FunctionName] '
            'AS [FunctionName_rhs] FROM [Lusid.Logs.RequestTrace] AS lhs INNER JOIN [Lusid.Logs.RequestTrace] AS rhs '
            'ON (lhs.[ThreadId] = rhs.[ThreadId]) AND (lhs.[ParentCallId] = rhs.[CallId])',
            sql_str
        )

        self.assertTrue(join_table._is_self_join)

    def test_self_join_error_without_aliases(self):

        rtrace = self.atlas.lusid_logs_requesttrace()

        with self.assertRaises(ValueError) as ve:
            join = rtrace.inner_join(
                rtrace,
                on=rtrace.call_id == rtrace.parent_call_id
            )

    def test_self_join_with_aliases_unprefixed_error(self):

        rtrace = self.atlas.lusid_logs_requesttrace()

        rt1 = rtrace.with_alias('lhs')
        rt2 = rtrace.with_alias('rhs')

        join_table = rt1.inner_join(
            rt2,
            on=(rt1.thread_id == rt2.thread_id) & (rt1.parent_call_id == rt2.call_id)
        )

        # Test the on check works
        with self.assertRaises(ValueError) as ve:
            join_table = rt1.inner_join(
                rt2,
                on=(rtrace.thread_id == rtrace.thread_id) & (rtrace.parent_call_id == rtrace.call_id)
            )
        self.assertIn("must be prefixed", str(ve.exception))

        # Test select check works
        with self.assertRaises(ValueError) as ve:
            join_table.select(
                rt1.request_id, rt1.function_name, rt2.function_name,
                rtrace.self_time, rtrace.thread_id
            )
        self.assertIn("must be prefixed", str(ve.exception))

        sel = join_table.select(
            rt1.request_id, rt1.function_name, rt2.function_name,
        )
        # Test where check works
        with self.assertRaises(ValueError) as ve:
            sel.where(
                (rtrace.self_time - rtrace.duration) / rtrace.duration > 0.5
            )
        self.assertIn("must be prefixed", str(ve.exception))

        where = sel.where(
            (rt2.self_time - rt2.duration) / rt2.duration > 0.5
        )
        # Test groupby check works
        with self.assertRaises(ValueError) as ve:
            where.group_by(
                rtrace.function_name
            )
        self.assertIn("must be prefixed", str(ve.exception))

    def test_self_join_overwrite_bug_fixed(self):

        rtrace = self.atlas.lusid_logs_requesttrace()
        lhs = rtrace.with_alias('LHS')
        rhs = rtrace.with_alias('RHS')

        req_id = '0HM3R52M8C342:00000009'
        condition = (rhs.request_id == req_id) & (lhs.request_id == req_id)

        join = lhs.inner_join(
            rhs,
            on=(rhs.call_id == lhs.parent_call_id) & (rhs.thread_id == lhs.thread_id)
        ).select('^').where(
            condition
        )

        join_sql = standardise_sql_string(join.get_sql())
        condition_sql = standardise_sql_string(condition.get_sql())

        self.assertIn(condition_sql, join_sql)

    def test_chained_joins_auto_aliased_tables_fails(self):

        h = self.atlas.lusid_portfolio_holding(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        )
        i = self.atlas.lusid_instrument(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        )
        p = self.atlas.lusid_property(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        )

        with self.assertRaises(ValueError) as ve:
            h.left_join(
                i,
                on=i.lusid_instrument_id == h.lusid_instrument_id
            ).left_join(
                p,
                on=(p.domain == 'Instrument') &
                   (p.entity_id_type == 'LusidInstrumentId') &
                   (p.entity_id == h.lusid_instrument_id) &
                   (p.property_scope == h.portfolio_scope)
            )

    def test_chained_joins_auto_aliased_explicit_arg(self):

        h = self.atlas.lusid_portfolio_holding(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        )
        i = self.atlas.lusid_instrument(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        )
        p = self.atlas.lusid_property(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        )

        chain_join = h.left_join(
            i,
            on=i.lusid_instrument_id == h.lusid_instrument_id
        ).left_join(
            p,
            on=(p.domain == 'Instrument') &
               (p.entity_id_type == 'LusidInstrumentId') &
               (p.entity_id == h.lusid_instrument_id) &
               (p.property_scope == h.portfolio_scope),
            right_alias='rhs_2'
        )
        qry = chain_join.select('*')

        self.assertEqual(len(qry.get_columns()), len(h.get_columns()) + len(i.get_columns()) + len(p.get_columns()))
        qry_sql = qry.get_sql()
        self.assertEqual(qry_sql.count('LEFT JOIN'), 2)

    def test_chained_joins_with_pre_aliased_tables(self):

        h = self.atlas.lusid_portfolio_holding(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        ).with_alias('h')
        i = self.atlas.lusid_instrument(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        ).with_alias('i')
        p = self.atlas.lusid_property(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        ).with_alias('p')

        chain_join = h.left_join(
            i,
            on=i.lusid_instrument_id == h.lusid_instrument_id
        ).left_join(
            p,
            on=(p.domain == 'Instrument') &
               (p.entity_id_type == 'LusidInstrumentId') &
               (p.entity_id == h.lusid_instrument_id) &
               (p.property_scope == h.portfolio_scope)
        )

        qry = chain_join.select('*')

        self.assertEqual(len(qry.get_columns()), len(h.get_columns()) + len(i.get_columns()) + len(p.get_columns()))
        qry_sql = qry.get_sql()
        self.assertEqual(qry_sql.count('LEFT JOIN'), 2)

    def test_join_of_joins(self):

        h = self.atlas.lusid_portfolio_holding(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        ).with_alias('h')
        i = self.atlas.lusid_instrument(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        ).with_alias('i')
        p = self.atlas.lusid_property(
            effective_at=datetime(2021, 3, 1),
            as_at=datetime(2021, 3, 8)
        ).with_alias('p')
        s = self.atlas.lusid_scope().with_alias('s')

        join1 = s.left_join(
            h,
            on=s.scope == h.portfolio_scope
        )

        join2 = i.left_join(
            p,
            on=(p.domain == 'Instrument') &
               (p.entity_id_type == 'LusidInstrumentId') &
               (p.entity_id == i.lusid_instrument_id)
        )

        with self.assertRaises(TypeError):
            join2.left_join(
                join1,
                on=h.lusid_instrument_id == i.lusid_instrument_id
            )

    def test_join_ignore_table_variable_lineage(self):
        RTrace = self.atlas.lusid_logs_requesttrace
        AppReq = self.atlas.lusid_logs_apprequest

        end_at = datetime.utcnow()
        lhs = AppReq(start_at=end_at - timedelta(days=1), end_at=end_at)
        rhs = RTrace()

        # When we create a join
        join1 = lhs.inner_join(rhs, on=rhs.request_id == lhs.request_id)
        # and then create two table vars from it
        tv_lhs = join1.select('*').where(rhs.function_name.like('function1.%')).to_table_var('tv_lhs')
        tv_rhs = join1.select('^').where(rhs.function_name.like('function2.%')).to_table_var('tv_rhs')

        # When we try to join these two table variables the join alias check should now ignore the aliased tables in
        # table var ancestry and the join should be build successfully.
        join2 = tv_lhs.inner_join(
            tv_rhs,
            on=tv_lhs.parent_call_id == tv_rhs.call_id
        )
        # Column aliases should also be handled correctly to avoid degeneracies when only one side gets renamed
        self.assertTrue(hasattr(join2, 'duration_rhs_rhs'))
        self.assertTrue(hasattr(join2, 'duration_lhs_rhs'))
        self.assertTrue(hasattr(join2, 'duration_rhs_lhs'))
        self.assertTrue(hasattr(join2, 'duration_lhs_lhs'))
