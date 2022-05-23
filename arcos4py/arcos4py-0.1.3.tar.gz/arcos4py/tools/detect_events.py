"""Module to track and detect collective events.

Example:
    >>> from arcos4py.tools import detectCollev
    >>> ts = detectCollev(data)
    >>> events_df = ts.run()
"""

from typing import Union

import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from sklearn.cluster import DBSCAN

from ._errors import columnError, epsError, minClSzError, noDataError, nPrevError


class detectCollev:
    """Identifies and tracks collective signalling events.

    Requires binarized measurement column.
    Makes use of the dbscan algorithm,
    applies this to every timeframe and subsequently connects
    collective events between frames located within eps distance of each other.

    Attributes:
        input_data (DataFrame): Input data to be processed. Must contain a binarized measurement column.
        eps (float): The maximum distance between two samples for one to be considered as in
            the neighbourhood of the other.
            This is not a maximum bound on the distances of points within a cluster.
            Value is also used to connect collective events across multiple frames.
        minClSz (int): Minimum size for a cluster to be identified as a collective event.
        nPrev (int): Number of previous frames the tracking
            algorithm looks back to connect collective events.
        posCols (list): List of position columns contained in the data.
            Must at least contain one
        frame_column (str): Indicating the frame column in input_data.
        id_column (str): Indicating the track id/id column in input_data.
        bin_meas_column (str): Indicating the bin_meas_column in input_data or None.
        clid_column (str): Indicating the column name containing the ids of collective events.
    """

    def __init__(
        self,
        input_data: pd.DataFrame,
        eps: float = 1,
        minClSz: int = 1,
        nPrev: int = 1,
        posCols: list = ["x"],
        frame_column: str = 'time',
        id_column: Union[str, None] = None,
        bin_meas_column: Union[str, None] = 'meas',
        clid_column: str = 'clTrackID',
    ) -> None:
        """Constructs class with input parameters.

        Arguments:
            input_data (DataFrame): Input data to be processed. Must contain a binarized measurement column.
            eps (float): The maximum distance between two samples for one to be considered as in
                the neighbourhood of the other.
                This is not a maximum bound on the distances of points within a cluster.
                Value is also used to connect collective events across multiple frames.
            minClSz (int): Minimum size for a cluster to be identified as a collective event.
            nPrev (int): Number of previous frames the tracking
                algorithm looks back to connect collective events.
            posCols (list): List of position columns contained in the data.
                Must at least contain one
            frame_column (str): Indicating the frame column in input_data.
            id_column (str | None): Indicating the track id/id column in input_data, optional.
            bin_meas_column (str): Indicating the bin_meas_column in input_data or None.
            clid_column (str): Indicating the column name containing the ids of collective events.
        """
        # assign some variables passed in as arguments to the object
        self.input_data = input_data
        self.eps = eps
        self.minClSz = minClSz
        self.nPrev = nPrev
        self.frame_column = frame_column
        self.id_column = id_column
        self.bin_meas_column = bin_meas_column
        self.clid_column = clid_column
        self.posCols = posCols
        self.columns_input = self.input_data.columns
        self.clidFrame = f'{clid_column}.frame'

        self.pos_cols_inputdata = [col for col in self.posCols if col in self.columns_input]

        # run input checks
        self._run_input_checks()

    def _check_input_data(self):
        """Checks if input contains data\
        raises error if not."""
        if self.input_data is None:
            raise noDataError("Input is None")
        elif self.input_data.empty:
            raise noDataError("Input is empty")

    def _check_pos_columns(self):
        """Checks if Input contains correct columns\
        raises Exception if not."""
        if not all(item in self.columns_input for item in self.posCols):
            raise columnError("Input data does not have the indicated position columns!")

    def _check_frame_column(self):
        if self.frame_column not in self.columns_input:
            raise columnError("Input data does not have the indicated frame column!")

    def _check_eps(self):
        """Checks if eps is greater than 0."""
        if self.eps <= 0:
            raise epsError("eps has to be greater than 0")

    def _check_minClSz(self):
        """Checks if minClSiz is greater than 0."""
        if self.minClSz <= 0:
            raise minClSzError("Parameter minClSiz has to be greater than 0!")

    def _check_nPrev(self):
        """Checks if nPrev is greater than 0."""
        if self.nPrev <= 0 and isinstance(self.nPrev, int):
            raise nPrevError("Parameter nPrev has to be an integer greater than 0 and an integer!")

    def _run_input_checks(self):
        """Run input checks."""
        self._check_input_data()
        self._check_pos_columns()
        self._check_eps()
        self._check_minClSz()
        self._check_nPrev()
        self._check_frame_column()

    def _select_necessary_columns(
        self, data: pd.DataFrame, frame_col: str, id_col: Union[str, None], pos_col: list, bin_col: Union[str, None]
    ) -> pd.DataFrame:
        """Select necessary input colums from input data into dataframe.

        Arguments:
            data (DataFrame): Containing necessary columns.
            frame_col (str): Frame column in data.
            id_col (str): Id column in data.
            pos_col (list): string representation of position columns in data.
            bin_col (str): Name of binary column.

        Returns:
            DataFrame: Filtered columns necessary for calculation.
        """
        columns = [frame_col, id_col, bin_col]
        columns = [col for col in columns if col]
        columns.extend(pos_col)
        neccessary_data = data[columns].copy(deep=True)
        return neccessary_data

    def _filter_active(self, data: pd.DataFrame, bin_meas_col: Union[str, None]) -> pd.DataFrame:
        """Selects rows with binary value of greater than 0.

        Arguments:
            data (DataFrame): Dataframe containing necessary columns.
            bin_meas_col (str|None): Either name of the binary column or None if no such column exists.

        Returns:
            DataFrame: Filtered pandas DataFrame.
        """
        if bin_meas_col is not None:
            data = data[data[bin_meas_col] > 0]
        return data

    def _dbscan(self, x: np.ndarray) -> list:
        """Dbscan method to run and merge the cluster id labels to the original dataframe.

        Arguments:
            x (np.ndarray): With unique frame and position columns.
            collid_col (str): Column to be created containing cluster-id labels.

        Returns:
            list[np.ndarray]: list with added collective id column detected by DBSCAN.
        """
        db_array = DBSCAN(eps=self.eps, min_samples=self.minClSz, algorithm="kd_tree").fit(x[:, 1:])
        cluster_labels = db_array.labels_
        cluster_list = [id + 1 if id > -1 else np.nan for id in cluster_labels]
        return cluster_list

    def _run_dbscan(self, data: pd.DataFrame, frame: str, clid_frame: str, id_column: Union[str, None]) -> pd.DataFrame:
        """Apply dbscan method to every group i.e. frame.

        Arguments:
            data (DataFrame): Must contain position columns and frame columns.
            frame (str): Name of frame column in data.
            clid_frame (str): column to be created containing the output cluster ids from dbscan.
            id_column (str | None): track_id column

        Returns:
            DataFrame: Dataframe with added collective id column detected by DBSCAN for every frame.
        """
        if self.id_column:
            data = data.sort_values([frame, id_column]).reset_index(drop=True)
        else:
            data = data.sort_values([frame]).reset_index(drop=True)
        subset = [frame] + self.pos_cols_inputdata
        data_np = data[subset].to_numpy(dtype=np.float64)
        grouped_array = np.split(data_np, np.unique(data_np[:, 0], axis=0, return_index=True)[1][1:])
        # map dbscan to grouped_array
        out = [self._dbscan(i) for i in grouped_array]
        out_list = [item for sublist in out for item in sublist]
        data[clid_frame] = out_list
        data = data.dropna()
        return data

    def _make_db_id_unique(self, db_data: pd.DataFrame, frame: str, clid_frame, clid) -> pd.DataFrame:
        """Make db_scan cluster id labels unique by adding the\
        cummulative sum of previous group to next group.

        Arguments:
            db_data (DataFrame): Returned by _run_dbscan function with non-unique cluster ids.
            frame (str): Frame column.
            clid_frame (str): Column name of cluster-id per frame.
            clid (str): Column name of unique cluster ids to be returned.

        Returns:
            DataFrame: Dataframe with unique collective events.
        """
        db_data_np = db_data[[frame, clid_frame]].to_numpy()
        grouped_array = np.split(db_data_np[:, 1], np.unique(db_data_np[:, 0], axis=0, return_index=True)[1][1:])
        max_array = [0] + [np.max(i) for i in grouped_array if i.size != 0]
        out = [np.add(value, np.cumsum(max_array)[i]) for i, value in enumerate(grouped_array)]
        db_gp = np.concatenate(out)
        db_data[clid] = db_gp.astype(np.int64)
        return db_data

    def _nearest_neighbour(
        self,
        data_a: np.ndarray,
        data_b: np.ndarray,
        nbr_nearest_neighbours: int = 1,
    ):
        """Calculates nearest neighbour in from data_a\
        to data_b nearest_neighbours in data_b.

        Arguments:
            data_a (DataFrame): containing position values.
            data_b (DataFrame): containing position values.
            nbr_nearest_neighbours (int): of the number of nearest neighbours to be calculated.

        Returns:
            tuple(np.ndarray, np.ndarray): Returns tuple of 2 arrays containing nearest neighbour indices and distances.
        """
        kdB = KDTree(data=data_a)
        nearest_neighbours = kdB.query(data_b, k=nbr_nearest_neighbours)
        return nearest_neighbours

    def _link_clusters_between_frames(self, data: pd.DataFrame, frame: str, colid: str) -> pd.DataFrame:
        """Tracks clusters detected with DBSCAN along a frame axis,\
        returns tracked collective events as a pandas dataframe.

        Arguments:
            data (DataFrame): Output from dbscan.
            frame (str): Frame column.
            colid (str): Colid column.

        Returns:
            DataFrame: Pandas dataframe with tracked collective ids.
        """
        essential_cols = [frame, colid] + self.posCols
        data_essential = data[essential_cols]
        data_np = data_essential.to_numpy()
        data_np_frame = data_np[:, 0]

        # loop over all frames to link detected clusters iteratively
        for t in np.unique(data_np_frame, return_index=False)[1:]:
            prev_frame = data_np[(data_np_frame >= (t - self.nPrev)) & (data_np_frame < t)]
            current_frame = data_np[data_np_frame == t]
            # only continue if objects were detected in previous frame
            if prev_frame.size:
                colid_current = current_frame[:, 1]
                # loop over unique cluster in frame
                for cluster in np.unique(colid_current, return_index=False):
                    pos_current = current_frame[:, 2:][colid_current == cluster]
                    pos_previous = prev_frame[:, 2:]
                    # calculate nearest neighbour between previoius and current frame
                    nn_dist, nn_indices = self._nearest_neighbour(pos_previous, pos_current)
                    prev_cluster_nbr_all = prev_frame[nn_indices, 1]
                    prev_cluster_nbr_eps = prev_cluster_nbr_all[(nn_dist <= self.eps)]
                    # only continue if neighbours
                    # were detected within eps distance
                    if prev_cluster_nbr_eps.size:
                        prev_clusternbr_eps_unique = np.unique(prev_cluster_nbr_eps, return_index=False)
                        if prev_clusternbr_eps_unique.size > 0:
                            # propagate cluster id from previous frame
                            data_np[((data_np_frame == t) & (data_np[:, 1] == cluster)), 1] = prev_cluster_nbr_all

        np_out = data_np[:, 1]
        sorter = np_out.argsort()[::1]
        grouped_array = np.split(np_out[sorter], np.unique(np_out[sorter], axis=0, return_index=True)[1][1:])
        np_grouped_consecutive = (np.repeat(i + 1, value.size) for i, value in enumerate(grouped_array))
        out_array = np.array([item for sublist in np_grouped_consecutive for item in sublist])
        data[colid] = out_array[sorter.argsort()].astype('int64')
        return data

    def _get_export_columns(self):
        """Get columns that will contained in the pandas dataframe returned by the run method."""
        self.pos_cols_inputdata = [col for col in self.posCols if col in self.columns_input]
        if self.id_column:
            columns = [self.frame_column, self.id_column]
        else:
            columns = [self.frame_column]
        columns.extend(self.pos_cols_inputdata)
        columns.append(self.clid_column)
        return columns

    def run(self) -> pd.DataFrame:
        """Method to execute the different steps necessary for tracking.

        1. Selects columns.
        2. filters data on binary column > 1.
        3. Applies dbscan algorithm to every frame.
        4. Makes cluster ids unique across frames.
        5. Tracks collective events i.e. links cluster ids across frames.
        6. Creates final DataFrame.

        Returns (Dataframe):
            Dataframe with tracked collective events is returned.
        """
        filtered_cols = self._select_necessary_columns(
            self.input_data,
            self.frame_column,
            self.id_column,
            self.pos_cols_inputdata,
            self.bin_meas_column,
        )
        active_data = self._filter_active(filtered_cols, self.bin_meas_column)
        db_data = self._run_dbscan(
            data=active_data,
            frame=self.frame_column,
            clid_frame=self.clidFrame,
            id_column=self.id_column,
        )
        db_data = self._make_db_id_unique(
            db_data,
            frame=self.frame_column,
            clid_frame=self.clidFrame,
            clid=self.clid_column,
        )
        tracked_events = self._link_clusters_between_frames(db_data, self.frame_column, self.clid_column)
        return_columns = self._get_export_columns()
        tracked_events = tracked_events[return_columns]
        if self.clid_column in self.input_data.columns:
            df_to_merge = self.input_data.drop(columns=[self.clid_column])
        else:
            df_to_merge = self.input_data
        tracked_events = tracked_events.merge(df_to_merge, how="left")
        tracked_events = tracked_events
        return tracked_events
