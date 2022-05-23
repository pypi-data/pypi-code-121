import unittest
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string, test_prefix_insertion
from lumipy.query.expression.window.over import window


class TestColumnFunctionMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.ar = self.atlas.lusid_logs_apprequest()
        self.win = window(
            groups=[self.ar.application, self.ar.method],
            orders=[self.ar.timestamp.ascending()],
        )
        self.maxDiff = 10000

    def test_column_fn_method_happy_path(self):

        from test.unit.expression.column_op.method_test_cases.finance import finance_method_cases_happy
        from test.unit.expression.column_op.method_test_cases.stats import stats_method_cases_happy
        from test.unit.expression.column_op.method_test_cases.cume import cume_method_cases_happy
        from test.unit.expression.column_op.method_test_cases.metric import metric_method_cases_happy
        from test.unit.expression.column_op.method_test_cases.linreg import linreg_method_cases_happy
        from test.unit.expression.column_op.method_test_cases.main import main_method_cases_happy
        from test.unit.expression.column_op.method_test_cases.operator import operator_cases_happy
        from test.unit.expression.column_op.method_test_cases.string import str_method_cases_happy
        from test.unit.expression.column_op.method_test_cases.datetime import datetime_method_cases_happy

        col1 = self.ar.duration
        col2 = self.ar.timestamp
        test_cases = {
            **operator_cases_happy,
            **main_method_cases_happy,
            **linreg_method_cases_happy,
            **metric_method_cases_happy,
            **cume_method_cases_happy,
            **stats_method_cases_happy,
            **finance_method_cases_happy,
            **str_method_cases_happy,
            **datetime_method_cases_happy,
        }

        for label, (fn, exp_sql_fn) in test_cases.items():
            with self.subTest(msg=label):

                expression = fn(col1, col2)

                exp_sql = standardise_sql_string(exp_sql_fn(col1, col2))
                obs_sql = standardise_sql_string(expression.get_sql())
                self.assertEqual(obs_sql, exp_sql, msg=f'Mismatch in SQL for column fn test: {label}')

                test_prefix_insertion(self, self.ar, expression)

                qry = self.ar.select('*', test=expression)
                self.assertEqual(hash(qry.test.get_original()), hash(expression))

    def test_column_fn_method_unhappy_path(self):

        from test.unit.expression.column_op.method_test_cases.main import main_method_cases_unhappy
        from test.unit.expression.column_op.method_test_cases.stats import stats_method_cases_unhappy
        from test.unit.expression.column_op.method_test_cases.finance import finance_method_cases_unhappy
        from test.unit.expression.column_op.method_test_cases.string import str_method_cases_unhappy

        col1 = self.ar.duration
        col2 = self.ar.timestamp
        test_cases = {
            **main_method_cases_unhappy,
            **stats_method_cases_unhappy,
            **finance_method_cases_unhappy,
            **str_method_cases_unhappy,
        }

        for label, (fn, ex_type, ex_msg) in test_cases.items():
            with self.subTest(msg=label):
                with self.assertRaises(ex_type) as ex:
                    fn(col1, col2)

                obs_msg = str(ex.exception)
                self.assertEqual(obs_msg, ex_msg(col1, col2))
