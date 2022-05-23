from typing import List

from ..util import tsv_to_df
from .base import SummaryStatistics


class CellCountSumstatFun(SummaryStatistics):
    """
    Count the number of different cell types based on a field of interest.
    """

    def __init__(
        self,
        field_of_interest: str,
        cell_types_list: List,
        time_step: int = None,
        time_symbol: str = 't',
        name: str = "CellCount",
    ):
        """
        Parameters
        ----------
        field_of_interest: str
            The field of interest that we want to count its different cell
            types.
        cell_types_list: list
            A list of different type of cell that we want to count.
            E.g. [1, 2, 3].
        time_step: int (optional)
            The time step between time points. If not specified,
            the time step of the Morpheus file will be used.
        time_symbol: str (default=t)
            The time symbol, as specified in the morpheus model.
        """
        super().__init__(name)
        self.field_of_interest = field_of_interest
        self.cell_types_list = cell_types_list
        self.time_step = time_step
        self.time_symbol = time_symbol

    def __call__(self, loc: str):
        """
        Parameters
        ----------
        loc: str
            location of the simulation output.
        Returns
        -------
        A dictionary with the time points as keys, and for each as entry
        a pandas.DataFrame containing two columns: cell types and numbers of
        cells that have that type.
        """
        df = tsv_to_df(loc, "logger.csv")
        return count_cell_types(
            df,
            self.field_of_interest,
            self.cell_types_list,
            self.time_step,
            self.time_symbol,
        )


def count_cell_types(
    logger_df,
    field_of_interest,
    cell_types_list,
    time_step=None,
    time_symbol='t',
):
    """
    Count the number of different cell types based on a field of interest.
    """
    # set the time step value
    if not time_step:
        time_steps = logger_df[time_symbol].unique()
        time_step = time_steps[1] - time_steps[0]
    # define an empty dictionary for different time steps
    sumstat_dict = []
    # loop through the different time steps
    for _ in range(len(cell_types_list)):
        sumstat_dict.append([])
    for j in range(
        logger_df[time_symbol].unique().tolist()[0],
        logger_df[time_symbol].unique().tolist()[-1] + 1,
        time_step,
    ):
        # takes the next time step
        filtered_data = logger_df[logger_df[time_symbol] == j]
        # time_series_counter = []
        # iterate through all different cell types

        for i, cell_type in enumerate(cell_types_list):
            # count the number of cells with a specific cell type
            sumstat_dict[i].append(
                filtered_data.groupby(field_of_interest)
                .size()
                .get(cell_type, 0)
            )
        # dict_time_series[j] = pd.DataFrame(
        #     {'cell_type': cell_types_list,
        #      'n_cells': time_series_counter}).set_index('cell_type')
    return {"cell_type": sumstat_dict}


def classify_based_on_value(
    logger_df,
    field_of_interest,
    value_of_interest,
    time_step=None,
    time_symbol='t',
):
    """
    Classify the data of a field of interest based on a value of interest.

    Parameters
    ----------
    logger_df: pd.DataFrame
        The logger file in pandas dataframe format.
    field_of_interest: str
        The field of interest that we want to count its different cell types.
    value_of_interest: int
        the value of interest of which the classification will be based on.
    time_step: int (optional)
        The time step between time points. If not specified,
        the time step of the Morpheus file will be used.
    time_symbol: str (default=t)
        The time symbol, as specified in the morpheus model.
    Returns
    -------
    dict_time_series: dict
        A dictionary with cell type as a key, and the occurrences of
        the cell types as a value for different time intervals.
    """
    # set the time step value
    if not time_step:
        time_steps = logger_df[time_symbol].unique()
        time_step = time_steps[1] - time_steps[0]
    # get the length of the time step
    if field_of_interest not in logger_df:
        error_message = "Column name does not exist!"
        return error_message
    df_size = len(logger_df[time_symbol].unique().tolist())
    # define an empty dictionary for different time steps
    dict_time_series = {}
    series_obj = 0

    # loop through the different time steps
    for j in range(
        logger_df[time_symbol].unique().tolist()[0],
        df_size * time_step,
        time_step,
    ):
        # take the next time step
        filtered_data = logger_df[logger_df[time_symbol] == j]
        # print the RNA concentration
        for _ in range(2):
            series_obj = filtered_data.apply(
                lambda x: True
                if x[field_of_interest] >= value_of_interest
                else False,
                axis=1,
            )

            # count number of True in series
            num_of_rows = len(series_obj[series_obj is True].index)
        dict_time_series[j] = [len(series_obj) - num_of_rows, num_of_rows]
    return dict_time_series
