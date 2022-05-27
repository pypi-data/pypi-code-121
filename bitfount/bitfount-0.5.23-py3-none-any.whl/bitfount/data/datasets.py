"""Classes concerning datasets."""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    OrderedDict,
    Sequence,
    Tuple,
    Union,
    cast,
)

import numpy as np
import pandas as pd
from skimage import color, io
from sqlalchemy import text

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasplitters import DatasetSplitter, PercentageSplitter
from bitfount.data.exceptions import DataNotLoadedError
from bitfount.data.types import DataSplit
from bitfount.transformations.base_transformation import Transformation
from bitfount.transformations.processor import TransformationProcessor
from bitfount.utils import _array_version

if TYPE_CHECKING:

    from bitfount.data.schema import TableSchema
    from bitfount.data.types import (
        _DataEntry,
        _ImagesData,
        _SemanticTypeValue,
        _SupportData,
        _TabularData,
    )
    from bitfount.transformations.batch_operations import BatchTimeOperation

logger = logging.getLogger(__name__)


class _BaseBitfountDataset(ABC):
    """Base class for representing a dataset."""

    x_columns: List[str]
    x_var: Tuple[Any, Any, np.ndarray]
    y_columns: List[str]
    y_var: np.ndarray

    embedded_col_names: List[str]
    image_columns: List[str]
    processors: Dict[int, TransformationProcessor]
    image: np.ndarray
    tabular: np.ndarray
    support_cols: np.ndarray

    def __init__(
        self,
        datasource: _BaseSource,
        data_split: DataSplit,
        schema: TableSchema,
        selected_cols: List[str],
        selected_cols_semantic_types: Mapping[_SemanticTypeValue, List[str]],
        data_splitter: Optional[DatasetSplitter] = None,
        target: Optional[Union[str, List[str]]] = None,
        batch_transforms: Optional[List[BatchTimeOperation]] = None,
        weights_col: Optional[str] = None,
        multihead_col: Optional[str] = None,
        ignore_classes_col: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.datasource = datasource
        self.schema = schema
        self.selected_cols = selected_cols
        self.selected_cols_semantic_types = selected_cols_semantic_types
        self.data_splitter = data_splitter
        self.target = target
        self.batch_transforms = batch_transforms
        self.data_split = data_split
        self.weights_col = weights_col
        self.multihead_col = multihead_col
        self.ignore_classes_col = ignore_classes_col

        self._set_column_name_attributes()
        self._set_batch_transformation_processors()

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    def _apply_schema(self, data: pd.DataFrame) -> None:
        """Applies `self.schema` to `data` and sets the result to `self.data`.

        `selected_cols` needs to be passed to the `apply` method here to ensure
        that we don't end up removing the extra columns in our dataframe that are
        used during training (e.g. loss_weights_col, etc.) but aren't part of the
        schema. Applying the schema adds extra columns to the dataframe if they
        are missing. Therefore we need to subset the data columns here to ensure
        we are only using the columns specified for this task
        """
        diff = list(sorted(set(self.selected_cols) - set(data.columns)))
        if diff:
            logger.warning(
                f"Selected columns `{','.join(diff)}` "
                f"were not found in the data, continuing without them."
            )
            self.selected_cols = [i for i in self.selected_cols if i not in diff]

        self.data = self.schema.apply(data, keep_cols=self.selected_cols)[
            self.selected_cols
        ].reset_index(drop=True)

    def _set_column_name_attributes(self) -> None:
        """Sets the attributes concerning column names.

        Namely, `self.x_columns`, `self.y_columns`, `self.embedded_col_names`,
        and `self.image_columns`.
        """
        self.image_columns = self.selected_cols_semantic_types.get("image", [])
        self.embedded_col_names = self.selected_cols_semantic_types.get(
            "categorical", []
        )
        self.x_columns = (
            self.embedded_col_names
            + self.selected_cols_semantic_types.get("continuous", [])
            + self.selected_cols_semantic_types.get("image", [])
        )
        if self.target is not None:
            self.y_columns = _array_version(self.target)
            self.embedded_col_names = [
                i for i in self.embedded_col_names if i not in self.y_columns
            ]
            self.x_columns = [i for i in self.x_columns if i not in self.y_columns]

    def _set_batch_transformation_processors(self) -> None:
        """Sets `self.processors` for batch transformations."""
        if self.batch_transforms is not None:
            # We create a dictionary mapping each image feature to the corresponding
            # list of transformations. This dictionary must be an OrderedDict so that
            # the order of the features is preserved and indexable. Currently, we only
            # support image transformations at batch time.
            feature_transforms: OrderedDict[
                str, List[BatchTimeOperation]
            ] = OrderedDict(
                {i: [] for i in self.selected_cols_semantic_types.get("image", [])}
            )

            for tfm in self.batch_transforms:
                if tfm.arg in feature_transforms:
                    feature_transforms[tfm.arg].append(tfm)

            # Each feature that will be transformed needs to have its own transformation
            # processor. These processors need to correspond to the index of the feature
            # to be transformed because at batch time, the feature name is unavailable -
            # we only have the feature index. Finally, we only leave transformations if
            # the 'step' corresponds to the 'step' of the Dataset. This is to optimise
            # for efficiency only since the processor will ignore transformations that
            # are not relevant to the current step at batch time anyway.
            self.processors: Dict[int, TransformationProcessor] = {
                list(feature_transforms).index(col): TransformationProcessor(
                    [
                        cast(Transformation, i)
                        for i in tfms
                        if i.step == self.data_split
                    ],
                )
                for col, tfms in feature_transforms.items()
            }

    def _transform_image(self, img: np.ndarray, idx: int) -> np.ndarray:
        """Performs image transformations if they have been specified.

        Args:
            img: The image to be transformed.
            idx: The index of the image.

        Returns:
            The transformed image.

        """
        if not self.batch_transforms:
            return img

        return self.processors[idx].batch_transform(img, step=self.data_split)

    def _load_images(
        self, idx: Union[int, Sequence[int]]
    ) -> Union[np.ndarray, Tuple[np.ndarray, ...]]:
        """Loads images and performs transformations if specified.

        This involves first converting grayscale images to RGB if necessary.

        Args:
            idx: The index to be loaded.

        Returns:
            Loaded and transformed image.

        """
        img_features = self.image[idx]
        imgs: Tuple[np.ndarray, ...] = tuple(
            io.imread(image, plugin="pil") for image in img_features
        )
        imgs = tuple(
            color.gray2rgb(image_array) if len(image_array.shape) < 3 else image_array
            for image_array in imgs
        )
        imgs = tuple(
            self._transform_image(image_array, i) for i, image_array in enumerate(imgs)
        )

        if len(img_features) == 1:
            return imgs[0]

        return imgs

    def _set_support_column_values(self, data: pd.DataFrame) -> None:
        """Sets `self.support_cols` - auxiliary columns for loss manipulation."""
        if self.weights_col:
            weights = data.loc[:, [self.weights_col]].values.astype(np.float32)
            self.x_columns.append(self.weights_col)
        else:
            weights = np.ones(len(data), dtype=np.float32)
        weights = weights.reshape(len(weights), 1)

        if self.ignore_classes_col:
            ignore_classes = data.loc[:, [self.ignore_classes_col]].values.astype(
                np.int64
            )
        else:
            ignore_classes = -np.ones(len(data), dtype=np.int64)
        ignore_classes = ignore_classes.reshape(len(ignore_classes), 1)

        if self.multihead_col:
            category = data.loc[:, [self.multihead_col]].values
            category = category.reshape(len(category), 1)
            self.support_cols = cast(
                np.ndarray, np.concatenate((weights, ignore_classes, category), axis=1)
            )
        else:
            self.support_cols = cast(
                np.ndarray, np.concatenate((weights, ignore_classes), axis=1)
            )

    def _set_image_values(self, data: pd.DataFrame) -> None:
        """Sets `self.image`."""
        if self.image_columns != []:
            for (i, col) in enumerate(self.image_columns):
                x_img = np.expand_dims(data.loc[:, col].values, axis=1)
                if i == 0:
                    self.image = x_img

                else:
                    self.image = np.concatenate((self.image, x_img), axis=1)
        else:
            self.image = np.array([])

    def _set_tabular_values(self, data: pd.DataFrame) -> None:
        """Sets `self.tabular`."""
        x1_var = data.loc[:, self.embedded_col_names].values.astype(np.int64)
        x2_var = data.loc[
            :, self.selected_cols_semantic_types.get("continuous", [])
        ].values.astype(np.float32)
        self.tabular = np.concatenate((x1_var, x2_var), axis=1)

    def _set_target_values(
        self, target: Optional[Union[pd.DataFrame, pd.Series]]
    ) -> None:
        """Sets `self.y_var`."""
        if target is not None:
            self.y_var = cast(np.ndarray, target.values)
        else:
            self.y_var = np.array([])

    def _get_xy(
        self, data: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Optional[Union[pd.DataFrame, pd.Series]]]:
        """Returns the x and y variables.

        By default, there is no target unless `self.target` has been specified.
        """
        X, Y = data, None

        if self.target is not None:
            # ignore error if target is already not part of the X data
            X = X.drop(columns=self.target, errors="ignore").reset_index(drop=True)
            Y = data[self.target].reset_index(drop=True)
        return X, Y

    def _getitem(self, idx: Union[int, Sequence[int]]) -> _DataEntry:
        """Returns the item referenced by index `idx` in the data."""
        image: _ImagesData
        tab: _TabularData
        sup: _SupportData

        # Set the target, if the dataset has no supervision,
        # choose set the default value to be 0.
        target = self.y_var[idx] if len(self.y_var) else np.array(0)

        # If the Dataset contains both tabular and image data
        if self.image.size and self.tabular.size:
            tab = self.tabular[idx]
            sup = self.support_cols[idx]
            image = self._load_images(idx)
            return (tab, image, sup), target

        # If the Dataset contains only tabular data
        elif self.tabular.size:
            tab = self.tabular[idx]
            sup = self.support_cols[idx]
            return (tab, sup), target

        # If the Dataset contains only image data
        else:
            sup = self.support_cols[idx]
            image = self._load_images(idx)
            return (image, sup), target

    def _reformat_data(self, data: pd.DataFrame) -> None:
        """Reformats the data to be compatible with the Dataset class."""
        self._apply_schema(data)
        X, Y = self._get_xy(self.data)

        self._set_image_values(X)
        self._set_tabular_values(X)
        self._set_support_column_values(X)
        # Package tabular, image and support columns together under the x_var attribute
        self.x_var = (self.tabular, self.image, self.support_cols)
        self._set_target_values(Y)

    def _resolve_data_splitter(
        self,
        data_splitter: Optional[DatasetSplitter] = None,
    ) -> DatasetSplitter:
        """Resolves the data splitter.

        The data splitter is resolved in the following order:
            1. _BaseSource data_splitter if specified
            2. Provided data_splitter if specified
            3. PercentageSplitter (default)

        Returns:
            The appropriate data splitter to use.
        """
        if self.datasource.data_splitter:
            if data_splitter:
                logger.warning(
                    "Ignoring provided data splitter as the _BaseSource "
                    "already has one."
                )
            data_splitter = self.datasource.data_splitter
        elif not data_splitter:
            logger.warning(
                "No data splitter provided. Using default PercentageSplitter."
            )
            data_splitter = PercentageSplitter()

        return data_splitter

    def _split_data(self, data_splitter: Optional[DatasetSplitter] = None) -> None:
        """Split the data into training, validation and test datasets.

        This method is idempotent so it can be called multiple times without
        re-splitting the data.

        Args:
            data_splitter: An optional data splitter object.
        """
        if not self.datasource._data_is_split:
            data_splitter = self._resolve_data_splitter(data_splitter)
            assert self.datasource.data is not None  # nosec

            (
                self.datasource._train_idxs,
                self.datasource._validation_idxs,
                self.datasource._test_idxs,
            ) = data_splitter.create_dataset_splits(self.datasource.data)

            self.datasource._data_is_split = True
        else:
            logger.debug("Data is already split, keeping the current split.")

    def get_dataset_split_length(
        self, split: DataSplit, data_splitter: Optional[DatasetSplitter] = None
    ) -> int:
        """Returns the length of the specified dataset split.

        Args:
            split: The split to get the length of.
            data_splitter: The splitter object used to split the data if the _BaseSource
                does not have one.

        Returns:
            The length of the specified dataset split.

        Raises:
            DataNotLoadedError: If unable to get the length of the dataset split.
        """
        data_splitter = self._resolve_data_splitter(data_splitter)

        # If PercentageSplitter is used regardless of the data loader.
        if isinstance(data_splitter, PercentageSplitter):
            len_loader = len(self.datasource)
            if split == DataSplit.TRAIN:
                return int(len_loader * data_splitter.train_percentage / 100)
            elif split == DataSplit.VALIDATION:
                return int(len_loader * data_splitter.validation_percentage / 100)
            elif split == DataSplit.TEST:
                return int(len_loader * data_splitter.test_percentage / 100)

        # If the data is held in memory with any other splitter.
        elif self.datasource._data_is_loaded:
            return len(self.get_dataset_split(split=split, data_splitter=data_splitter))

        # If the data is held in a database with any other splitter. This is because
        # it requires the database to be queried in order to determine the length of
        # a split e.g. `SplitterDefinedInData`
        elif isinstance(self.datasource, DatabaseSource):
            query = self._resolve_data_splitter(data_splitter).get_split_query(
                self.datasource, split
            )
            with self.datasource.con.connect() as con:
                # Ignoring the security warning because the sql query is trusted and
                # will be executed regardless.
                result = con.execute(text(f"SELECT COUNT(*) FROM ({query}) q"))  # nosec
                return cast(int, result.scalar_one())

        # `load_data` should be called to avoid this error being raised
        raise DataNotLoadedError("Unable to get length of dataset split")

    def get_dataset_split(
        self,
        split: DataSplit,
        data_splitter: Optional[DatasetSplitter] = None,
    ) -> pd.DataFrame:
        """Returns the relevant portion of `self.data`.

        Args:
            split: The portion of data to return.
            data_splitter: The splitter object used to split the data.

        Returns:
            A dataframe-type object containing the data points specified by the data
            splitter.

        Raises:
            DataNotLoadedError: If data has not been loaded.
        """
        if not self.datasource._data_is_loaded:
            raise DataNotLoadedError(
                "Please load data before accessing a split. "
                "If the data is remote, it must be iterated."
            )

        self._split_data(data_splitter)  # idempotent
        indices: np.ndarray = getattr(self.datasource, f"_{split.value}_idxs")
        df: pd.DataFrame = self.datasource.data.loc[indices.tolist()]
        return df.reset_index(drop=True)


class _BitfountDataset(_BaseBitfountDataset):
    """A dataset for supervised tasks.

    When indexed, returns numpy arrays corresponding to
    categorical features, continuous features, weights and target value (and
    optionally category)
    """

    def __init__(
        self,
        datasource: _BaseSource,
        data_split: DataSplit,
        schema: TableSchema,
        selected_cols: List[str],
        selected_cols_semantic_types: Mapping[_SemanticTypeValue, List[str]],
        data_splitter: Optional[DatasetSplitter] = None,
        target: Optional[Union[str, List[str]]] = None,
        batch_transforms: Optional[List[BatchTimeOperation]] = None,
        weights_col: Optional[str] = None,
        multihead_col: Optional[str] = None,
        ignore_classes_col: Optional[str] = None,
    ) -> None:
        super().__init__(
            datasource=datasource,
            data_split=data_split,
            schema=schema,
            selected_cols=selected_cols,
            selected_cols_semantic_types=selected_cols_semantic_types,
            data_splitter=data_splitter,
            target=target,
            batch_transforms=batch_transforms,
            weights_col=weights_col,
            multihead_col=multihead_col,
            ignore_classes_col=ignore_classes_col,
        )

        data = self.get_dataset_split(
            split=self.data_split, data_splitter=self.data_splitter
        )
        self._reformat_data(data)

    def __len__(self) -> int:
        return len(self.x_var[0])


class _IterableBitfountDataset(_BaseBitfountDataset):
    """Iterable Dataset.

    Currently, this is only used for Database connections.
    """

    def __iter__(self) -> Iterator[_DataEntry]:
        """Iterates over the dataset."""
        for data_partition in self.yield_dataset_split(
            split=self.data_split, data_splitter=self.data_splitter
        ):
            self._reformat_data(data_partition)

            for idx in range(len(self.data)):
                yield self._getitem(idx)

    @cached_property
    def _len(self) -> int:
        """Returns the length of the dataset."""
        return self.get_dataset_split_length(
            split=self.data_split, data_splitter=self.data_splitter
        )

    def __len__(self) -> int:
        return self._len

    def yield_dataset_split(
        self,
        split: DataSplit,
        data_splitter: Optional[DatasetSplitter] = None,
    ) -> Iterator[pd.DataFrame]:
        """Returns an iterator over the relevant data split.

        Args:
            split: The portion of data to yield from.
            data_splitter: The splitter object used to split the data.

        Returns:
            A iterator of pandas dataframes containing the relevant data split.

        Raises:
            ValueError: If no query or table name has been supplied for multi-table
                data.
            ValueError: If attempting to iterate over in-memory data.
        """
        if isinstance(self.datasource, DatabaseSource):
            if not self.datasource.query:
                raise ValueError("No query or table name specified.")

            query = self._resolve_data_splitter(data_splitter).get_split_query(
                self.datasource, split
            )
            with self.datasource.con.connect() as con:
                result = con.execute(text(query))
                for partition in result.partitions(
                    self.datasource.database_partition_size
                ):
                    yield pd.DataFrame(partition, columns=list(result.keys()))
        else:
            raise ValueError(
                "Iterating over in-memory data is currently not supported."
            )
