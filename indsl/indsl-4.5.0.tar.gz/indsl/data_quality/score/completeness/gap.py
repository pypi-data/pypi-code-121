# Copyright 2021 Cognite AS
from __future__ import annotations

from typing import Literal, Optional, Union

import pandas as pd

from indsl.data_quality.gaps_identification import (
    gaps_identification_iqr,
    gaps_identification_modified_z_scores,
    gaps_identification_threshold,
    gaps_identification_z_scores,
)
from indsl.type_check import check_types

from ..base import DataQualityScore, DataQualityScoreAnalyser


class GapDataQualityScoreAnalyser(DataQualityScoreAnalyser):
    @check_types
    def __init__(self, series: pd.Series):
        """Gap based data quality scores

        Args:
            series: Series to be analysed

        raises:
            UserValueError: If the series has less than 2 values
            UserValueError: If series has no time index
        """
        super().__init__(series)
        self._gap_detection_methods = {
            "iqr": gaps_identification_iqr,
            "z_scores": gaps_identification_z_scores,
            "modified_z_scores": gaps_identification_modified_z_scores,
            "threshold": gaps_identification_threshold,
        }

    @check_types
    def compute_score(
        self,
        analysis_start: pd.Timestamp,
        analysis_end: pd.Timestamp,
        gap_detection_method: Literal["iqr", "z_scores", "modified_z_scores", "threshold"] = "iqr",
        **gap_detection_options: Optional[Union[pd.Timedelta, int, bool]],
    ) -> DataQualityScore:
        """Compute the gap analysis score

        Args:
            analysis_start: Analyis start time
            analysis_end: Analyis end time
            gap_detection_method: Gap detection method
                Must be one of "iqr", "z_scores", "modified_z_scores"
            gap_detection_options: Arguments to gap detection method
                Provided as a keyword dictionary

        Returns:
            DataQualityScore: A GapDataQualityScore object

        raises:
            UserValueError: If analysis_start < analysis_end
            UserValueError: If the analysis start and end timestamps are outside the range of the series index
        """

        super().compute_score(analysis_start, analysis_end)
        # Treat empty series as one gap
        if len(self.series) == 0:
            return DataQualityScore(analysis_start, analysis_end, [(analysis_start, analysis_end)])

        method = self._gap_detection_methods[gap_detection_method]
        gaps = method(self.series, **gap_detection_options)

        events = self._convert_series_to_events(gaps)
        events = self._filter_events_outside_analysis_period(events, analysis_start, analysis_end)
        # The first and last gap might range outside the analysis period. Let's fix this...
        events = self._limit_first_and_last_events_to_analysis_period(events, analysis_start, analysis_end)

        return DataQualityScore(analysis_start, analysis_end, [tuple(event) for event in events])
