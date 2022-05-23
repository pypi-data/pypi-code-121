import unittest

from lumipy.query.expression.sql_value_type import SqlValType
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


class TestCaseExpression(unittest.TestCase):

    def setUp(self) -> None:

        self.atlas = make_test_atlas()

        self.appreq = self.atlas.lusid_logs_apprequest()
        self.rtrace = self.atlas.lusid_logs_requesttrace()

        self.test_text_col = self.appreq.request_id
        self.test_double_col = self.appreq.duration
        self.test_int_col = self.appreq.error_code.cast(int)

    def test_case_construction(self):

        table = self.appreq
        case = table.when(table.duration < 100).then("quick") \
            .when((table.duration > 100) & (table.duration < 1000)).then("medium") \
            .when((table.duration > 1000) & (table.duration < 5000)).then("long") \
            .otherwise("very long")

        expected = '''(
            CASE
                WHEN [Duration] < 100
                THEN \'quick\'
                WHEN ([Duration] > 100) AND ([Duration] < 1000)
                THEN \'medium\'
                WHEN ([Duration] > 1000) AND ([Duration] < 5000)
                THEN \'long\'
              ELSE \'very long\'
            END
            )'''

        self.assertEqual(
            standardise_sql_string(case.get_sql()),
            standardise_sql_string(expected)
        )

        self.assertEqual(
            case.get_type(),
            SqlValType.Text
        )

    def test_case_default_otherwise(self):
        table = self.appreq
        case = table.when(table.duration < 100).then("quick") \
            .when((table.duration > 100) & (table.duration < 1000)).then("medium") \
            .when((table.duration > 1000) & (table.duration < 5000)).then("long") \
            .otherwise()

        expected = '''(
            CASE
                WHEN [Duration] < 100
                THEN \'quick\'
                WHEN ([Duration] > 100) AND ([Duration] < 1000)
                THEN \'medium\'
                WHEN ([Duration] > 1000) AND ([Duration] < 5000)
                THEN \'long\'
              ELSE null
            END
            )'''

        self.assertEqual(
            standardise_sql_string(case.get_sql()),
            standardise_sql_string(expected)
        )

        self.assertEqual(
            case.get_type(),
            SqlValType.Text
        )

    def test_case_in_select_statement(self):

        table = self.appreq
        case = table.when(table.duration < 100).then("quick")\
            .when((table.duration > 100) & (table.duration < 1000)).then("medium")\
            .when((table.duration > 1000) & (table.duration < 5000)).then("long")\
            .otherwise("very long")

        qry = table.select(table.method, table.request_id, TestCase=case)

        sql_str = qry.get_sql()
        expected = """
            SELECT
              [Method], [RequestId], (  
              CASE
                  WHEN [Duration] < 100
                  THEN 'quick'
                  WHEN ([Duration] > 100) AND ([Duration] < 1000)
                  THEN 'medium'
                  WHEN ([Duration] > 1000) AND ([Duration] < 5000)
                  THEN 'long'
                ELSE 'very long'
              END
            ) AS [TestCase]
            FROM
              [Lusid.Logs.AppRequest]
            """

        self.assertEqual(
            standardise_sql_string(sql_str),
            standardise_sql_string(expected)
        )

    def test_case_in_join_table(self):

        join = self.appreq.inner_join(
            self.rtrace,
            on=self.rtrace.request_id == self.appreq.request_id
        )

        qry = join.select(
            self.rtrace.function_name,
            self.appreq.duration,
            self.rtrace.self_time,
            InternalDurationLabel=join.when(
                ((self.rtrace.self_time/self.appreq.duration) > 0.25) &
                ((self.rtrace.self_time/self.appreq.duration) < 0.50)
            ).then("MoreThanQuarter").when(
                (self.rtrace.self_time / self.appreq.duration) > 0.5
            ).then("MoreThanHalf").otherwise(
                "Smaller"
            ),
        )

        sql_str = qry.get_sql()
        expected = """
            SELECT
              rhs.[FunctionName], 
              lhs.[Duration] AS [Duration_lhs], 
              rhs.[SelfTime], 
              (  
              CASE
                  WHEN ((rhs.[SelfTime] / (cast(lhs.[Duration] AS DOUBLE))) > 0.25) AND ((rhs.[SelfTime] / (cast(lhs.[Duration] AS DOUBLE))) < 0.5)
                  THEN 'MoreThanQuarter'
                  WHEN (rhs.[SelfTime] / (cast(lhs.[Duration] AS DOUBLE))) > 0.5
                  THEN 'MoreThanHalf'
                ELSE 'Smaller'
              END 
            ) AS [InternalDurationLabel]
            FROM
              [Lusid.Logs.AppRequest] AS lhs 
            INNER JOIN
              [Lusid.Logs.RequestTrace] AS rhs
             ON
              rhs.[RequestId] = lhs.[RequestId]
        """
        self.assertEqual(
            standardise_sql_string(sql_str),
            standardise_sql_string(expected)
        )

    def test_case_in_prefix_insertion(self):

        table = self.appreq
        case = table.when(
            table.duration < 100
        ).then(
            "quick"
        ).when(
            (table.duration > 100) & (table.duration < 1000)
        ).then(
            "medium"
        ).when(
            (table.duration > 1000) & (table.duration < 5000)
        ).then(
            "long"
        ).otherwise(
            "very long"
        )

        aliased_table = table.with_alias('test')

        prefixed = aliased_table.apply_prefix(case)

        prfx_sql = prefixed.get_sql()
        expected = """
            (  
              CASE
                  WHEN test.[Duration] < 100
                  THEN 'quick'
                  WHEN (test.[Duration] > 100) AND (test.[Duration] < 1000)
                  THEN 'medium'
                  WHEN (test.[Duration] > 1000) AND (test.[Duration] < 5000)
                  THEN 'long'
                ELSE 'very long'
              END 
            )
        """
        self.assertEqual(
            standardise_sql_string(prfx_sql),
            standardise_sql_string(expected)
        )

    def test_case_then_clause_variants(self):

        # Try with numeric THEN values that are not literals
        table = self.appreq

        getter_mean = 300
        setter_mean = 150
        upsert_mean = 400
        others_mean = 125

        case = table.when(
            table.method.startswith('Get')
        ).then(
            table.duration - getter_mean
        ).when(
            table.method.startswith('Set')
        ).then(
            table.duration - setter_mean
        ).when(
            table.method.startswith('Upsert')
        ).then(
            table.duration - upsert_mean
        ).otherwise(
            table.duration - others_mean
        )

        case_sql = case.get_sql()
        expected = """
        (  
          CASE
              WHEN [Method] LIKE 'Get%'
              THEN [Duration] - 300
              WHEN [Method] LIKE 'Set%'
              THEN [Duration] - 150
              WHEN [Method] LIKE 'Upsert%'
              THEN [Duration] - 400
            ELSE [Duration] - 125
          END
        )
        """
        self.assertEqual(
            standardise_sql_string(case_sql),
            standardise_sql_string(expected)
        )

        self.assertEqual(case.get_type(), SqlValType.Double)
