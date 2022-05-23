"""Module containing binarization and detrending classes.

Example:
    >>> from arcos4py.tools import binData
    >>> binarizer = binData(biasMet="lm", polyDeg=1)
    >>> data_rescaled = binarizer.run(data, colMeas="ERK_KTR", colGroup="trackID")
"""
import numpy as np
import pandas as pd
from scipy.ndimage import median_filter
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, minmax_scale


class detrender:
    """Smooth and de-trend input data.

    First, a short-term median filter with size smoothK is applied
    to remove fast noise from the time series.
    The subsequent de-trending can be performed with a long-term median filter
    with the size biasK {biasMet = "runmed"}
    or by fitting a polynomial of degree polyDeg {biasMet = "lm"}.

    Attributes:
        smoothK (int): Representing the size of the short-term median smoothing filter.
        biasK (int): Representing the size of the long-term de-trending median filter.
        peakThr (float): Threshold for rescaling of the de-trended signal.
        polyDeg (int): Sets the degree of the polynomial for lm fitting.
        biasMet (str): Indicating de-trending method, one of ['runmed', 'lm', 'none'].
    """

    def __init__(
        self,
        smoothK: int = 3,
        biasK: int = 51,
        peakThr: float = 0.2,
        polyDeg: int = 1,
        biasMet: str = "runmed",
    ) -> None:
        """Smooth and de-trend input data.

        Arguments:
            smoothK (int): Representing the size of the short-term median smoothing filter.
            biasK (int): Representing the size of the long-term de-trending median filter.
            peakThr (float): Threshold for rescaling of the de-trended signal.
            polyDeg (int): Sets the degree of the polynomial for lm fitting.
            biasMet (str): Indicating de-trending method, one of ['runmed', 'lm', 'none'].
        """
        # check if biasmethod contains one of these three types
        biasMet_types = ["runmed", "lm", "none"]
        if biasMet not in biasMet_types:
            raise ValueError(f"Invalid bias method. Expected one of: {biasMet_types}")

        self.smoothK = smoothK
        self.biasK = biasK
        self.peakThr = peakThr
        self.polyDeg = polyDeg
        self.biasMet = biasMet

    def _detrend_runnmed(self, x, filter_size, endrule_mode):
        local_smoothing = median_filter(input=x, size=filter_size, mode=endrule_mode)
        return local_smoothing

    def _detrend_lm(self, x, polynomial_degree):
        x = np.linspace(1, x.size, x.size).astype(int).reshape((-1, 1))
        transformer = PolynomialFeatures(degree=polynomial_degree, include_bias=False)
        data_ = transformer.fit_transform(x)
        model = LinearRegression().fit(X=data_, y=x)
        predicted_value = model.predict(data_)
        return predicted_value

    def _run_detrend(self, x: np.ndarray) -> np.ndarray:
        if x.size:
            local_smoothed = self._detrend_runnmed(x, self.smoothK, "constant")
            if self.biasMet != "none":
                if self.biasMet == "runmed":
                    global_smoothed = self._detrend_runnmed(
                        x=local_smoothed,
                        filter_size=self.biasK,
                        endrule_mode="constant",
                    )
                elif self.biasMet == "lm":
                    global_smoothed = self._detrend_lm(local_smoothed, self.polyDeg)

                local_smoothed = np.subtract(local_smoothed, global_smoothed)
                local_smoothed = np.clip(local_smoothed, 0, None)
                if (local_smoothed.max() - local_smoothed.min()) > self.peakThr:
                    local_smoothed = np.divide(local_smoothed, local_smoothed.max())
                local_smoothed = np.nan_to_num(local_smoothed)
        else:
            local_smoothed = None

        return local_smoothed

    def detrend(self, x: np.ndarray, group_index: int, meas_index: int) -> np.ndarray:
        """Run detrinding on input data.

        The method applies detrending to each group defined in group_col and
        outputs it into the resc_column.

        Arguments:
            x (np.ndarray): Time series data for smoothing.
            group_index (int): Index of id column in x.
            meas_index (int): Index of measurement column in x.

        Returns (np.ndarray): Dataframe containing rescaled column.
        """
        #################################################
        meas_array = x[:, meas_index].astype('float64')
        try:
            group_array = x[:, group_index].astype('int64')
        except ValueError:
            try:
                group_array = x[:, group_index].astype('float64')
            except ValueError:
                group_array = x[:, group_index].astype('U6')

        grouped_array = np.split(meas_array, np.unique(group_array, axis=0, return_index=True)[1][1:])
        out = [self._run_detrend(x) for x in grouped_array]
        out_list = [item for sublist in out for item in sublist]
        return np.array(out_list)


class binData(detrender):
    """Smooth, de-trend, and binarise the input data.

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
    The final signal is binarised using the binThr threshold.

    Attributes:
        smoothK (int): Size of the short-term median smoothing filter.
        biasK (int): Size of the long-term de-trending median filter.
        peakThr (float): Threshold for rescaling of the de-trended signal.
        binThr (float): Threshold for binarizing the de-trended signal.
        polyDeg (int): Sets the degree of the polynomial for lm fitting.
        biasMet (str): De-trending method, one of ['runmed', 'lm', 'none'].
    """

    def __init__(
        self,
        smoothK: int = 3,
        biasK: int = 51,
        peakThr: float = 0.2,
        binThr: float = 0.1,
        polyDeg: int = 1,
        biasMet: str = "runmed",
    ) -> None:
        """Smooth, de-trend, and binarise the input data.

        Arguments:
            smoothK (int): Size of the short-term median smoothing filter.
            biasK (int): Size of the long-term de-trending median filter.
            peakThr (float): Threshold for rescaling of the de-trended signal.
            binThr (float): Threshold for binarizing the de-trended signal.
            polyDeg (int): Sets the degree of the polynomial for lm fitting.
            biasMet (str): De-trending method, one of ['runmed', 'lm', 'none'].
        """
        super().__init__(smoothK, biasK, peakThr, polyDeg, biasMet)
        self.binThr = binThr

    def _rescale_data(self, x: np.ndarray, group_index: int, meas_index: int, feat_range: tuple = (0, 1)) -> np.ndarray:
        grouped_array = np.split(x[meas_index, :], np.unique(x[group_index, :], axis=0, return_index=True)[1][1:])
        out = [minmax_scale(i, feature_range=feat_range) for i in grouped_array]
        rescaled = [item for sublist in out for item in sublist]
        # rescaled = minmax_scale(x[:,1], feature_range=feat_range)
        x[:, meas_index] = rescaled
        return x

    def _bin_data(self, x: np.ndarray) -> np.ndarray:
        bin = (x > self.binThr).astype(np.int_)
        return bin

    def run(self, x: pd.DataFrame, colGroup: str, colMeas: str, colFrame: str) -> pd.DataFrame:
        """Runs binarization and detrending.

        If the bias Method is 'none', first it rescales the data to between [0,1], then
        local smoothing is applied to the measurement by groups, followed by
        binarization.

        If biasMeth is one of ['lm', 'runmed'], first the data is detrended locally with a
        median filter and then detrended globally, for 'lm' with a linear model and for 'runmed' with a
        median filter.
        Followed by binarization of the data.

        Arguments:
            x (DataFrame): The time-series data for smoothing, detrending and binarization.
            colGroup (str): Object id column in x. Detrending and rescaling is performed on a per-object basis.
            colMeas (str): Measurement column in x on which detrending and rescaling is performed.
            colFrame (str): Frame column in Time-series data. Used for sorting.

        Returns:
            DataFrame: Dataframe containing binarized data, rescaled data and the original columns.
        """
        col_resc = f"{colMeas}.resc"
        col_bin = f"{colMeas}.bin"
        cols = [colGroup, colMeas]
        x.sort_values([colGroup, colFrame], inplace=True)
        data_np = x[cols].to_numpy()

        if self.biasMet == "none":
            rescaled_data = self._rescale_data(data_np, group_index=0, meas_index=1)
            detrended_data = self.detrend(rescaled_data, 0, 1)
            binarized_data = self._bin_data(detrended_data)
        else:
            detrended_data = self.detrend(data_np, group_index=0, meas_index=1)
            binarized_data = self._bin_data(detrended_data)

        x[col_resc] = detrended_data
        x[col_bin] = binarized_data
        return x


if __name__ == '__main__':
    df = pd.read_csv("/mnt/c/Users/benig/Downloads/objNuclei_1line_clean_tracks.csv")
    df["col_meas"] = df["objCytoRing_Intensity_MeanIntensity_imKTR"] / df["objNuclei_Intensity_MeanIntensity_imKTR"]
    ts = binData()
    ts.run(df, 'track_id_uni', 'col_meas', 'Image_Metadata_T')
