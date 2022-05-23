import datetime as dt

import lumipy as lm
from test.integration.base_intergration_test import BaseIntegrationTest


class TestWindowFunction(BaseIntegrationTest):
    """Integration tests for window functions

    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.ar = cls.atlas.lusid_logs_apprequest(
            start_at=dt.datetime.utcnow() - dt.timedelta(days=1)
        )

    def test_cumulative_fns_match_pandas(self):

        qry = self.ar.select(
            self.ar.timestamp, self.ar.duration,
            CumeSum=self.ar.duration.cume.sum(),
            CumeMin=self.ar.duration.cume.min(),
            CumeMax=self.ar.duration.cume.max(),
        ).where(
            (self.ar.application == 'lusid')
            & (self.ar.method == 'UpsertInstruments')
        ).limit(100)

        df = qry.go()

        df['PdCumeSum'] = df.Duration.cumsum()
        df['PdCumeMax'] = df.Duration.cummax()
        df['PdCumeMin'] = df.Duration.cummin()

        self.assertSequenceEqual(df.PdCumeSum.round(9).tolist(), df.CumeSum.round(9).tolist())
        self.assertSequenceEqual(df.PdCumeMin.round(9).tolist(), df.CumeMin.round(9).tolist())
        self.assertSequenceEqual(df.PdCumeMax.round(9).tolist(), df.CumeMax.round(9).tolist())

    def test_frac_diff_matches_pandas(self):
        qry = self.ar.select(
            self.ar.timestamp, self.ar.duration,
            FracDiff=self.ar.duration.frac_diff(),
            FracDiffN3=self.ar.duration.frac_diff(offset=3),
        ).where(
            (self.ar.application == 'lusid')
            & (self.ar.method == 'UpsertInstruments')
            & (self.ar.event_type == 'Completed')
        ).limit(100)

        df = qry.go()

        df['PdFracDiff'] = df.Duration.pct_change()
        df['PdFracDiffN3'] = df.Duration.pct_change(periods=3)

        self.assertSequenceEqual(
            df.PdFracDiff.round(9).tolist()[1:],
            df.FracDiff.round(9).tolist()[1:],
        )

        self.assertSequenceEqual(
            df.PdFracDiffN3.round(9).tolist()[3:],
            df.FracDiffN3.round(9).tolist()[3:],
        )

    def test_drawdown_matches_pandas(self):

        win = lm.window()
        qry = self.ar.select(
            self.ar.timestamp, self.ar.duration,
            Drawdown=win.finance.drawdown(self.ar.duration)
        ).where(
            (self.ar.application == 'lusid')
            & (self.ar.method == 'UpsertInstruments')
            & (self.ar.event_type == 'Completed')
        ).limit(100)

        df = qry.go()

        df['PdDrawdown'] = abs(df.Duration - df.Duration.cummax()) / df.Duration.cummax()
        df = df.iloc[1:]
        self.assertSequenceEqual(
            df.PdDrawdown.round(9).tolist(),
            df.Drawdown.round(9).tolist(),
        )

    def test_cume_dist_matches_pandas(self):

        qry = self.ar.select(
            self.ar.timestamp, self.ar.duration,
            CumeDist=self.ar.duration.cume.dist()
        ).where(
            (self.ar.application == 'lusid')
            & (self.ar.method == 'UpsertInstruments')
            & (self.ar.event_type == 'Completed')
        ).limit(100)

        df = qry.go()
        df['PdCumeDist'] = df.Duration.rank(pct=True, method='max')

        self.assertSequenceEqual(
            df.CumeDist.round(9).tolist(),
            df.PdCumeDist.round(9).tolist(),
        )
