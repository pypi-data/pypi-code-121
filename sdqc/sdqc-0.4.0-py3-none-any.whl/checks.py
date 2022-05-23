"""
SDQC checks file
"""
import numpy as np


def missing_values(data, **kwargs):
    """
    Checks for missing values on the data.

    Parameters
    ----------
    data: ndarray
        The data to check.

    Returns
    -------
    pass, outs: bool, list
        pass is True if no missing values have been found and False if
        missing values have been found. outs is a list with the number
        of missing values and the total number of values.

    """
    n_nan = int(np.sum(np.isnan(data)))
    n_values = int(np.prod(data.shape))

    if n_nan == 0:
        return True, [0, n_values]

    return False, [n_nan, n_values]


def missing_values_data(data, series, completeness, **kwargs):
    """
    Checks for missing values on the data giving the series.

    Parameters
    ----------
    data: ndarray
        The data to check.
    series: ndarray (1D)
        The series to check.
    completeness: str (optional)
        If completeness is 'any' (default) the check will not pass
        if there is any missing value for a given series value (column).
        If completeness is 'all' the check will not pass if all the data
        values are missing for a given series value .
        It only has effects when data is a matrix (2 or more dimensions).

    Returns
    -------
    pass, outs: bool, list
        pass is True if no missing values have been found and False if
        missing values have been found. outs is a list with a first list
        of the number of missing values and the total number of values
        checked, and a second list with the series values for which the
        missing values where found. Note that the number of missing
        values and the total values depens on the completeness.

    """
    data_nan = np.isnan(data)
    n_nan = int(np.sum(data_nan))
    n_values = int(np.prod(data_nan.shape))

    if len(data.shape) >= 2:
        if completeness == 'all':
            data_nan = np.all(data_nan, axis=tuple(range(1, data_nan.ndim)))
            n_nan = int(np.sum(data_nan))
            n_values = int(np.prod(data_nan.shape))
        elif completeness == 'any':
            data_nan = np.any(data_nan, axis=tuple(range(1, data_nan.ndim)))
        else:
            raise ValueError("Invalid value for completeness argument.")

    if not any(data_nan):
        return True, [[0, n_values], []]

    missing = list(series[data_nan])
    return False, [[n_nan, n_values], missing]


def series_monotony(series, **kwargs):
    """
    Checks if series is monotonous.

    Parameters
    ----------
    series: ndarray (1D)
        The series to check.

    Returns
    -------
    pass, outs: bool, list
        pass is True if series is monotonous and False if not.
        outs is a list with the series range (minimum and maximum).

    """
    if all(np.diff(series) < 0) or all(np.diff(series) > 0):
        return True, [series[0], series[-1]]

    return False, [np.min(series), np.max(series)]


def series_range(series, srange, **kwargs):
    """
    Checks if series range is inside a given range.

    Parameters
    ----------
    series: ndarray (1D)
        The series to check.

    srange: list (len 2)
        The minimum and maximum value of the series.

    Returns
    -------
    pass, outs: bool, list
        pass is True if series is monotonous and False if not.
        outs is a list with the series range (minimum and maximum)
        and a list with the give srange.

    """
    smin, smax = np.min(series), np.max(series)
    if smin < srange[0] or smax > srange[1]:
        return False, [[smin, smax], srange]

    return True, [[smin, smax], srange]


def series_increment_type(series, type, **kwargs):
    """
    Checks if series increments following the trend specified by the type
    argument.

    Parameters
    ----------
    series: ndarray (1D)
        The series to check.

    type: str
        The series distribution ('linear')

    Returns
    -------
    pass, outs: bool, list
        pass is True if series is monotonous and False if not.
        outs is a list with the series step or the full series.

    """
    # TODO include more distributions ('exponential', 'logarithmic'...)
    if type == 'linear':
        ds = np.diff(series)
        if np.all(ds == ds[0]):
            # return True with the step
            return True, [ds[0]]
    else:
        raise ValueError(
            f"The argument {type} is not supported by series_increment_type.")

    return False, list(series)


def outlier_values(data, method, **kwargs):
    """
    Checks if there are possible outliers in the data using a
    multiple of the standard deviation.

    Parameters
    ----------
    data: ndarray
        The data to check.

    method: str
         The method to be used. Can be 'std' for standard deviation method
         or 'iqr' for interquartile range method.

    **kwargs: see below

    Keyword Args
    ------------
    nstd: float
        For 'std' method, the number of standard deviations
        to define outliers.

    niqr: float
        For 'iqr' method, the number of interquartile ranges
        to define outliers.

    Returns
    -------
    pass, outs: bool, list
        pass is True if the data does not have outliers and False if it does.
        outs is a list with the number of possible outliers and
        the total number of values.
    """
    # number of values in the ndarray
    n_values = data.size

    if method == 'std':
        # standard deviation method
        nstd = kwargs.get('nstd', 2)
        mean = np.nanmean(data)
        std = np.nanstd(data)
        # mark outlier values as True
        mask = np.logical_or(data < mean - nstd*std,
                             data > mean + nstd*std)

    elif method == 'iqr':
        # interquartile range method
        niqr = kwargs.get('niqr', 1.5)
        q_low, q_up = np.percentile(data, 25), np.percentile(data, 75)
        iqr = q_up - q_low
        # mark outlier values as True
        mask = np.logical_or(data < q_low - niqr*iqr,
                             data > q_up + niqr*iqr)

    else:
        raise ValueError(
            f"The method {method} is not supported by outlier_values."
        )

    # no outliers found
    if not np.any(mask):
        return True, [[], n_values]

    coords = kwargs.get('coords', [])
    final_coords = kwargs.get('final_coords', {})

    # get indexes of outlier values. This returns as many arrays as there are
    # dimensions in the ndarray. Each array contains the indexes of the outlier
    # in that dimension.
    outlier_indexes = np.where(mask)

    # If the data has dimensions the outlier_indexes is a list of as many
    # arrays as there are dimensions in the ndarray. Here we make lists with
    # the indexes of the outlier values in each dimension.
    if len(data.shape) > 1:
        outlier_indexes = [list(idxs) for idxs in zip(*outlier_indexes)]

    outliers = []
    if len(coords) > 1:  # data loaded from multiple files/tabs/cellrange names

        # here we classify outlier values in separate lists, corresponding to
        # the file/tab/cellrange name from which the values were loaded

        # join all unique coordinates of all dimensions from the different
        # files/tabs/cellrange names into a single list
        grouped_coords = [set().union(*element.values()) for element in coords]

        # put the coordinates of each dimension of the final_coords in a
        # separate list
        grouped_final_coords = list(final_coords.values())

        # number of values in the ndarray obtained from dimensions.
        # when we compare this with the number of values in the data, we will
        # and they don't match, we will know the data has a time dimenision.
        n_values_from_coords = 1
        for x in grouped_final_coords:
            n_values_from_coords *= len(x)

        for el in grouped_coords:
            sublist = []
            for idx in outlier_indexes:  # idx should be smthng like [4, 2, 1]

                # removing the time dimension, if it exists
                idx_ = idx[1:] if n_values != n_values_from_coords else idx

                # get the names of the coordinates corresponding to the
                # indexes of the identified outliers
                coord_names = []
                for i in range(len(idx_)):
                    coord_names.append(grouped_final_coords[i][idx_[i]])

                # if those coordinate names are all in the coords of the
                # specific file/tab/cellrange name we are iterating over (el),
                # it means that the outlier is in that file/tab/cellrange,
                # so we add it to a separate list for that particular
                # file/tab/cellrange name.
                if all(map(lambda x: x in el, coord_names)):
                    sublist.append(data[tuple(idx)].item())

            outliers.append(sublist)

    else:
        # data loaded from a single file/tab/cellrange name,
        # hence we put all outliers in a single list
        if len(data.shape) > 1:  # has dimensions
            outliers = [data[tuple(idx)].item() for idx in outlier_indexes]
        else:  # without dimensions
            outliers = [data[idx].item() for idx in outlier_indexes[0]]

    return False, [outliers, n_values]
