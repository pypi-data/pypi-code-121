import unittest

from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


class TestColumnBinaryScalarOp(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.appreq = self.atlas.lusid_logs_apprequest()
        self.rtrace = self.atlas.lusid_logs_requesttrace()
        self.test_text_col = self.appreq.request_id
        self.test_double_col = self.appreq.duration
        self.test_int_col = self.appreq.error_code.cast(int)
        self.maxDiff = 10000

    def test_is_in_with_subquery(self):

        other = self.appreq.select(self.appreq.request_id).where(
            self.appreq.duration > 1000
        ).to_table_var('other')

        is_in_sql = self.appreq.request_id.is_in(other.select(other.request_id)).get_sql()
        self.assertEqual(
            standardise_sql_string(is_in_sql),
            "[RequestId] IN (SELECT [RequestId] FROM @other)"
        )

        qry_sql = self.appreq.select('^').where(
            self.appreq.request_id.is_in(
                other.select(other.request_id)
            )
        ).get_sql()
        self.assertEqual(
            standardise_sql_string(qry_sql),
            "@other = SELECT [RequestId] FROM [Lusid.Logs.AppRequest] WHERE ([Duration] > 1000); SELECT [Application], "
            "[Client], [Controller], [Duration], [EventType], [Method], [RequestId], [StatusCode], [Timestamp], [User] "
            "FROM [Lusid.Logs.AppRequest] WHERE ([RequestId] IN (SELECT [RequestId] FROM @other))"
        )

    def test_automatic_parentheses(self):

        duration = self.appreq.duration
        test = (duration + 1) + 100
        test_sql = test.get_sql()

        self.assertEqual(test_sql, '([Duration] + 1) + 100')

    def test_membership_container(self):

        from lumipy.query.expression.column.collection import CollectionExpression

        container1 = CollectionExpression(self.appreq.select(self.appreq.duration))
        container1_sql = container1.get_sql()
        self.assertEqual(
            standardise_sql_string(container1_sql),
            standardise_sql_string("(SELECT [Duration] FROM [Lusid.Logs.AppRequest])")
        )

        container2 = CollectionExpression(*["a", "b", "c"])
        container2_sql = container2.get_sql()

        self.assertEqual(container2_sql, "('a', 'b', 'c')")

    def test_is_in_prefixing_reconstruction_with_subquery(self):

        appreq_alias = self.appreq.with_alias('test')
        rtrace_alias = self.rtrace.with_alias('RT')

        is_in = self.appreq.application.is_in(['shrine', 'lusid'])
        prfx_is_in = appreq_alias.apply_prefix(is_in)

        sql_prfx_is_in = prfx_is_in.get_sql()
        self.assertEqual(sql_prfx_is_in, "test.[Application] IN ('shrine', 'lusid')")

        rids = self.appreq.select('*').where(self.appreq.duration > 10000).to_table_var('rids').with_alias('RIDS')

        cndn = self.rtrace.request_id.is_in(rids.select(rids.request_id))
        prfx_cndn = rids.apply_prefix(rtrace_alias.apply_prefix(cndn))

        prfx_cndn_sql = prfx_cndn.get_sql()
        self.assertEqual(
            standardise_sql_string(prfx_cndn_sql),
            standardise_sql_string('RT.[RequestId] IN (SELECT RIDS.[RequestId] FROM @rids AS RIDS)')
        )

    def test_degenerate_expression_args_bug_is_fixed(self):

        provider1 = self.atlas.lusid_logs_apprequest()
        provider2 = self.atlas.lusid_logs_apprequest()
        v1 = provider1.duration / 2
        v2 = provider2.duration / 2

        v3 = v1 + v2
        self.assertEqual(v3.get_sql(), f"({v1.get_sql()}) + ({v2.get_sql()})")
