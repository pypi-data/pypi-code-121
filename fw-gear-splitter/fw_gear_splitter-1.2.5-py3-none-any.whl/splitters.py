"""Splitter implementations."""
# pylint: disable=invalid-name
import typing as t
import warnings

import numpy as np
import pandas as pd
from fw_file.base import File
from fw_file.dicom import DICOM, DICOMCollection
from scipy.spatial.distance import euclidean, jensenshannon
from scipy.stats import beta, halfnorm

from .splitter.base import MultiSplitter, SingleSplitter, SplitterError
from .utils import quote_val

__all__ = ["EuclideanSplitter", "JensenShannonDICOMSplitter"]


class EuclideanSplitter(SingleSplitter):
    """Euclidean metric based splitter."""

    def __init__(
        self,
        files: DICOMCollection,
        decision_val: int = 10,
        tag: str = "ImageOrientationPatient",
    ) -> None:
        """Initiate euclidean splitter.

        The euclidean splitter compares neighbor files by computing
        the euclidean distance between the files on a specific tag.

        The tag provided `tag` must be castable into a numpy array
        for calculating euclidean distance.

        Args:
            files (DICOMCollection): DICOMCollection to split.
            decision_val (int): Value to assign to frames that are decided
                to be different by splitter (other frames get 0).
                Defaults to 10.
            tag (str, optional): File attribute to make splitting
                decisions on, must be a value that can be casted
                to a numpy array. Defaults to
                "ImageOrientationPatient".
        """
        super().__init__(files, decision_val)
        self.tag = tag

    def calc_value(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calculate corresponding value column(s) for decision function.

        Subclass will implement specific method based on splitting
        strategy.

        Args:
            dataframe (pd.DataFrame): Sorted pandas dataframe representation of
                `self.files`.

        Returns:
            pd.DataFrame: DataFrame with the same columns, plus new
                column(s) for use by decision function.
        """

        def dist_fn(dcm1: File, dcm2: File) -> float:
            """Calculate euclidean distance between two files."""
            return np.round(
                euclidean(np.array(dcm1.get(self.tag)), np.array(dcm2.get(self.tag))), 3
            )

        self.get_neighbor_dist(dataframe, dist_fn)

        return dataframe

    def decision(  # type: ignore
        self,
        dataframe: pd.DataFrame,
        thresh: float = 0.01,
    ) -> pd.DataFrame:
        """Make splitting decision based on value column.

        Args:
            dataframe (pd.DataFrame): Pandas dataframe representation of
                `self.files` with added 'value' column.
            thresh (float): p-value threshold for Id of localizer.
                Defaults to 0.01.

        Returns:
            (pd.DataFrame): Dataframe with decision column populated.
        """
        if len(pd.unique(dataframe["value"])) == 1:
            dataframe["decision"] = 0
            dataframe = dataframe.drop("value", axis=1)
        else:
            val_mean = np.mean(dataframe.loc[:, "value"])
            val_std = np.std(dataframe.loc[:, "value"])
            # Use halfnorm here where the random variable is the distance
            # between the value and the mean.  Will always be >0 with the highest
            # probability being when the value is at the mean, and getting lower
            # the further away from mean.
            dist = halfnorm(loc=0, scale=val_std)
            dataframe["p"] = dist.sf(np.abs(dataframe.loc[:, "value"] - val_mean))
            dataframe = self.neighbor_decision(dataframe, thresh)
        return dataframe


class JensenShannonDICOMSplitter(SingleSplitter):
    """Jensen-shannon metric based DICOM splitter."""

    @staticmethod
    def dist_fn(dcm1: DICOM, dcm2: DICOM) -> float:
        """Calculate distance between two dicom images."""
        try:
            pixels1 = dcm1.dataset.raw.pixel_array.ravel()
            pixels2 = dcm2.dataset.raw.pixel_array.ravel()
        except ValueError as e:
            raise SplitterError(
                "Could not run JensenShannonDICOMSplitter: " + e.args[0]
            ) from e
        bounds1 = np.percentile(pixels1, [2, 98])
        bounds2 = np.percentile(pixels2, [2, 98])
        scaled1 = pixels1[(pixels1 >= bounds1[0]) & (pixels1 <= bounds1[1])]
        scaled2 = pixels2[(pixels2 >= bounds2[0]) & (pixels2 <= bounds2[1])]
        dist1, _ = np.histogram(scaled1, bins=1000)
        dist2, _ = np.histogram(scaled2, bins=1000)
        return jensenshannon(dist1, dist2)

    def calc_value(self, dataframe: pd.DataFrame) -> pd.DataFrame:  # pragma: no cover
        """Calculate corresponding value column(s) for decision function.

        Args:
            in_dataframe (pd.DataFrame): Sorted pandas dataframe representation of
                `self.files`.

        Returns:
            pd.DataFrame: DataFrame with the same columns, plus new
                column(s) for use by decision function.
        """
        self.get_neighbor_dist(dataframe, self.dist_fn)
        return dataframe

    def decision(  # type: ignore
        self,
        dataframe: pd.DataFrame,
        thresh: float = 0.01,
        drop_cols: t.Optional[t.List[str]] = None,
    ) -> t.Tuple[pd.DataFrame, pd.DataFrame]:
        """Make splitting decision based on jensen-shannon distance.

        Args:
            dataframe (pd.DataFrame): Pandas dataframe representation of
                `self.files` with added 'value' column.
            thresh (float): p-value threshold for Id of localizer.
                Defaults to 0.01.
            drop_cols (t.List[str]): Columns to drop when returning dataframe.
                Defaults to ['value','p'] since those columns were added
                during `calc_value` and this function.

        Returns:
            t.Tuple[pd.DataFrame, pd.DataFrame]:
                1. Dataframe of files that belong in primary (largest)
                    collection.
                2. Dataframe of other files.
        """
        if not drop_cols:
            drop_cols = ["value", "p"]

        # Beta fit can raise a RuntimeError which is caught and handled in
        # main.gen_split_score.  It also raises some warnings that make it to
        # the console, we don't need these since the error is already handled.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dist_params = beta.fit(
                dataframe[(dataframe["value"] != 0) & (dataframe["value"] != 1)][
                    "value"
                ],
                floc=0,
                fscale=1,
            )
            dist = beta(*dist_params)

        dataframe["p"] = dist.sf(dataframe["value"])

        dataframe = self.neighbor_decision(dataframe, thresh)
        return dataframe


class UniqueTagSingleSplitter(SingleSplitter):
    """Uniqueness based splitter."""

    def __init__(
        self,
        files: DICOMCollection,
        decision_val: int = 10,
        tags: t.Optional[t.List[str]] = None,
    ) -> None:
        """Initiate UniqueTagSingleSplitter.

        Splits a dicom archive into two groups based on unique combinations
        of tags specified.

        This splitter will return only two dicom collections, the splitter
        will find the combination of specified tags which comprise the
        largest number of frames and return this as the primary collection,
        all other unique values will be grouped together and returned
        as the secondary collection.

        Args:
            files (DICOMCollection): DICOMCollection to split.
            decision_val (int): Value to assign to frames that are decided
                to be different by splitter (other frames get 0).
                Defaults to 10.
            tags (t.List[str]): File attribute to make splitting
                decisions on.
        """
        super().__init__(files, decision_val)
        self.tags = sorted(tags)

    def calc_value(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calculate 'value' column for decision function.


        Args:
            in_dataframe (pd.DataFrame): Sorted pandas dataframe representation of
                `self.files`.

        Returns:
            pd.DataFrame: DataFrame with the same columns, plus tag columns
                for decision function.
        """

        def calc_row(row: pd.Series) -> pd.Series:
            dcm = self.files[row.name]
            row_indices = []
            row_data = []

            for tag in self.tags:
                val = dcm.get(tag)
                if isinstance(val, list):
                    val = tuple(val)
                row_data.append(val)
                row_indices.append(tag)

            return pd.Series(data=row_data, index=row_indices)

        dataframe.loc[:, self.tags] = dataframe.apply(calc_row, axis=1)

        return dataframe

    def decision(  # type: ignore # pylint: disable=unused-variable
        self,
        dataframe: pd.DataFrame,
        drop_cols: t.Optional[t.List[str]] = None,
    ) -> t.Tuple[pd.DataFrame, pd.DataFrame]:
        """Make splitting decision based on multiple unique tags.

        Args:
            dataframe (pd.DataFrame): Pandas dataframe representation of
                `self.files` with added columns for decision.
            drop_cols (t.List[str]): Columns to drop when returning dataframes.
                Defaults to ['value'] since those columns were added
                during `calc_value`.

        Returns:
            t.Tuple[pd.DataFrame, pd.DataFrame]
                1. Dataframe containing paths of dicom frames that belong
                    in main archive
                2. Dataframe containing paths of frames that belong in
                    localizer
        """
        if not drop_cols:
            drop_cols = ["value", "p"]
        unique = dataframe.groupby(self.tags).size().reset_index()
        primary_val = unique.iloc[unique.iloc[:, -1].idxmax(), :]
        values = [getattr(primary_val, tag) for tag in self.tags]
        query = []
        # for tag, val in zip(self.tags, values):
        #    query.append(f"{tag} == {quote_val(val)}")
        for i, tag in enumerate(self.tags):
            query.append(f"dataframe.{tag} == values[{i}]")
        query_str = " and ".join(query)
        primary_idx = pd.eval(query_str)
        dataframe.loc[primary_idx, "decision"] = 0
        # TODO: pylint complains invalid unary operator, however
        # this is what pandas docs says to do, leaving complaint
        # For future test case...
        dataframe.loc[~primary_idx, "decision"] = self.decision_val

        return dataframe


class UniqueTagMultiSplitter(MultiSplitter):
    """Uniqueness based splitter."""

    def __init__(
        self,
        files: DICOMCollection,
        decision_val: int = 10,
        tags: t.Optional[t.List[str]] = None,
    ) -> None:
        """Initiate UniqueTagMultiSplitter.

        Splits a dicom archive into two or more groups based on unique
        combinations of tags specified.

        This splitter returns dicom collections for each unique group
        of tags specified.

        Args:
            files (DICOMCollection): DICOMCollection to split.
            decision_val (int): Value to assign to frames that are decided
                to be different by splitter (other frames get 0).
                Defaults to 10.
            tags (t.List[str]): File attribute to make splitting
                decisions on.
        """
        super().__init__(files, decision_val)
        self.tags = sorted(tags)

    def calc_value(self, in_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calculate 'value' column for decision function.


        Args:
            in_dataframe (pd.DataFrame): Sorted pandas dataframe representation of
                `self.files`.

        Returns:
            pd.DataFrame: DataFrame with the same columns, plus tag columns
                for decision function.
        """
        dataframe = in_dataframe.copy(deep=True)

        def calc_row(row: pd.Series) -> pd.Series:
            dcm = self.files[row.name]
            row_indices = []
            row_data = []

            for tag in self.tags:
                val = dcm.get(tag)
                if isinstance(val, list):
                    val = tuple(val)
                row_data.append(val)
                row_indices.append(tag)

            return pd.Series(data=row_data, index=row_indices)

        dataframe.loc[:, self.tags] = dataframe.apply(calc_row, axis=1)

        return dataframe

    def decision(  # type: ignore
        self,
        dataframe: pd.DataFrame,
        drop_cols: t.Optional[t.List[str]] = None,
    ) -> t.Tuple[pd.DataFrame, ...]:
        """Make splitting decision based on multiple unique tags.

        Args:
            dataframe (pd.DataFrame): Pandas dataframe representation of
                `self.files` with added columns for decision.
            drop_cols (t.List[str]): Columns to drop when returning dataframes.
                Defaults to ['value'] since those columns were added
                during `calc_value`.

        Returns:
            t.Tuple[pd.DataFrame, ...]
                1. Dataframe containing paths of dicom frames that belong
                    in main archive
                ... Dataframes of other unique groups
        """
        if not drop_cols:
            drop_cols = ["value", "p"]

        unique = dataframe.groupby(self.tags)
        return tuple([unique.get_group(g) for g in unique.groups])
