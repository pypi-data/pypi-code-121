# Copyright 2021 Cognite AS
import warnings

import numpy as np
import pandas as pd

from csaps import csaps
from kneed import KneeLocator
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from indsl.exceptions import UserValueError
from indsl.type_check import check_types
from indsl.validations import validate_series_is_not_empty


@check_types
def remove_outliers(
    data: pd.Series,
    reg_smooth: float = 0.9,
    min_samples: int = 4,
    eps: float = None,
    time_window: str = "60min",
    del_zero_val: bool = False,
) -> pd.Series:
    """Outlier removal

    Identifies outliers combining two methods, dbscan and csap.

    - **dbscan**: Density-based clustering algorithm used to identify clusters of varying shape and size within a data
      set. Does not require a pre-determined set number of clusters. Able to identify outliers as noise, instead of
      classifying them into a cluster. Flexible when it comes to the size and shape of clusters, which makes it more
      useful for noise, real life data.

    - **csaps regression**: Cubic smoothing spline algorithm. Residuals from the regression are computed. Data points with
      high residuals (3 Standard Deviations from the Mean) are considered as outliers.

    Args:
        data: Time series.
        reg_smooth: Smoothing factor.
            The smoothing parameter that determines the weighted sum of terms in the regression and it is limited by
            the range [0,1]. Defaults to 0.9. Ref: https://csaps.readthedocs.io/en/latest/formulation.html#definition
        min_samples: Minimum samples.
            Minimum number of data points required to form a distinct cluster. Defaults to 4.
            Defines the minimum number of data points required to form a distinct cluster. Rules of thumb for selecting
            the minimum samples value:

            * The larger the data set, the larger the value of MinPts should be.
            * If the data set is noisier, choose a larger value of MinPts Generally, MinPts should be greater than or
              equal to the dimensionality of the data set. For 2-dimensional data, use DBSCAN’s default value of 4
              (Ester et al., 1996).
            * If your data has more than 2 dimensions, choose MinPts = 2*dim, where dim= the dimensions of your data
              set (Sander et al., 1998).

        eps: Distance threshold.
            Defaults to None.  Defines the maximum distance between two samples for one to be considered as in the
            neighborhood of the other (i.e. belonging to the same cluster). The value of this parameter is automatically
            set after using a Nearest Neighbors algorithm to calculate the average distance between each point and its k
            nearest neighbors, where k = min_samples (minimum samples). In ascending order on a k-distance graph, the
            optimal value for the threshold is at the point of maximum curvature (i.e. after plotting the average
            k-distances in where the graph has the greatest slope). This is not a maximum bound on the distances of
            points within a cluster. This is the most important DBSCAN parameter to choose appropriately for your data
            set and distance function. If no value is given, it is set automatically using nearest neighbors algorithm.
            Defaults to None.
        time_window: Window.
            Length of the time period to compute the rolling mean. The rolling mean and the data point value are the two features considered when calculating the distance to the furthest neighbour.
            This distance allows us to find the right epsilon when training dbscan. Defaults to '60min'.
            Accepted string format: '3w', '10d', '5h', '30min', '10s'.
            If a number without unit (such as '60')is given, it will be considered as the number of minutes.
        del_zero_val: Remove zeros.
            Removes data points containing a value of 0. Defaults to False.

    Returns:
        pandas.Series: Time series without outliers.
    """

    df = data.to_frame()
    df = df.rename(columns={df.columns[0]: "val"})

    if str.isdigit(time_window):  # if user gives '60' it will be considered as '60min'
        warnings.warn(
            f"Missing time unit in argument 'time_window' in remove_outliers function, assuming {time_window}min.",
            UserWarning,
        )
        time_window = str(time_window) + "min"

    try:
        time_window = pd.Timedelta(time_window)
    except ValueError:
        raise UserValueError(
            f"Time window should be a string in weeks, days, hours or minutes format:'3w', '10d', '5h', '30min', '10s' not {time_window}."
        ) from None

    df["rolling_mean"] = df["val"].rolling(time_window, min_periods=1).mean()  # calculate features

    if del_zero_val:  # delete 0 values if user requests it
        df = df[df["val"] != 0.0]

    df_dbscan = df[["val"]].copy()

    validate_series_is_not_empty(df_dbscan)

    if eps is None:
        # calculate distance to the further neighbor in order to find best epsilon (radius) parameter for dbscan
        nbrs = NearestNeighbors(n_neighbors=2 * 3).fit(df)
        distances, indices = nbrs.kneighbors(df)
        df["knn_dist"] = distances[:, -1]

        dist = np.sort(distances[:, -1])
        i = np.arange(len(dist))
        knee = KneeLocator(i, dist, S=1, curve="convex", direction="increasing", interp_method="polynomial")
        eps = dist[knee.knee]

    # train dbscan
    dbscan_model = DBSCAN(eps=eps, min_samples=min_samples).fit(df_dbscan)
    labels = dbscan_model.labels_
    outlier_pos = np.where(labels == -1)[0]

    # y = df["val"].iloc[outlier_pos]
    # x = df.iloc[outlier_pos].index
    # dbscan_outliers_series = pd.Series(data = y, index= x) # todo return as output

    # delete outliers detected by dbscan
    no_outliers_df = df.drop(df.index[outlier_pos]).copy()

    # regression on the remainin datapoints
    df_reg = df.loc[no_outliers_df.index, :].copy()
    date_int = df_reg.index.to_series().apply(lambda x: x.value)
    date_int_stand = (date_int - date_int.mean()) / date_int.std()
    xs = np.linspace(date_int_stand.iloc[0], date_int_stand.iloc[-1], len(date_int_stand))
    csaps_data = csaps(date_int_stand, df_reg["val"], xs, smooth=reg_smooth)
    xs_destand = np.linspace(date_int.iloc[0], date_int.iloc[-1], len(date_int))
    xs_destand = pd.to_datetime(xs_destand)
    # reg_outliers_series = pd.Series(data = csaps_data, index= xs_destand) # todo return as output

    # delete points with high residuals
    res = pd.DataFrame(abs(df_reg["val"] - csaps_data))
    res["val_stand"] = (res["val"] - res["val"].mean()) / res["val"].std()
    # res_stand_outliers = res[res["val_stand"] >= 3]
    res_stand_no_outliers = res[res["val_stand"] < 3]
    # reg_outliers_series = pd.Series(data = res_stand_outliers.index, index= df.loc[res_stand_outliers.index,:]['val'].values) # todo return as output
    df_without_outliers = df.loc[res_stand_no_outliers.index, :]

    return df_without_outliers["val"]


OUTLIERS_REMOVE = remove_outliers
