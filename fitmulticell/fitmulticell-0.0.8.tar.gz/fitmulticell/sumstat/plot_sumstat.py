import matplotlib.pyplot as plt
import numpy as np


def plot_different_cell_type(
    dict_time_series,
    cell_types_list,
    time_step=1,
    figure_title='',
    cell_types_names=None,
):
    """
    plot 1d chart of the count of cell types at different time points

    Parameters
    ----------
    dict_time_series: dict
        a dictionary that contains number of occurrence for each cell type
        throughout different time points
    cell_types_list: list
        a list of different type of cell that we want to count. E.g. [1, 2, 3].
    time_step: int (default=1)
        the time step between time points
    figure_title: str, optional (default=None)
        the title for the plotted figure
    cell_types_names: list, optional (default is cell_types_list)
        the name of different cell type. If not specified, the names will be
        taken from the cell_types_list

    Returns
    -------
    ax: matplotlib axis
        axis of the plot
    """
    if not dict_time_series and not isinstance(dict_time_series, dict):
        print("the provided dictionary is not in the required format")
        return -1
    if not isinstance(cell_types_list, list):
        print("the provided cell types list is not in the required format")
        return -1
    if not isinstance(time_step, int):
        print("the time step should be in int")
        return -1
    if cell_types_names is None:
        cell_types_names = cell_types_list

    _, ax = plt.subplots()
    # get all time points
    time_interval = list(dict_time_series.keys())
    y_list = []
    # create empty neasted lists for each cell type
    for _ in range(len(cell_types_list)):
        y_list.append([])
    # iterate through the different time interval and save the cells data in
    # the neasted lists
    for _key, data_dataframe in dict_time_series.items():
        for i in range(len(cell_types_list)):
            y_list[i].append(data_dataframe.iloc[i]['n_cells'])
    # plot the change of cell types throughout different time points
    ax.set_ylabel('Number of cells')
    ax.set_xlabel('Time (h)')
    ax.set_title(figure_title)
    for i in range(len(cell_types_list)):
        ax.plot(time_interval, y_list[i])
        # set up time points
    ax.set_xticks(np.arange(time_interval[0], time_interval[-1], time_step))
    ax.legend(cell_types_names)
    return ax


def plot_cluster_size_time_point(dict_time_series, figure_title=''):
    """
    plot a bar chart of the size of clusters at single time point

    Parameters
    ----------
    dict_time_series: dict
        a dictionary that contains number of occurrence for each cell type
        throughout different time points
    figure_title: str, optional (default=None)
        the title for the plotted figure

    Returns
    -------
    ax: matplotlib axis
        axis of the plot
    """
    if not dict_time_series and not isinstance(dict_time_series, dict):
        print("the provided dictionary is not in the required format")
        return -1
    _, ax = plt.subplots()
    # get all time points
    y_list = []
    # create empty neasted lists for each cell type
    keys_list = []
    # iterate through clusters in the dict_time_series
    for key, data_dict in dict_time_series.items():
        y_list.append(len(data_dict))
        keys_list.append(key)
    ax.bar(keys_list, y_list)
    # set up the label of x and y axis
    ax.set_ylabel('Size of cluster')
    ax.set_xlabel('Cluster index number')
    # set the title of the bar chart
    ax.set_title(figure_title)
    keys_list = list(map(str, keys_list))
    ax.set_xticks(keys_list)
    return ax


def plot_cluster_count_all_time_point(
    dict_time_series, time_step=1, figure_title=''
):
    """
    plot a bar chart of the counts of clusters at multiple time points

    Parameters
    ----------
    dict_time_series: dict
        a dictionary that contains number of occurrence for each cell type
        throughout different time points
    time_step: int (default=1)
        the time step between time points
    figure_title: str, optional (default=None)
        the title for the plotted figure

    Returns
    -------
    ax: matplotlib axis
        axis of the plot
    """
    if not dict_time_series and not isinstance(dict_time_series, dict):
        print("the provided dictionary is not in the required format")
        return -1
    _, ax = plt.subplots()
    # get the cluster counts
    y_list = list(dict_time_series.values())
    # get different time points
    keys_list = list(dict_time_series.keys())
    ax.bar(keys_list, y_list)
    # set up the label of x and y axis
    ax.set_ylabel('Number of clusters')
    ax.set_xlabel('time (h)')
    # set the title of the bar chart
    ax.set_title(figure_title)
    ax.set_xticks(np.arange(keys_list[0], keys_list[-1], time_step))
    return ax


def plot_cluster_size_all_time_point(
    dict_time_series, time_step=1, figure_title=''
):
    """
    plot a bar chart of the size of clusters at multiple time points

    Parameters
    ----------
    dict_time_series: dict
        a dictionary that contains number of occurrence for cluster index
        throughout different time points
    time_step: int (default=1)
        the time step between time points
    figure_title: str, optional (default=None)
        the title for the plotted figure

    Returns
    -------
    ax: matplotlib axis
        axis of the plot
    """
    if not dict_time_series and not isinstance(dict_time_series, dict):
        print("the provided dictionary is not in the required format")
        return -1
    _, ax = plt.subplots()
    # get the cluster counts
    y_list = list(dict_time_series.values())
    # get different time points
    keys_list = list(dict_time_series.keys())
    keys_list_str = [str(x) for x in keys_list]
    ax.bar(keys_list_str, y_list)
    # set up the label of x and y axis
    ax.set_ylabel('Number of clusters')
    ax.set_xlabel('Cluster index')
    # set the title of the bar chart
    ax.set_title(figure_title)
    ax.set_xticks(keys_list_str)
    return ax


def plot_active_cell_all_time_point(
    dict_time_series, time_step=1, figure_title=''
):
    """
    plot a bar chart of the number of active infected cell at multiple time
    points

    Parameters
    ----------
    dict_time_series: dict
        a dictionary that contains the total number of active infected cells at
        different time points
    time_step: int (default=1)
        the time step between time points
    figure_title: str, optional (default=None)
        the title for the plotted figure

    Returns
    -------
    ax: matplotlib axis
        axis of the plot
    """
    if not dict_time_series and not isinstance(dict_time_series, dict):
        print("the provided dictionary is not in the required format")
        return -1
    _, ax = plt.subplots()
    # get the cluster counts
    y_list = list(dict_time_series.values())
    # get different time points
    keys_list = list(dict_time_series.keys())
    ax.bar(keys_list, y_list)
    # set up the label of x and y axis
    ax.set_ylabel('Number of CC contributor cells')
    ax.set_xlabel('time (h)')
    # set the title of the bar chart
    ax.set_title(figure_title)
    ax.set_xticks(keys_list)

    return ax
