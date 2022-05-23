import unittest
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string, test_prefix_insertion
from lumipy.query.expression.window.over import window
from test.unit.expression.window.method_test_cases.finance import finance_method_cases
from test.unit.expression.window.method_test_cases.linreg import linreg_method_cases
from test.unit.expression.window.method_test_cases.main import main_method_cases
from test.unit.expression.window.method_test_cases.metric import metric_method_cases
from test.unit.expression.window.method_test_cases.stats import stats_method_cases


class TestWindowFunctionMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.ar = self.atlas.lusid_logs_apprequest()
        self.win = window(
            groups=[self.ar.application, self.ar.method],
            orders=[self.ar.timestamp.ascending()],
        )
        self.maxDiff = 10000

    def test_window_fn_methods(self):

        col1 = self.ar.duration
        col2 = self.ar.duration*2

        test_cases = {
            **main_method_cases,
            **stats_method_cases,
            **linreg_method_cases,
            **metric_method_cases,
            **finance_method_cases,
        }

        for k, (fn, exp_fn) in test_cases.items():
            with self.subTest(msg=k):

                expression = fn(self.win, col1, col2)

                exp_sql = standardise_sql_string(exp_fn(self.win, col1, col2))
                obs_sql = standardise_sql_string(expression.get_sql())
                self.assertEqual(obs_sql, exp_sql, msg=f'Mismatch in SQL for window fn test: {k}')

                test_prefix_insertion(self, self.ar, expression)

                qry = self.ar.select('*', test=expression)
                self.assertEqual(hash(qry.test.get_original()), hash(expression))
