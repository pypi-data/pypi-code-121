"""Base splitter classes."""
# pylint: disable=invalid-name
import abc
import typing as t

import numpy as np
import pandas as pd
from fw_file.base import File
from fw_file.dicom import DICOMCollection


class SplitterError(RuntimeError):
    """Wrapper for splitter errors."""

    pass


class Splitter(abc.ABC):
    """Abstract class for splitting DICOMCollections."""

    def __init__(  # pylint: disable=unused-argument
        self, files: DICOMCollection, decision_val: int = 10, **options: t.Any
    ) -> None:
        """Instantiate new splitter for DICOMCollection.

        Args:
            files (DICOMCollection): Collection of files.
            decision_val (int): Value to assign to frames that are decided
                to be different by splitter (other frames get 0).
                Defaults to 10.
            options (t.Any): Keyword arguments to be handled by subclasses
        """
        self.files = files
        self.decision_val = decision_val

    def get_neighbor_dist(
        self,
        dataframe: pd.DataFrame,
        dist_fn: t.Callable[[File, File], float],
    ) -> None:
        """Populate column of distance to neighbor file(s).

        Note: Modifies dataframe in place.

        Args:
            dataframe (pd.DataFrame): Sorted pandas dataframe representation of
                `self.files`.
            dist_fn (t.Callable[[File. File], float]: A distance function
                that takes in two files and returns a float 'distance'.
        """
        vals: t.List[float] = []
        for row in range(len(self.files)):
            dist: float = 0
            if row == len(self.files) - 1:
                vals.append(dist)
                continue
            dist = dist_fn(self.files[row], self.files[row + 1])

            vals.append(dist)
        dataframe.insert(dataframe.shape[1], "value", vals)

    @abc.abstractmethod
    def calc_value(self, dataframe: pd.DataFrame) -> pd.DataFrame:  # pragma: no cover
        """Calculate corresponding value column(s) for decision function.

        Subclass will implement specific method based on splitting
        strategy.

        Args:
            dataframe (pd.DataFrame): Sorted pandas dataframe representation of
                `self.files`.

        Raises:
            NotImplementedError: Must be implemented by subclass.

        Returns:
            pd.DataFrame: DataFrame with the same columns, plus new
                column(s) for use by decision function.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def decision(  # pragma: no cover
        self, dataframe: pd.DataFrame, **kwargs: t.Any
    ) -> t.Union[t.Tuple[pd.DataFrame, ...], pd.DataFrame]:
        """Make splitting decision based on value column(s).

        Args:
            dataframe (pd.DataFrame): Pandas dataframe representation of
                `self.files` with added columns for decision.
            kwargs (t.Any): Specific keywords arguments for use by
                subclasses.

        Raises:
            NotImplementedError: Must be implemented by subclass

        Returns:
            either:
                (pd.DataFrame): Dataframe of files that belong in primary
                    (largest) collection.
                (tuple(pd.DataFrame,...): Dataframe(s) of other files
                    grouped according to subclass splitting method.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def split(  # pragma: no cover
        self, dataframe: pd.DataFrame, **kwargs: t.Any
    ) -> t.Union[t.Tuple[DICOMCollection, ...], DICOMCollection]:
        """Run splitting algorithm.

        Args:
            dataframe (pd.DataFrame): Dataframe representing `self.files`

        Raises:
            NotImplementedError: Must be implemented by subclass.

        Returns:
            t.Tuple[DICOMCollection, ...]: two or more
                DICOMCollections depending on implementation.
        """
        raise NotImplementedError

    def neighbor_decision(self, dataframe: pd.DataFrame, thresh: float) -> pd.DataFrame:
        """Apply neighbor based decision value."""
        # Find split indices
        indices = sorted(np.where(dataframe["p"] < thresh)[0])
        # Assign a group to each split section of DF
        dataframe["split_group"] = 0
        for index in indices:
            dataframe.loc[dataframe.index > index, "split_group"] += 1
        # Collapse groups down to two
        dataframe.loc[:, "split_group"] %= 2
        splits = dataframe.groupby("split_group")
        # Assign larger of two groups to be the dicom
        dicom = np.argmax(splits.size())
        # Apply decision value to dicom/localizer groups
        dataframe.loc[dataframe["split_group"] == dicom, "decision"] = 0
        dataframe.loc[dataframe["split_group"] != dicom, "decision"] = self.decision_val
        dataframe = dataframe.drop(["value", "p", "split_group"], axis=1)
        return dataframe


class SingleSplitter(Splitter):
    """Split one DICOMCollection in two.

    in: One DICOMCollection
    out: Two DICOMCollections
    """

    def split(self, dataframe: pd.DataFrame, **kwargs: t.Any) -> pd.DataFrame:
        """Run splitting algorithm.

        Args:
            dataframe (pd.DataFrame): Dataframe representing `self.files`

        Returns:
            t.Tuple[DICOMCollection, ...]: two DICOMCollections.
        """
        # Populate initial values
        split_dataframe = dataframe.copy(deep=True)

        value_dataframe = self.calc_value(split_dataframe)
        dec = self.decision(value_dataframe, **kwargs)

        return dec


class MultiSplitter(Splitter):
    """Split one DICOMCollection into multiple others.

    in: One DICOMCollection
    out: Two or more DICOMCollections
    """

    def split(
        self, dataframe: pd.DataFrame, **kwargs: t.Any
    ) -> t.Tuple[pd.DataFrame, ...]:
        """Run splitting algorithm.

        Args:
            dataframe (pd.DataFrame): Dataframe representing `self.files`

        Returns:
            t.Tuple[pd.DataFrame, ...]: two or more DICOMCollections.
        """
        primary_dataframe = dataframe.copy(deep=True)

        value_dataframe = self.calc_value(primary_dataframe)
        out_dataframe = self.decision(value_dataframe)

        return tuple(out_dataframe)
