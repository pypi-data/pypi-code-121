#######################################################################
#
# Copyright (C) 2022 David Palao
#
# This file is part of PacBioDataProcessing.
#
#  PacBioDataProcessing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBio data processing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

"""These UTs are full of mocks, given the nature of the problem:
we want to check that some library calls are made.
"""

import unittest
from unittest.mock import MagicMock, patch, call

from pandas import Series

from pacbio_data_processing.plots import (
    make_barsplot, make_histogram, make_multi_histogram, make_rolling_history,
    make_continuous_rolled_data
)



@patch("pacbio_data_processing.plots.plt")
class MakeBarsPlotTestCase(unittest.TestCase):
    def test_delegates_important_actions(self, pplt):
        dataframe = MagicMock()
        f = MagicMock()
        ax = MagicMock()
        pplt.subplots.return_value = f, ax

        make_barsplot(dataframe, "my title", "result.png")

        dataframe.plot.bar.assert_called_once_with(rot=0, ax=ax)
        ax.set_title.assert_called_once()
        call_args = ax.set_title.call_args.args
        self.assertIn("my title", call_args)
        pplt.savefig.assert_called_once()
        savefig_args = pplt.savefig.call_args.args
        self.assertIn("result.png", savefig_args)


@patch("pacbio_data_processing.plots.sns")
@patch("pacbio_data_processing.plots.plt")
class MakeHistogramTestCase(unittest.TestCase):
    def test_delegates_important_actions(self, pplt, psns):
        dataframe = MagicMock()
        f = MagicMock()
        ax = MagicMock()
        pplt.subplots.return_value = f, ax

        make_histogram(dataframe, "my title", "result.png")

        psns.histplot.assert_called_once_with(
            data=dataframe, x=dataframe.iloc[:,0], ax=ax
        )
        ax.set_title.assert_called_once()
        call_args = ax.set_title.call_args.args
        self.assertIn("my title", call_args)
        pplt.savefig.assert_called_once()
        savefig_args = pplt.savefig.call_args.args
        self.assertIn("result.png", savefig_args)
        ax.legend.assert_called_once_with()

    def test_legend_not_done_if_disabled(self, pplt, psns):
        dataframe = MagicMock()
        f = MagicMock()
        ax = MagicMock()
        pplt.subplots.return_value = f, ax

        make_histogram(dataframe, "my title", "result.png", legend=False)

        ax.legend.assert_not_called()


@patch("pacbio_data_processing.plots.sns")
@patch("pacbio_data_processing.plots.plt")
class MakeMultiHistogramTestCase(unittest.TestCase):
    def test_delegates_important_actions(self, pplt, psns):
        # Series wont work with comparisons (in the assert):
        data_a = MagicMock() # Series(range(8))
        data_a.mean.return_value = 7
        data_b = MagicMock() # Series(range(10))
        data_b.mean.return_value = 4
        data = {"a": data_a, "b": data_b}
        f = MagicMock()
        ax = MagicMock()
        pplt.subplots.return_value = f, ax
        colors = (3, 7)
        psns.color_palette.return_value = colors

        make_multi_histogram(data, "my title", "result.png")
        psns.histplot.assert_any_call(
            data=data_a,
            label="a (mean length: 7)",
            stat="percent",
            ax=ax,
            kde=True,
            color=3,
            log_scale=(True, False)
        )
        psns.histplot.assert_any_call(
            data=data_b,
            label="b (mean length: 4)",
            stat="percent",
            ax=ax,
            kde=True,
            color=7,
            log_scale=(True, False)
        )
        ax.set_title.assert_called_once()
        call_args = ax.set_title.call_args.args
        self.assertIn("my title", call_args)
        pplt.savefig.assert_called_once()
        savefig_args = pplt.savefig.call_args.args
        self.assertIn("result.png", savefig_args)
        ax.legend.assert_called_once_with(fontsize=16)

    def test_legend_not_done_if_disabled(self, pplt, psns):
        dataframe = MagicMock()
        f = MagicMock()
        ax = MagicMock()
        pplt.subplots.return_value = f, ax

        make_multi_histogram(dataframe, "my title", "result.png", legend=False)

        ax.legend.assert_not_called()


class MakeContinuousRolledDataTestCase(unittest.TestCase):
    def test_returns_expected_dataframe(self):
        missing = {k: 100-2*k for k in range(1, 12)}
        missing.update({13: 45, 14: 50})
        data_sets = [
            {k: 4*k+1 for k in range(12)},
            {k: 3*k for k in range(4, 13)},
            missing
        ]
        expected_results = [
            {
                'coverage': {
                    0: 17.0, 1: 5.0, 2: 9.0, 3: 13.0, 4: 17.0,
                    5: 21.0, 6: 25.0, 7: 29.0, 8: 33.0, 9: 37.0,
                    10: 41.0, 11: 29.0
                }
            },
            {
                'coverage': {
                    4: 21.0, 5: 15.0, 6: 18.0, 7: 21.0, 8: 24.0,
                    9: 27.0, 10: 30.0, 11: 33.0, 12: 27.0
                }
            },
            {
                'coverage': {
                    1: 72.25, 2: 84.5, 3: 95.0, 4: 93.0, 5: 91.0, 6: 89.0,
                    7: 87.0, 8: 85.0, 9: 83.0, 10: 81.0, 11: 60.0, 12: 50.75,
                    13: 43.25, 14: 48.25
                }
            }
        ]
        windows = [3, 3, 4]
        for i, (data, expected, w) in enumerate(zip(data_sets, expected_results, windows)):
            df = make_continuous_rolled_data(data, w)
            self.assertEqual(df.to_dict(), expected, f"case: {i}")

    def test_issue_73(self):
        data = {k: k+3 for k in range(10)}
        df = make_continuous_rolled_data(data, 2)
        self.assertEqual(df.index.name, "positions")


@patch("pacbio_data_processing.plots.make_continuous_rolled_data")
@patch("pacbio_data_processing.plots.sns")
@patch("pacbio_data_processing.plots.plt")
class MakeRollingHistoryTestCase(unittest.TestCase):
    def test_delegates_important_actions(self, pplt, psns, pmake):
        data = {k: 2*k for k in range(1, 10)}
        f = MagicMock()
        ax = MagicMock()
        pplt.subplots.return_value = f, ax

        make_rolling_history(data, "my title", "result.png")

        pmake.assert_called_once_with(data, 1000)

        psns.lineplot.assert_called_once_with(
            data=pmake.return_value,
            x="positions", y="coverage",
            label=f"rolling average (window=1000)",
            ax=ax, ci=None
        )
        ax.set_title.assert_called_once()
        call_args = ax.set_title.call_args.args
        self.assertIn("my title", call_args)
        pplt.savefig.assert_called_once()
        savefig_args = pplt.savefig.call_args.args
        self.assertIn("result.png", savefig_args)
        ax.legend.assert_called_once_with(fontsize=16)

    def test_legend_not_done_if_disabled(self, pplt, psns, pmake):
        data = {1: 0}
        f = MagicMock()
        ax = MagicMock()
        pplt.subplots.return_value = f, ax

        make_rolling_history(data, "my title", "result.png", legend=False)

        ax.legend.assert_not_called()
