import unittest
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string
from lumipy import window


class TestWindowPrefixing(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.ar = self.atlas.lusid_logs_apprequest()
        self.rt = self.atlas.lusid_logs_requesttrace()

    def test_auto_prefixing_in_window_fn_frame_only(self):
        ar = self.atlas.lusid_logs_apprequest()
        ar2 = ar.with_alias('TEST')

        duration = ar2.apply_prefix(ar.duration.cume.sum())
        sql = duration.get_sql()

        self.assertEqual(
            standardise_sql_string('''
            total(TEST.[Duration]) OVER(
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )'''),
            standardise_sql_string(sql)
        )

    def test_auto_prefixing_in_window_fn_with_partition(self):
        ar = self.atlas.lusid_logs_apprequest()
        ar2 = ar.with_alias('TEST')

        win_fn = window(groups=[ar.application, ar.method]).mean(ar.duration)

        prfx_win_fn = ar2.apply_prefix(win_fn)
        sql = prfx_win_fn.get_sql()

        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string('''
                avg(TEST.[Duration]) OVER(
                        PARTITION BY TEST.[Application], TEST.[Method]
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    )
                ''')
        )

    def test_auto_prefixing_in_window_fn_with_partition_and_order(self):
        ar = self.atlas.lusid_logs_apprequest()
        ar2 = ar.with_alias('TEST')

        win_fn = window(
            groups=[ar.application, ar.method],
            orders=ar.duration.ascending()
        ).rank()

        prfx_win_fn = ar2.apply_prefix(win_fn)
        sql = prfx_win_fn.get_sql()

        self.assertEqual(
            standardise_sql_string(sql),
            standardise_sql_string('''
                RANK() OVER(
                        PARTITION BY TEST.[Application], TEST.[Method]
                        ORDER BY TEST.[Duration] ASC
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    )
                ''')
        )

    def test_complex_join_window_function_prefixing(self):
        rt = self.atlas.lusid_logs_requesttrace()
        ar = self.atlas.lusid_logs_apprequest()

        tv = ar.select(
            ar.timestamp, ar.duration, ar.request_id
        ).where(
            (ar.application == 'lusid') & (ar.method != '') & (ar.event_type == 'Completed')
        ).limit(1000).to_table_var()

        join = tv.left_join(
            rt,
            on=(rt.request_id == tv.request_id) & (rt.self_time > 0) & (~rt.is_origin_call)
        )

        qry = join.select(
            tv.timestamp, tv.duration, tv.request_id,
            SelfTimeCumeDist=rt.self_time.cume.dist(),
            ForLackOfABetterExample=rt.self_time.cume.dist()*tv.duration.cume.dist()
        )

        sql = standardise_sql_string(qry.get_sql())
        exp_sql = standardise_sql_string('''
            CUME_DIST() OVER(
                    ORDER BY rhs.[SelfTime] ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS [SelfTimeCumeDist], 
            CUME_DIST() OVER(
                    ORDER BY rhs.[SelfTime] ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) * CUME_DIST() OVER(
                    ORDER BY lhs.[Duration] ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS [ForLackOfABetterExample]        
        ''')
        self.assertIn(exp_sql, sql)
