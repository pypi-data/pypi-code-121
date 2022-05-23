import unittest

import cufflinks as cf
import pandas as pd
import plotly.graph_objects as go
from commodutil import transforms

from commodplot import commodplottrace as cptr


class TestCommodPlotTrace(unittest.TestCase):
    def test_min_max_range(self):
        df = cf.datagen.lines(1, 5000)
        dft = transforms.seasonailse(df)
        res = cptr.min_max_mean_range(dft, shaded_range=5)
        self.assertTrue(isinstance(res[0], pd.DataFrame))
        self.assertTrue(isinstance(res[1], int))

    def test_timeseries_trace(self):
        df = cf.datagen.lines(1, 5000)
        t = cptr.timeseries_trace(df[df.columns[0]])
        self.assertTrue(isinstance(t, go.Scatter))
        self.assertEqual(t.name, df.columns[0])
        self.assertEqual(t.hovertemplate, cptr.hovertemplate_default)

    def test_timeseries_trace_by_year(self):
        df = cf.datagen.lines(1, 5000)
        df = transforms.seasonailse(df)
        colyear = df.columns[-1]
        t = cptr.timeseries_trace_by_year(df[df.columns[-1]], colyear=colyear)
        self.assertTrue(isinstance(t, go.Scatter))
        self.assertEqual(t.name, str(df.columns[-1]))
        self.assertEqual(
            t.visible, cptr.line_visible(colyear)
        )  # line visible should match results of line_visible()
        self.assertEqual(t.line.color, cptr.get_year_line_col(colyear))


if __name__ == "__main__":
    unittest.main()
