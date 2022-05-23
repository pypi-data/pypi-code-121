import unittest

import cufflinks as cf
import pandas as pd

from commodplot import commodplotutil as cpu


class TestCommodPlotUtil(unittest.TestCase):
    def test_delta_summary_str(self):
        df = cf.datagen.lines(2, 1000)
        col = df.columns[0]

        m1 = df.iloc[-1, 0]
        m2 = df.iloc[-2, 0]
        diff = m1 - m2
        res = cpu.delta_summary_str(df)

        self.assertIn(str(m1.round(2)), res)
        self.assertIn(str(diff.round(2)), res)

    def test_gen_title(self):
        df = pd.DataFrame([1, 2, 3], columns=["Test"])

        res = cpu.gen_title(df, title=None)
        self.assertTrue(res.startswith("3"))

        res = cpu.gen_title(df, title="TTitle")
        self.assertTrue(res.startswith("TTitle"))
        self.assertTrue(res.endswith("+1"))

        res = cpu.gen_title(df, title="TTitle", title_postfix="post")
        self.assertTrue(res.startswith("TTitle  post:"))
        self.assertTrue(res.endswith("+1"))


if __name__ == "__main__":
    unittest.main()
