import logging
from typing import Optional, Union

import pandas as pd


class DataFrame(pd.DataFrame):
    """A class allowing to manipulate a Sarus dataset as a Pandas DataFrame.

    By default, all operations are performed on the synthetic data represented
    as a pandas DataFrame.

    The `mean`, 'std' and `sum` methods have been overloaded to acccept an
    additional `target_epsilon` parameter. Setting `target_epsilon` to be
    greater than zero will execute remotely a private query on the protected
    dataset. Supported methods list will progressively be enriched.
    """

    def __init__(
        self,
        dataset,
        max_download_size: Optional[int] = None,
        original: bool = True,
    ) -> None:
        super().__init__(
            data=dataset._synthetic_as_pd_dataframe(
                rows_number=max_download_size,
                original=original,
            )
        )
        self.dataset = dataset

    def mean(
        self,
        axis: int = 0,
        skipna: bool = True,
        level: Optional[Union[int, str]] = None,
        numeric_only: Optional[bool] = None,
        target_epsilon: Optional[float] = None,
        verbose: bool = False,
        **kwargs,
    ) -> pd.Series:
        """Return the mean of the values over the requested axis.

        Execute the standard pandas method if `target_epsilon` is zero. If
        `target_epsilon` is greater than zero, it builds and sends a private
        query for execution on the Sarus server.

        Args:
            axis (int): Axis for the function to be applied on.
                Only axis=0 is supported when `target_epsilon` > 0 for DP
                reasons.
            skipna (bool): Exclude NA/null values when computing the result.
            level (int, level name):
                If the axis is a MultiIndex (hierarchical), count along a
                particular level, collapsing into a Series.
            numeric_only (bool):
                Include only float, int, boolean columns. If None, will attempt
                to use everything, then use only numeric data. Not implemented
                for Series.
            target_epsilon (Optional[float]):
                Maximum privacy budget (epsilon) to assign to the mean computation
                of all relevant columns.
                If 0, runs on the synthetic data.
                If >0, each column result is a combination of a query on the synthetic
                data and a Differentially-Private query on the real data.
                If None, a default target epsilon specific to the current user and access rule is used.
                Default target epsilon is 0 if the access is a Differentially-Private access with
                per-user or per-group limit; default value equals to per-query limit if the access is
                a Differentially-Private access with a per-query limit only. Meaning Sarus maximizes result
                accuracy in the given privacy constraints. See user documentation to know more.
        Returns:
            A pandas.Series.
        """
        if target_epsilon == 0.0:
            return super().mean(axis, skipna, level, numeric_only, **kwargs)
        else:
            # Check parameters
            if axis == 1:
                logging.warn(
                    "Cannot query `mean` on private dataset with "
                    "`axis`=1. Computing on synthetic data."
                )
                return super().mean(axis, skipna, level, numeric_only, **kwargs)

            if numeric_only is False:
                logging.warn(
                    "Cannot query `mean` of non numeric columns with `numeric_only`=False on private dataset. "
                    "Computing on synthetic data."
                )
                return super().mean(axis, skipna, level, numeric_only, **kwargs)

            # Select numeric columns only
            numeric_columns = [
                feature["name"]
                for feature in self.dataset.features
                if list(feature["type"].keys())[0] in ["integer", "real"]
            ]
            non_numeric_columns = [
                feature["name"]
                for feature in self.dataset.features
                if feature["name"] not in numeric_columns
            ]
            if verbose:
                logging.info(
                    "Dropping non numeric column:",
                    ", ".join(non_numeric_columns),
                )

            # Build query
            # Need to be careful with quotes ordering: put " " inside ' '
            values = [
                f'AVG("{column}") as "avg_{column.lower()}"'
                for column in numeric_columns
            ]
            query = f'SELECT {", ".join(values)} FROM {self.dataset.name}'
            if verbose:
                logging.info(query)
            response = self.dataset.client.query(
                query=query, target_epsilon=target_epsilon, verbose=True
            )

            # Return result as a pd.Series with original column names
            if response["status"] == "SUCCESS":
                result = response["result"][0]
                API_columns = response["columns"]
                name_mapping = {
                    f"avg_{column.lower()}": column
                    for column in numeric_columns
                }
                result = {
                    name_mapping[col]: result[idx]
                    for idx, col in enumerate(API_columns)
                }
                return pd.Series(result)
            else:
                raise Exception(f"The query {query} failed.")

    def std(
        self,
        axis: int = 0,
        skipna: bool = True,
        level: Optional[Union[int, str]] = None,
        ddof: int = 1,
        numeric_only: Optional[bool] = True,
        target_epsilon: Optional[float] = None,
        verbose: bool = False,
        **kwargs,
    ) -> pd.Series:
        """Return the mean of the values over the requested axis.

        Execute the standard pandas method if `target_epsilon` is zero. If
        `target_epsilon` is greater than zero, it builds and sends a private
        query for execution on the Sarus server.

        Args:
            axis (int): Axis for the function to be applied on.
                Only axis=0 is supported when `target_epsilon` > 0 for DP
                reasons.
            skipna (bool): Exclude NA/null values when computing the result.
            level (int, level name):
                If the axis is a MultiIndex (hierarchical), count along a
                particular level, collapsing into a Series.
            ddof (int, default 1):
                Delta Degrees of Freedom. The divisor used in calculations is
                N - ddof, where N represents the number of elements.
            numeric_only (bool):
                Include only float, int, boolean columns. If None, will attempt
                to use everything, then use only numeric data. Not implemented
                for Series.
            target_epsilon (Optional[float]):
                Maximum privacy budget (epsilon) to assign to the std computation
                of all relevant columns.
                If 0, runs on the synthetic data.
                If >0, each column result is a combination of a query on the
                synthetic data and a Differentially-Private query on the real data.
                If None, a default target epsilon specific to the current user and access rule is used.
                Default target epsilon is 0 if the access is a Differentially-Private access with
                per-user or per-group limit; default value equals to per-query limit if the access is
                a Differentially-Private access with a per-query limit only. Meaning Sarus maximizes result
                accuracy in the given privacy constraints. See user documentation to know more.

        Returns:
            A pandas.Series.
        """
        if target_epsilon == 0.0:
            return super().std(
                axis=axis,
                skipna=skipna,
                level=level,
                ddof=ddof,
                numeric_only=numeric_only,
                **kwargs,
            )
        else:
            # Check parameters
            if axis == 1:
                logging.warn(
                    "Cannot query `std` with `axis`=1 on private dataset. "
                    "Computing on synthetic data."
                )
                return super().std(
                    axis=axis,
                    skipna=skipna,
                    level=level,
                    ddof=ddof,
                    numeric_only=numeric_only,
                    **kwargs,
                )

            if numeric_only is False:
                logging.warn(
                    "Cannot query `std` of non numeric columns with "
                    "`numeric_only`=False on private dataset. "
                    "Computing on synthetic data.."
                )
                return super().std(
                    axis=axis,
                    skipna=skipna,
                    level=level,
                    ddof=ddof,
                    numeric_only=numeric_only,
                    **kwargs,
                )

            logging.warn("Ignoring `ddof` with `target_epsilon` > 0.")

            # Select numeric columns only
            numeric_columns = [
                feature["name"]
                for feature in self.dataset.features
                if list(feature["type"].keys())[0] in ["integer", "real"]
            ]
            non_numeric_columns = [
                feature["name"]
                for feature in self.dataset.features
                if feature["name"] not in numeric_columns
            ]
            if verbose:
                logging.info(
                    "Dropping non numeric column:",
                    ", ".join(non_numeric_columns),
                )

            # Build query
            # Need to be careful with quotes ordering: put " " inside ' '
            values = [
                f'STDDEV("{column}") as "stddev_{column.lower()}"'
                for column in numeric_columns
            ]
            query = f'SELECT {", ".join(values)} FROM {self.dataset.name}'
            if verbose:
                logging.info(query)
            response = self.dataset.client.query(
                query=query, target_epsilon=target_epsilon, verbose=True
            )

            # Return result as a pd.Series with original column names
            if response["status"] == "SUCCESS":
                result = response["result"][0]
                API_columns = response["columns"]
                name_mapping = {
                    f"stddev_{column.lower()}": column
                    for column in numeric_columns
                }
                result = {
                    name_mapping[col]: result[idx]
                    for idx, col in enumerate(API_columns)
                }
                return pd.Series(result)
            else:
                raise Exception(f"The query {query} failed.")

    def sum(
        self,
        axis: int = 0,
        skipna: bool = True,
        level: Optional[Union[int, str]] = None,
        numeric_only: Optional[bool] = True,
        min_count: int = 0,
        target_epsilon: Optional[float] = None,
        verbose: bool = False,
        **kwargs,
    ):
        """Return the sum of the values over the requested axis.

        Execute the standard pandas method if `target_epsilon` is zero. If
        `target_epsilon` is greater than zero, it builds and sends a private
        query for execution on the Sarus server.

        Args:
            axis (int): Axis for the function to be applied on.
                Only axis=0 is supported when `target_epsilon` > 0 for DP
                reasons.
            skipna (bool): Exclude NA/null values when computing the result.
            level (int, level name):
                If the axis is a MultiIndex (hierarchical), count along a
                particular level, collapsing into a Series.
            numeric_only (bool):
                Include only float, int, boolean columns. If None, will attempt
                to use everything, then use only numeric data. Not implemented
                for Series.
            min_count (int):
                Include only float, int, boolean columns. If None, will attempt
                to use everything, then use only numeric data. Not implemented
                for Series.
            target_epsilon (Optional[float]):
                Maximum privacy budget (epsilon) to assign to the sum computation
                of all relevant columns.
                If 0, runs on the synthetic data.
                If >0, each column result is a combination of a query on the synthetic
                data and a Differentially-Private query on the real data.
                If None, a default target epsilon specific to the current user and access rule is used.
                Default target epsilon is 0 if the access is a Differentially-Private access with
                per-user or per-group limit; default value equals to per-query limit if the access is
                a Differentially-Private access with a per-query limit only. Meaning Sarus maximizes result
                accuracy in the given privacy constraints. See user documentation to know more.

        Returns:
            A pandas.Series.
        """
        if target_epsilon == 0.0:
            return super().sum(axis, skipna, level, numeric_only, min_count)
        else:
            # Check parameters
            if axis == 1:
                logging.warn(
                    "Cannot query `sum` with `axis`=1 on private dataset. "
                    "Computing on synthetic data."
                )
                return super().sum(axis, skipna, level, numeric_only, min_count)

            if numeric_only is False:
                logging.warn(
                    "Cannot query `sum` of non numeric columns "
                    "`numeric_only`=False on private dataset. Computing on "
                    "synthetic data."
                )
                return super().sum(axis, skipna, level, numeric_only, min_count)

            if min_count != 0:
                logging.warn(
                    "Cannot query `sum` with `min_count`!=0 on private "
                    "dataset. Computing on synthetic data."
                )
                return super().sum(axis, skipna, level, numeric_only, min_count)

            # Select numeric columns only
            numeric_columns = [
                feature["name"]
                for feature in self.dataset.features
                if list(feature["type"].keys())[0] in ["integer", "real"]
            ]
            non_numeric_columns = [
                feature["name"]
                for feature in self.dataset.features
                if feature["name"] not in numeric_columns
            ]
            if verbose:
                logging.info(
                    "Dropping non numeric column:",
                    ", ".join(non_numeric_columns),
                )

            # Build query
            # Need to be careful with quotes ordering: put " " inside ' '
            values = [
                f'SUM("{column}") as "sum_{column.lower()}"'
                for column in numeric_columns
            ]
            query = f'SELECT {", ".join(values)} FROM {self.dataset.name}'
            if verbose:
                logging.info(query)
            response = self.dataset.client.query(
                query=query, target_epsilon=target_epsilon, verbose=True
            )

            # Return result as a pd.Series with original column names
            if response["status"] == "SUCCESS":
                result = response["result"][0]
                API_columns = response["columns"]
                name_mapping = {
                    f"sum_{column.lower()}": column
                    for column in numeric_columns
                }
                result = {
                    name_mapping[col]: result[idx]
                    for idx, col in enumerate(API_columns)
                }
                return pd.Series(result)
            else:
                raise Exception(f"The query {query} failed.")
