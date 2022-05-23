"""Main Module of arcos4py.

This module contains the ARCOS class, which implements most functionallity of arcos4py
to prepare data and to detect and track collective events.

Example:
    >>> from arcos4py import ARCOS
    >>> ts = ARCOS(data,["x"], 'time', 'id', 'meas', 'clTrackID')
    >>> ts.interpolate_measurements()
    >>> ts.clip_meas(clip_low = 0.001, clip_high=0.999)
    >>> ts.bin_measurements(
            smoothK = 3,
            biasK = 51,
            peakThr = 0.2,
            binThr = 0.1,
            polyDeg = 1,
            biasMet = "runmed")
    >>> events_df = ts.trackCollev(eps = 1, minClsz = 1, nPrev = 1)
"""

from typing import Union

import pandas as pd

from .tools.binarize_detrend import binData
from .tools.cleandata import clipMeas, interpolation
from .tools.detect_events import detectCollev


class ARCOS:
    """Detects and tracks collective events in a tracked time-series dataset.

    Requires binarized measurement column, that can be generated with the
    bin_measurements method.
    Tracking makes use of the dbscan algorithm, which is applied to every frame
    and subsequently connects collective events between frames located
    within eps distance of each other.

    Attributes:
        data (DataFrame): Data of tracked time-series in "long format". Can be used to
            acess modified dataframe at any point.
        posCols (list): List containing position column names strings inside data e.g.
            At least one dimension is required.
        frame_column (str): Indicating the frame column in input_data.
        id_column (str): Indicating the track id/id column in input_data.
        measurement_column (str): Indicating the measurement column in input_data.
        clid_column (str): Indicating the column name containing the collective event ids.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        posCols: list = ["x"],
        frame_column: str = 'time',
        id_column: str = 'id',
        measurement_column: str = 'meas',
        clid_column: str = 'clTrackID',
    ) -> None:
        """Constructs class with provided arguments.

        Arguments:
            data (DataFrame): Input Data of tracked time-series in "long format" containing position columns,
                a measurement and an object ID column.
            posCols (list): List ontaining position column names strings inside data e.g.
                At least one dimension is required.
            frame_column (str): Indicating the frame column in input_data.
            id_column (str): Indicating the track id/object id column in input_data.
            measurement_column (str): Indicating the measurement column in input_data.
            clid_column (str): Indicating the column name containing the collective event ids.
        """
        self.data = data
        self.posCols = posCols
        self.frame_column = frame_column
        self.id_column = id_column
        self.measurement_column = measurement_column
        self.clid_column = clid_column

        self.data_binarized: pd.DataFrame = None
        self.tracked_events: pd.DataFrame = None
        self.bin_col: Union[str, None] = None
        # to check if no measurement was provided assign None

        self.data = self.data.sort_values(by=[self.frame_column, self.id_column])
        self._check_col()
        if self.measurement_column is not None:
            self.resc_col = f"{self.measurement_column}.resc"
            self.bin_col = f"{self.measurement_column}.bin"

    def __repr__(self) -> pd.DataFrame:
        """Set __repr___ to return self.data."""
        return repr(self.data)

    def _check_col(self):
        """Checks that self.cols contains all required columns."""
        columns = self.data.columns
        input_columns = [self.frame_column, self.id_column, self.id_column, self.measurement_column]
        input_columns = [col for col in input_columns if col is not None]
        if not all(item in columns for item in input_columns):
            raise ValueError(f"Columns {input_columns} do not match with column in dataframe.")

    def interpolate_measurements(self) -> pd.DataFrame:
        """Interpolates NaN's in place in measurement column.

        Returns:
            Dataframe with interpolated measurement column.
        """
        meas_interp = interpolation(self.data).interpolate()
        self.data = meas_interp
        return self.data

    def clip_meas(self, clip_low: float = 0.001, clip_high: float = 0.999) -> pd.DataFrame:
        """Clip measurement column to upper and lower quantiles defined in clip_low and clip_high.

        Arguments:
            clip_low (float): Lower clipping boundary (quantile).

            clip_high (float): Upper clipping boundary (quantile).

        Returns:
            Dataframe with in place clipped measurement column.
        """
        meas_column = self.data[self.measurement_column].to_numpy()
        meas_clipped = clipMeas(meas_column).clip(clip_low, clip_high)
        self.data[self.measurement_column] = meas_clipped
        return self.data

    def bin_measurements(
        self,
        smoothK: int = 3,
        biasK: int = 51,
        peakThr: float = 0.2,
        binThr: float = 0.1,
        polyDeg: int = 1,
        biasMet: str = "runmed",
    ) -> pd.DataFrame:
        r"""Smooth, de-trend, and binarise the input data.

        First a short-term median filter with size smoothK
        is applied to remove fast noise from the time series.
        If the de-trending method is set to "none",
        smoothing is applied on globally rescaled time series.
        The subsequent de-trending can be performed with a long-term median filter
        with the size biasK {biasMet = "runmed"}
        or by fitting a polynomial of degree polyDeg {biasMet = "lm"}.

        After de-trending,
        if the global difference between min/max is greater than the threshold
        the signal is rescaled to the (0,1) range.
        The final signal is binarised using the binThr threshold

        Arguments:
            smoothK (int): Size of the short-term median smoothing filter.
            biasK (int): Size of the long-term de-trending median filter
            peakThr (float): Threshold for rescaling of the de-trended signal.
            binThr (float): Threshold for binary classification.
            polyDeg (int): Sets the degree of the polynomial for lm fitting.
            biasMet (str): De-trending method, one of ['runmed', 'lm', 'none'].

        Returns:
            DataFrame with detrended/smoothed and binarized measurement column.
        """
        self.data = binData(
            smoothK,
            biasK,
            peakThr,
            binThr,
            polyDeg,
            biasMet,
        ).run(self.data, colMeas=self.measurement_column, colGroup=self.id_column, colFrame=self.frame_column)
        return self.data

    def trackCollev(self, eps: float = 1, minClsz: int = 1, nPrev: int = 1) -> pd.DataFrame:
        """Requires binarized measurement column.

        Makes use of the dbscan algorithm,
        applies this to every timeframe and subsequently connects
        collective events between frames located within eps distance of each other.

        Arguments:
            eps (float): The maximum distance between two samples for one to be considered as in
                the neighbourhood of the other.
                This is not a maximum bound on the distances of points within a cluster.
                Value is also used to connect collective events across multiple frames.
            minClsz (str): The minimum size for a cluster to be identified as a collective event
            nPrev (int): Number of previous frames the tracking
                algorithm looks back to connect collective events

        Returns:
            DataFrame with detected collective events across time.
        """
        self.data = detectCollev(
            self.data,
            eps=eps,
            minClSz=minClsz,
            nPrev=nPrev,
            posCols=self.posCols,
            frame_column=self.frame_column,
            id_column=self.id_column,
            bin_meas_column=self.bin_col,
            clid_column=self.clid_column,
        ).run()

        return self.data
