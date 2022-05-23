"""Module containing tools to calculate statistics of collective events.

Example:
    >>> from arcos4py.tools import calcCollevStats
    >>> test = calcCollevStats()
    >>> out = test.calculate(data = data,frame_column = "frame", collid_column = "collid")
"""

from typing import Union

import numpy as np
import pandas as pd


class calcCollevStats:
    """Class to calculate statistics of collective events."""

    def __init__(self) -> None:
        """Class to calculate statistics of collective events."""
        pass

    def _calculate_duration_size_group(self, data: np.ndarray) -> np.ndarray:
        """Calculates duration and size for the collective event in the dataframe.

        Arguments:
            data (np.ndarray): Containing a single collective event.

        Returns:
            np.ndarray: Array containing the collective event id, duration, tot_size, min_size,
                max_size, "nd_frame, first_frame_centroid and last_frame_centroid
                of the current collective event.
        """
        coll_dur = max(data[:, 0]) - min(data[:, 0]) + 1
        coll_total_size = np.unique(data[:, 1]).size
        (unique, counts) = np.unique(data[:, 0], return_counts=True)
        frequencies = np.asarray((unique, counts)).T
        coll_min_size = np.min(frequencies[:, 1])
        coll_max_size = np.max(frequencies[:, 1])
        coll_start_frame = np.min(data[:, 0])
        coll_end_frame = np.max(data[:, 0])
        if data.shape[1] > 3:
            coll_start_coord = np.mean(data[(data[:, 0] == coll_start_frame)][:, 3:], axis=0)
            coll_end_coord = np.mean(data[(data[:, 0] == coll_end_frame)][:, 3:], axis=0)
        else:
            coll_start_coord = np.nan
            coll_end_coord = np.nan
        d = np.array(
            [
                data[0, 2],
                coll_dur,
                coll_total_size,
                coll_min_size,
                coll_max_size,
                coll_start_frame,
                coll_end_frame,
                coll_start_coord,
                coll_end_coord,
            ],
            dtype=object,
        )
        return d

    def _get_collev_duration(
        self,
        data: pd.DataFrame,
        frame_column: str,
        collev_id: str,
        obj_id_column: str,
        posCol: Union[list, None],
    ) -> pd.DataFrame:
        """Applies self._calculate_duration_size_group() to every group\
        i.e. every collective event.

        Arguments:
            data (DataFrame): Containing unfiltered collective events.
            collev_id (str): Indicating the contained collective id column.
            frame_column (str): Indicating the contained frame column.
            obj_id_column (str): Indicating object id.
            posCol (list | None): Contains names of position columns. If None coordinates of
                start and end frame are not calcualted

        Returns:
            DataFrame: DataFrame containing "collid", "duration", "total_size",
                "min_size","max_size", "start_frame", "end_frame",
                "first_frame_centroid" and "last_frame_centroid"
                of all collective events.
        """
        cols = [
            collev_id,
            "duration",
            "total_size",
            "min_size",
            "max_size",
            "start_frame",
            "end_frame",
            "first_frame_centroid",
            "last_frame_centroid",
        ]
        subset = [frame_column, obj_id_column, collev_id]
        if posCol:
            subset.extend(posCol)
        # if object id cannot be converted to a float, generate unique labels with pd.factorize
        try:
            data_np = data[subset].to_numpy(dtype=np.float64)
        except ValueError:
            labels, levels = pd.factorize(data[obj_id_column])
            new_obj_id = f'{obj_id_column}_labels'
            data[new_obj_id] = labels
            subset[1] = new_obj_id
            data_np = data[subset].to_numpy(dtype=np.float64)

        data_np = data_np[~np.isnan(data_np).any(axis=1)]
        data_np_sorted = data_np[data_np[:, 2].argsort()]
        grouped_array = np.split(data_np_sorted, np.unique(data_np_sorted[:, 2], axis=0, return_index=True)[1][1:])
        # map to grouped_array
        out = map(self._calculate_duration_size_group, grouped_array)
        out_list = [i for i in out]
        df = pd.DataFrame(out_list, columns=cols)
        return df

    def calculate(
        self,
        data: pd.DataFrame,
        frame_column: str,
        collid_column: str,
        obj_id_column: str,
        posCol: Union[list, None] = None,
    ) -> pd.DataFrame:
        """Calculate statistics of collective events.

        Arguments:
            data (DataFrame): Containing collective events.
            frame_column (str): Indicating the frame column in data.
            collid_column (str): Indicating the collective event id column in data.
            obj_id_column (str): Indicating object id.
            posCol (list | None): Contains names of position columns. If None coordinates of
                start and end frame are not calcualted

        Returns:
            DataFrame: DataFrame containing "collid", "duration", "total_size",
                "min_size","max_size", "start_frame", "end_frame",
                "first_frame_centroid" and "last_frame_centroid"
                of all collective events.
        """
        if data.empty:
            return data
        colev_stats = self._get_collev_duration(data, frame_column, collid_column, obj_id_column, posCol)
        return colev_stats
