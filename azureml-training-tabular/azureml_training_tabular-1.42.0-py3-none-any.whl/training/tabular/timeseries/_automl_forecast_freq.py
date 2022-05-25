# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The AutoMLForecastFreq object to handle the freq and its string representation."""
from typing import Any, Optional, Union, cast

import json

import numpy as np
import pandas as pd

from pandas.tseries.frequencies import to_offset


class AutoMLForecastFreq(object):
    """The class holding date and string offset representation of frequency"""

    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.tseries.offsets.DateOffset.html
    DATE_KWDS = ['years', 'months', 'weeks', 'days', 'hours',
                 'minutes', 'seconds', 'microseconds', 'nanoseconds',
                 'year', 'month', 'day', 'weekday', 'hour', 'minute',
                 'second', 'microsecond', 'nanosecond']
    DATE_OFFSET_SIGNATURE = 'DateOffset_params'

    def __init__(self, freq: Optional[Union[str, pd.DateOffset]]
                 ) -> None:
        """
        Construct the new AutoMLForecastFreq object.

        The primary purpose of this class is to make transforms, accepting frequency as a parameter
        cloneable. To clone the transform we are taking freq parameter as a string and for the cloned transform
        scikit learn checks if cloned object's parameter freq, taken by get_params() is the same as the one used
        in the constructor.
        :param freq: The frequency to be returned.
        :return: The tuple with string and pd.DateOffset representation of frequency.
        """
        self._freq = None  # type: Optional[pd.DateOffset]
        self._freqstr = None  # type: Optional[str]
        if isinstance(freq, str):
            self._freq = AutoMLForecastFreq.str_to_freq(freq)
            if self._freq is None:
                self._freqstr = None
            else:
                self._freqstr = freq
        elif isinstance(freq, pd.DateOffset):
            self._freq = freq
            self._freqstr = AutoMLForecastFreq.freq_to_str(freq)

    @property
    def freq(self) -> Optional[pd.DateOffset]:
        """Return the pd.DateOffset representation of frequency."""
        return self._freq

    @property
    def freqstr(self) -> Optional[str]:
        """Return the string representation of a frequency."""
        return self._freqstr

    @staticmethod
    def freq_to_str(freq: pd.DateOffset) -> str:
        """
        The safe method to convert pd.DateOffset to string.

        **Note:** This method honor the special case if the date offset is defined as
        pd.DateOffset(days=5, months=1). This frequency can not be reversible converted to string:
        calling to_offset(pd.DareOffset(days=5, months=1).freqstr) will result in ValueError.
        :param freq: The frequency to be converted to string.
        :return: The string representation of a frequency.
        """
        # Check if freqstr can be serialized back.
        result_str = freq.freqstr
        try:
            to_offset(result_str)
            return cast(str, result_str)
        except BaseException:
            # We are working with pd.DateOffset, which is not serializable.
            pass

        # Handle the pd.DateOffset class
        # We convert freq.n to int to make sure, it is not np.int32, which is not
        # json serializable.
        params = {'n': int(freq.n), 'normalize': freq.normalize}
        for keyword in AutoMLForecastFreq.DATE_KWDS:
            if hasattr(freq, keyword):
                param = getattr(freq, keyword)
                if isinstance(param, np.number):
                    param = int(param)
                params[keyword] = param
        return json.dumps({AutoMLForecastFreq.DATE_OFFSET_SIGNATURE: params})

    @staticmethod
    def str_to_freq(freq_str: str) -> Optional[pd.DateOffset]:
        """
        Safely convert string to pd.DateOffset.

        This method can use the JSON to deserialize the pd.DateOffset to string.
        :param freq_str: The string representation of a frequency.
        :return: The date offset, corresponding to frequency or None.
        :raises: ConfigException if the string can not be parsed
        """
        try:
            # First we will try pandas mechanism.
            return to_offset(freq_str)
        except ValueError:
            # if pandas mechanism fail, we will check if string contains the DateOffset JSON.
            if freq_str.startswith('{"' + AutoMLForecastFreq.DATE_OFFSET_SIGNATURE):
                # Try to parse strings.
                try:
                    param_dict = json.loads(freq_str)[AutoMLForecastFreq.DATE_OFFSET_SIGNATURE]
                    return pd.DateOffset(**param_dict)
                except BaseException:
                    pass
        return None

    @staticmethod
    def _get_freqstr_safe(transform: Any) -> Optional[str]:
        """
        The method for backward compatibe way to get frequency.

        :param transform: The transform that may contain the frequency parameter. In our code
                          it may be _freq and freq.
        :return: The string, representing frequency.
        """
        freq_obj = None
        # First check for private attributes.
        for attr in ('_freq', '_ts_freq'):
            if hasattr(transform, attr):
                freq_obj = getattr(transform, attr)
                break
        if freq_obj is None and hasattr(transform, 'freq'):
            freq_obj = transform.freq
        if isinstance(freq_obj, AutoMLForecastFreq):
            return freq_obj.freqstr
        if isinstance(freq_obj, pd.DateOffset):
            return cast(str, freq_obj.freqstr)
        return None
