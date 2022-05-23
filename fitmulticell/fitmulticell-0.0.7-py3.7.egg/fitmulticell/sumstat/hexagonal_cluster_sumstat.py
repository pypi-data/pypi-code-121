import math
from typing import List

import numpy as np

from ..util import tsv_to_df
from .base import SummaryStatistics


class ClusterCountSumstatFun(SummaryStatistics):
    """
    Total number of clusters for all time points.
    """

    def __init__(
        self,
        field_of_interest: str,
        cluster_cell_type: List,
        time_step: int = None,
        time_interval: List = None,
        time_symbol: str = 't',
        name: str = "ClusterCount",
    ):
        """
        Parameters
        ----------
        field_of_interest: str
            The field of interest that contains the clusters data.
        cluster_cell_type: list
            List of cell type that are member of the cluster.
        time_step: int (optional)
            The time step between time points. If not specified,
            the time step of the Morpheus file will be used.
        time_interval: list [start_time_point, end_time_point] (optional)
            You can use the time_interval to define the starting and ending
            point that is in the range of the origianl time interval of the
            simulation.
            If not specified, the original time interval will be used.
        time_symbol: str (default=t)
            The time symbol, as specified in the morpheus model.
        """
        super().__init__(name)
        self.field_of_interest = field_of_interest
        self.cluster_cell_type = cluster_cell_type
        self.time_step = time_step
        self.time_interval = time_interval
        self.time_symbol = time_symbol

    def __call__(self, loc):
        """
        Parameters
        ----------
        loc: str
            The simulation folder.

        Returns
        -------
        cluster_count: int
            The total number of clusters for all time points.
        """
        df = tsv_to_df(loc, "logger.csv")
        return get_clusters_count(
            df,
            self.field_of_interest,
            self.cluster_cell_type,
            self.time_step,
            self.time_interval,
            self.time_symbol,
        )


def get_clusters_count(
    logger_df,
    field_of_interest,
    cluster_cell_type,
    time_step=None,
    time_interval=None,
    time_symbol='t',
):
    """
    Get the total number of clusters for all time points.
    """
    # check if time_step is specified, if not then calculate its value from
    # the distance between two time points from the morpheus logger file
    if not time_step:
        time_steps = logger_df[time_symbol].unique()
        time_step = time_steps[1] - time_steps[0]
    # starting and ending time point
    if time_interval is None:
        start = logger_df[time_symbol].unique().tolist()[0]
        end = logger_df[time_symbol].unique().tolist()[-1]
    else:
        start = time_interval[0]
        end = time_interval[1]

    cluster_per_time_point = {}
    # filter the data to only consider a specifice time point
    filtered_data = logger_df[logger_df[time_symbol] == start]
    number_of_cells = filtered_data.shape[0]
    # calculate the edge size of the hexagonal grid
    edge = math.ceil(math.sqrt((number_of_cells - 1) / 3))
    # iterate through all time points
    for j in range(start, end + 1, time_step):
        # filter the data to only consider a specific time point
        filtered_data = logger_df[logger_df[time_symbol] == j]
        # only consider the data on the field of interest
        morpheus_logger_list = filtered_data[field_of_interest].tolist()
        cluster_count = 0
        full_list_of_cluster = []
        # iterate through all cells in the specified time point
        for index in range(len(morpheus_logger_list)):
            # check if the cell belongs to the cluster and it is not already
            # considered
            if (morpheus_logger_list[index] in cluster_cell_type) and (
                index not in full_list_of_cluster
            ):
                index_list_of_cluster = []
                # find the neighbor cells list for a specific cell
                neighbor_cells_list = find_neighbor_list(index, edge)
                index_list_of_cluster.append(index)
                # check if the neighbor cells also belong to the same cluster
                index_list_of_cluster = check_for_connecting_cluster_loop(
                    cluster_cell_type,
                    edge,
                    neighbor_cells_list,
                    index_list_of_cluster,
                    morpheus_logger_list,
                )
                full_list_of_cluster = (
                    full_list_of_cluster + index_list_of_cluster
                )
                cluster_count = cluster_count + 1
            morpheus_logger_list_unique = sorted(set(morpheus_logger_list))
        if morpheus_logger_list_unique == sorted(cluster_cell_type):
            cluster_count = 1
        cluster_per_time_point[j] = cluster_count

    return {"cluster_count": list(cluster_per_time_point.values())}


def find_offset_list(edge: int) -> list:
    """
    Get the offset for all rows to be used to identify the neighbor cells.

    Parameters
    ----------
    edge: int
        The edge size of the hexagonal grid.

    Returns
    -------
    offset: list
        A list of offsets for the entire hexagonal grids.
    """
    k = 0
    counter_index = 0
    offset = []
    for i in range(0, edge * 2 - 2):
        if i < edge - 1:
            k = edge + i
            offset.append(k)
        else:
            offset.append(k - counter_index)
            counter_index = counter_index + 1
    return offset


def find_offset_int(edge: int, row: int) -> int:
    """
    Get the offset of the neighbor cells.

    Parameters
    ----------
    edge: int
        The edge size of the hexagonal grid.
    row: int
        The number of which we want to find its offset.

    Returns
    -------
    offset: int
        The offset of the specific row.
    """
    k = 0
    counter_index = 0
    offset = []
    for i in range(0, edge * 2 - 2):
        if i < edge - 1:
            k = edge + i
            offset.append(k)
        else:
            offset.append(k - counter_index)
            counter_index = counter_index + 1
    return offset[row]


def find_neighbor_list(cell_id, edge: int, nn=6):
    """
    Get the list of neighbor cells for a specific cell.

    Parameters
    ----------
    cell_id: int
        The ID of the cell that we want to find its neighbor.
    edge: int
        The edge size of the hexagonal grid.
    nn: int, optional (default=6)
        Number of neighbor cells. E.g. a hexagonal
        cell might have nn=6 because it has 6 neighbors.

    Returns
    -------
    list_of_neighbor: list
        List of neighbor cells.
    """
    # the current function works only when the number of neighbor cells is 5
    if nn != 6:
        return "Currently this function can only deal with neighbors = 6!"
    edge_cells_list = find_edge_cell(edge)
    # check if cell_id is out of the range of the hexagonal grid of the model
    if (
        cell_id < edge_cells_list[0][0]
        or cell_id > edge_cells_list[1][edge * 2 - 2]
    ):
        print("the cell_id is out of the range")
        return -1
    row = find_row_of_cell(cell_id, edge)
    offset = find_offset_list(edge)
    list_of_neighbor = []
    # deals with special scenarios, e.g., if cell is on the first row,
    # it will have only 4 neighbors
    # check if cell is in the last row of hexagon
    if row == edge * 2 - 2:
        list_of_neighbor.append(cell_id - offset[row - 1])
        list_of_neighbor.append(cell_id - offset[row - 1] - 1)
        if cell_id == edge_cells_list[1][edge * 2 - 2] - edge + 1:
            list_of_neighbor.append(cell_id + 1)
        elif cell_id == edge_cells_list[1][edge * 2 - 2]:
            list_of_neighbor.append(cell_id - 1)
        else:
            list_of_neighbor.append(cell_id + 1)
            list_of_neighbor.append(cell_id - 1)
    # check if cell is in the first row of hexagon
    elif row == edge_cells_list[0][0]:
        list_of_neighbor.append(cell_id + offset[row])
        list_of_neighbor.append(cell_id + offset[row] + 1)
        if cell_id == edge_cells_list[0][0]:
            list_of_neighbor.append(cell_id + 1)
        elif cell_id == edge - 1:
            list_of_neighbor.append(cell_id - 1)
        else:
            list_of_neighbor.append(cell_id + 1)
            list_of_neighbor.append(cell_id - 1)
    # check if cell not on the edge of hexagon
    elif cell_id not in edge_cells_list:
        list_of_neighbor.append(cell_id - 1)
        list_of_neighbor.append(cell_id + 1)
        list_of_neighbor.append(cell_id + offset[row])
        list_of_neighbor.append(cell_id + offset[row] + 1)
        list_of_neighbor.append(cell_id - offset[row - 1])
        list_of_neighbor.append(cell_id - offset[row - 1] - 1)

    # check if cell not on left edge of hexagon
    elif cell_id in edge_cells_list[0][:]:
        list_of_neighbor.append(cell_id + 1)
        list_of_neighbor.append(cell_id + offset[row] + 1)
        list_of_neighbor.append(cell_id - offset[row - 1])
        if edge < row + 1:
            list_of_neighbor.append(cell_id - offset[row - 1] - 1)
        if edge > row + 1:
            list_of_neighbor.append(cell_id + offset[row])
    # check if cell not on right edge of hexagon
    elif cell_id in edge_cells_list[1][:]:
        list_of_neighbor.append(cell_id - 1)
        list_of_neighbor.append(cell_id + offset[row])
        list_of_neighbor.append(cell_id - offset[row - 1] - 1)
        if edge < row + 1:
            list_of_neighbor.append(cell_id - offset[row - 1])
        if edge > row + 1:
            list_of_neighbor.append(cell_id + offset[row] + 1)
    return list_of_neighbor


def find_edge_cell(edge: int):
    """
    Get the list cells that are in the edge of the hexagonal grid.

    Parameters
    ----------
    edge: int
        The edge size of the hexagonal grid.

    Returns
    -------
    edge_cell_list: list
        List of edge cells.
    """
    edge_cell_list = np.zeros((2, edge * 2 - 1))
    k = edge
    temp = 0
    # iterate through all rows in the grid and locate edge cells for each row
    for i in range(0, edge * 2 - 1):
        if i == 0:
            edge_cell_list[0, i] = temp
        elif i < edge:
            temp = temp + k
            edge_cell_list[0, i] = temp
            k = k + 1
        else:
            temp = temp + k
            edge_cell_list[0, i] = temp
            k = k - 1
    k = edge + 1
    temp = edge - 1
    for i in range(0, edge * 2 - 1):
        if i == 0:
            edge_cell_list[1, i] = temp
        elif i < edge:
            temp = temp + k
            edge_cell_list[1, i] = temp
            k = k + 1
        elif i == edge:
            k = k - 2
            temp = temp + k
            edge_cell_list[1, i] = temp
        else:
            k = k - 1
            temp = temp + k
            edge_cell_list[1, i] = temp
    edge_cell_list = edge_cell_list.astype(int)
    return edge_cell_list


def check_neighbor_inactive_infected_cell(
    morpheus_neighbor_list, index, inactive_cell, cluster_cell_type
):
    """
    Check if the cell (index) is infected or not.

    Parameters
    ----------
    morpheus_neighbor_list: list
        The field of interest in the structure of list.
    index: int
        The cell id of the cell that will be checked.
    inactive_cell: list
        The list of the inactive infected cell.
    cluster_cell_type: list
        List of cell type that are member of the cluster.

    Returns
    -------
    inactive_cell: int
        The cumulative list of the inactive infected cells.
    """
    if len(morpheus_neighbor_list) > 0 and all(
        elem in cluster_cell_type for elem in morpheus_neighbor_list
    ):
        inactive_cell.append(index + 1)
    return inactive_cell


def find_row_of_cell(cell_id: int, edge: int):
    """
    Get the list of neighbor cells for a specific cell.

    Parameters
    ----------
    cell_id: int
        The ID of the cell whose row we want to find.
    edge: int
        The edge size of the hexagonal grid.

    Returns
    -------
    row_number: int
        the row number of the cell with (cell_id)
    """
    edge_cell_list = find_edge_cell(edge)
    row_number = 0
    for i in range(0, len(edge_cell_list[0])):
        if edge_cell_list[0][i] <= cell_id <= edge_cell_list[1][i]:
            row_number = i
            break
    return row_number


def check_for_connecting_cluster_loop(
    cluster_cell_type,
    edge,
    neighbor_cells_list,
    index_list_of_cluster,
    morpheus_logger_list,
) -> list:
    """
    Check whether the neighbor_cell_list ist member of cluster.

    Parameters
    ----------
    edge: int
        The edge size of the hexagonal grid.
    neighbor_cells_list: list
        A list for the neighbor cell.
    index_list_of_cluster: list
        The list of cluster member.
    morpheus_logger_list: pd.Series
        A pandas time series for the field of interest taken from the
        morpheus logger file.

    Returns
    -------
    index_list_of_cluster: list
        the list of cluster member
    """
    # iterate through all the cells in the neighbor_cells_list
    # check if they are connected to the cluster or not
    for neighbor_cell in neighbor_cells_list:
        # check if the cell has the same characteristics as the rest
        # of the cluster
        if morpheus_logger_list[neighbor_cell] in cluster_cell_type:
            if neighbor_cell not in index_list_of_cluster:
                index_list_of_cluster.append(neighbor_cell)
            new_neighbor_cells_list = find_neighbor_list(neighbor_cell, edge)
            # check if the cell is still not discovered as part of the
            # cluster in the current iteration
            for cell in new_neighbor_cells_list:
                if cell not in neighbor_cells_list:
                    neighbor_cells_list.append(cell)
    return index_list_of_cluster


class ClusterSizeSumstatFun(SummaryStatistics):
    """
    Total number of clusters and size of each cluster.
    """

    def __init__(
        self,
        field_of_interest: str,
        cluster_cell_type: List,
        time_point: int,
        time_symbol: str = 't',
        name: str = "ClusterSize",
    ):
        """
        Parameters
        ----------
        logger_df: pd.DataFrame
            The logger file in pandas dataframe format.
        field_of_interest: str
            The field of interest that contains the clusters data.
        cluster_cell_type: list
            A list of cell type that are member of the cluster.
        time_point: int
            The time point where we want count the number of clusters.
        time_symbol: str (default=t)
            The time symbol, as specified in the morpheus model.
        """
        super().__init__(name)
        self.field_of_interest = field_of_interest
        self.cluster_cell_type = cluster_cell_type
        self.time_point = time_point
        self.time_symbol = time_symbol

    def __call__(self, loc):
        """
        Returns
        -------
        cluster_count: dict
            A dictionary that contains the index and the member of each
            cluster.
        """
        df = tsv_to_df(loc, "logger.csv")
        return get_clusters_sizes_tp(
            df,
            self.field_of_interest,
            self.cluster_cell_type,
            self.time_point,
            self.time_symbol,
        )


def get_clusters_sizes_tp(
    logger_df,
    field_of_interest,
    cluster_cell_type,
    time_point,
    time_symbol='t',
):
    """
    Get the total number of clusters and the size of each cluster
    for a specific time point.
    """
    full_list_of_cluster = []
    dict_cluster_member = {}
    # filter the data to only consider a specific time point
    filtered_data = logger_df[logger_df[time_symbol] == time_point]
    number_of_cells = filtered_data.shape[0]
    # calculate the edge size of the hexagonal grid
    edge = math.ceil(math.sqrt((number_of_cells - 1) / 3))
    morpheus_logger_list = filtered_data[field_of_interest].tolist()
    # iterate through al cells in the specified time point
    for index in range(len(morpheus_logger_list)):
        # check if the cell belongs to the cluster and it is not already
        # considered
        if (morpheus_logger_list[index] in cluster_cell_type) and (
            index + 1 not in full_list_of_cluster
        ):
            index_list_of_cluster = []
            # find the neighbor cells list for a specific cell
            neighbor_cells_list = find_neighbor_list(index, edge)
            index_list_of_cluster.append(index)
            # check if the neighbor cells also belong to the same cluster
            index_list_of_cluster = check_for_connecting_cluster_loop(
                cluster_cell_type,
                edge,
                neighbor_cells_list,
                index_list_of_cluster,
                morpheus_logger_list,
            )
            index_list_of_cluster = [x + 1 for x in index_list_of_cluster]
            dict_cluster_member[index + 1] = len(index_list_of_cluster)
            full_list_of_cluster = full_list_of_cluster + index_list_of_cluster
    return dict_cluster_member


class CCNonContributorsTpSumstatFun(SummaryStatistics):
    """
    List of inactive cell in the grid at a specific time point.
    """

    def __init__(
        self,
        field_of_interest: str,
        cluster_cell_type: List,
        time_point: int,
        time_symbol: str = 't',
        name: str = "CCNonContributorsTp",
    ):
        """
        Parameters
        ----------
        logger_df: pd.DataFrame
            The logger file in pandas dataframe format.
        field_of_interest: str
            The field of interest that contains the clusters data
        cluster_cell_type: list
            A list of cell type that are member of the cluster
        time_point: int
            The time point where we want count the number of clusters
        time_symbol: str (default=t)
            The time symbol, as specified in the morpheus model
        """
        super().__init__(name)
        self.field_of_interest = field_of_interest
        self.cluster_cell_type = cluster_cell_type
        self.time_point = time_point
        self.time_symbol = time_symbol

    def __call__(self, loc):
        """
        Returns
        -------
        inactive_cell_list: list
            A list of all inactive infected cell, that means all cell that does
            not contribute to the cell-to-cell infection.
        """
        df = tsv_to_df(loc, "logger.csv")
        return get_cc_non_contributors_tp(
            df,
            self.field_of_interest,
            self.cluster_cell_type,
            self.time_point,
            self.time_symbol,
        )


def get_cc_non_contributors_tp(
    logger_df,
    field_of_interest,
    cluster_cell_type,
    time_point,
    time_symbol='t',
):
    """
    Get the list of inactive cell in the grid at a specific time point.
    """
    # filter the data to only consider a specific time point
    filtered_data = logger_df[logger_df[time_symbol] == time_point]
    number_of_cells = filtered_data.shape[0]
    # calculate the edge size of the hexagonal grid
    edge = math.ceil(math.sqrt((number_of_cells - 1) / 3))
    morpheus_logger_list = filtered_data[field_of_interest].tolist()
    inactive_cell_list = []
    full_list_of_cluster = []
    # iterate through all cells in the specified time point
    for index in range(len(morpheus_logger_list)):
        if (morpheus_logger_list[index] in cluster_cell_type) and (
            index + 1 not in full_list_of_cluster
        ):
            index_list_of_cluster = []
            neighbor_cells_list = find_neighbor_list(index, edge)
            morpheus_neighbor_list = []
            # iterate through all neighbor cells
            for i in neighbor_cells_list:
                morpheus_neighbor_list.append(morpheus_logger_list[i])
            index_list_of_cluster.append(index)
            # check if neighbor cells are CC active or not
            inactive_cell_list = check_neighbor_inactive_infected_cell(
                morpheus_neighbor_list,
                index,
                inactive_cell_list,
                cluster_cell_type,
            )
    return inactive_cell_list


class CCContributorsAllTpCountSumstatFun(SummaryStatistics):
    """
    Total number of active infected cells in the grid at a
    specific time point.
    """

    def __init__(
        self,
        field_of_interest: str,
        cluster_cell_type: List,
        time_step: int = None,
        time_interval: List = None,
        time_symbol: str = 't',
        name: str = "CCContributorsAllTpCount",
    ):
        """
        Parameters
        ----------
        logger_df: pd.DataFrame
            The logger file in pandas dataframe format.
        field_of_interest: str
            The field of interest that contains the clusters data.
        cluster_cell_type: list
            A list of cell type that are member of the cluster
        time_step: int (optional)
            The time step between time points. If not specified,
            the time step of the Morpheus file will be used.
        time_interval: list [start_time_point, end_time_point] (optional)
            You can use the time_interval to define the starting and ending
            point that is in the range of the original time interval of the
            simulation.
            If not specified, the original time interval will be used.
        time_symbol: str (default=t)
            The time symbol, as specified in the morpheus model.
        """
        super().__init__(name)
        self.field_of_interest = field_of_interest
        self.cluster_cell_type = cluster_cell_type
        self.time_step = time_step
        self.time_interval = time_interval
        self.time_symbol = time_symbol

    def __call__(self, loc):
        """
        Returns
        -------
        active_cell_count: int
            The total count of active infected cell, that means all cell that
            does not contribute to the cell-to-cell infection.
        """
        df = tsv_to_df(loc, "logger.csv")
        return get_count_cc_contributors_alltp(
            df,
            self.field_of_interest,
            self.cluster_cell_type,
            self.time_step,
            self.time_interval,
            self.time_symbol,
        )


def get_count_cc_contributors_alltp(
    logger_df,
    field_of_interest,
    cluster_cell_type,
    time_step=None,
    time_interval=None,
    time_symbol='t',
):
    """
    Get the total number of active infected cells in the grid at a
    specific time point
    """
    # check if time_step is specified, if not then calculate its value from the
    # distance between two time points from the morpheus logger file
    if time_step is None:
        time_steps = logger_df[time_symbol].unique()
        time_step = time_steps[1] - time_steps[0]
    inactive_cell_list = []
    # get the starting and ending time point
    if time_interval is None:
        start = logger_df[time_symbol].unique().tolist()[0]
        end = logger_df[time_symbol].unique().tolist()[-1]
    else:
        start = time_interval[0]
        end = time_interval[1]
    count_per_time_point = {}
    # filter the data to only consider the first time point
    filtered_data = logger_df[logger_df[time_symbol] == start]
    number_of_cells = filtered_data.shape[0]
    # calculate the edge size of the hexagonal grid
    edge = math.ceil(math.sqrt((number_of_cells - 1) / 3))
    # iterate through all cells in the specified time point
    for j in range(start, end + 1, time_step):
        filtered_data = logger_df[logger_df[time_symbol] == j]
        morpheus_logger_list = filtered_data[field_of_interest].tolist()
        full_list_of_cluster = []
        # iterate through all cells in the specified time point
        for index in range(len(morpheus_logger_list)):
            if (morpheus_logger_list[index] in cluster_cell_type) and (
                index + 1 not in full_list_of_cluster
            ):
                index_list_of_cluster = []
                # find the neighbor cells list for a specific cell
                neighbor_cells_list = find_neighbor_list(index, edge)
                morpheus_neighbor_list = []
                # iterate through all neighbor cells
                for i in neighbor_cells_list:
                    morpheus_neighbor_list.append(morpheus_logger_list[i])
                index_list_of_cluster.append(index)
                # check if neighbor cells are CC active or not
                inactive_cell_list = check_neighbor_inactive_infected_cell(
                    morpheus_neighbor_list,
                    index,
                    inactive_cell_list,
                    cluster_cell_type,
                )
                # find CC active cells
        active_cell_count = sum(
            i in cluster_cell_type for i in morpheus_logger_list
        ) - len(list(set(inactive_cell_list)))
        count_per_time_point[j] = active_cell_count
    return {"cc_contributors": list(count_per_time_point.values())}
