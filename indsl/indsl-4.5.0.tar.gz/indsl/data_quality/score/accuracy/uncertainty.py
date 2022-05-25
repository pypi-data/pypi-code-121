# Copyright 2021 Cognite AS
from __future__ import annotations

from typing import List, Optional, Tuple

import pandas as pd

from indsl.data_quality import uncertainty_rstd

from ..base import DataQualityScore, DataQualityScoreAnalyser


class UncertaintyDataQualityScoreAnalyser(DataQualityScoreAnalyser):
    @staticmethod
    def _limit_series_to_analysis_period(
        series: pd.Series, analysis_start: pd.Timestamp, analysis_end: pd.Timestamp
    ) -> pd.Series:
        return series[(analysis_start <= series.index) & (series.index <= analysis_end)]

    def compute_score(
        self,
        analysis_start: pd.Timestamp,
        analysis_end: pd.Timestamp,
        threshold=0.02,
        resample_rate: pd.Timedelta = pd.Timedelta("30m"),
        emd_sift_thresh: float = 1e-8,
        emd_max_num_imfs: Optional[int] = None,
        emd_error_tolerance: float = 0.05,
    ) -> DataQualityScore:
        """Compute uncertainty data quality score

        The score measures events where the uncertainty of the time series values is above the user-specified threshold.
        The uncertainty is estimated using the uncertainty_rstd function, the segment size is controlled by the resample_rate parameter.

        Args:
            analysis_start: Analyis start time
            analysis_end: Analyis end time
            threshold (float): Threshold
                Uncertainty values above this threshold are counted as events in the data quality score. Default: 0.02
            resample_rate: Window aggregate
                Perform the uncertainty analysis on aggregate data. Default: 30 minutes
            emd_sift_thresh: Sifting threshold
                Threshold to stop EMD sifting process. This threshold is based on the Cauchy convergence test and represent the
                residue between two consecutive oscillatory components (IMFs). A small threshold (close to zero) will
                result in more components extracted. Typically, a few IMFs are enough to build the main trend. Choosing a
                high threshold might not affect the outcome. Defaults to 1e-8.
            emd_max_num_imfs: Maximum number of components
                Maximum number of EMD oscillatory components (or IMFs) to estimate the main trend. If no value (None) is defined
                the process continues until sifting threshold is reached. Defaults to None.
            emd_error_tolerance: Energy tolerance
                Threshold for the EMD cross energy ratio validation used for choosing oscillatory components or IMFs. Defaults to
                0.05.

        Returns:
            DataQualityScore: Data quality score
        """

        if len(self.series) < 10:
            return DataQualityScore(analysis_start, analysis_end, [])

        relative_std_deviation = uncertainty_rstd(
            self.series, resample_rate, emd_sift_thresh, emd_max_num_imfs, emd_error_tolerance
        )

        event_marker_resampler = (relative_std_deviation > threshold).resample(resample_rate, origin="start")
        events_series = event_marker_resampler.sum() / event_marker_resampler.count()
        events_series = events_series[events_series > 0]
        events = self._convert_marker_series_to_event_list(events_series, resample_rate, analysis_start, analysis_end)
        score = DataQualityScore(analysis_start, analysis_end, events)

        return score

    @staticmethod
    def _plot(series, estimated_truth, events, score):
        from matplotlib import pyplot as plt

        _, ax1 = plt.subplots()
        ax1.plot(series, label="Signal with noise")
        ax1.plot(estimated_truth, label="Estimated truth")

        for start, stop in events:
            plt.axvspan(start, stop, color="red", alpha=0.5, zorder=10)

        plt.title(f"Uncertainty score: {score.data_quality_score:.4f}")

        plt.show()

    @staticmethod
    def _convert_marker_series_to_event_list(
        events_series: pd.Series,
        window_aggregate: pd.Timedelta,
        analysis_start: pd.Timestamp,
        analysis_end: pd.Timestamp,
    ) -> List[Tuple[pd.Timestamp, pd.Timestamp]]:

        # Create initial list of events
        def limit_to_analysis_period(timestamp):
            return min(max(timestamp, analysis_start), analysis_end)

        events = [
            (limit_to_analysis_period(event_start), limit_to_analysis_period(event_start + window_aggregate))
            for event_start in events_series.index
        ]

        # Remove empty events
        events = [(start, end) for start, end in events if end - start > pd.Timedelta(0)]

        # Merge contiguous events
        merged_events: List[List[pd.Timestamp]] = []
        for event_start, event_end in events:

            if len(merged_events) > 0 and event_start == merged_events[-1][1]:
                merged_events[-1][1] = event_end
            else:
                merged_events.append([event_start, event_end])

        return [tuple(event) for event in merged_events]  # type: ignore
