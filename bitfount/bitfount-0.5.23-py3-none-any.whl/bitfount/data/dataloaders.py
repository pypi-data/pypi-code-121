"""Classes concerning data loading and dataloaders."""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Tuple, Union

import pandas as pd

if TYPE_CHECKING:
    from bitfount.data.datasets import _BaseBitfountDataset
    from bitfount.data.types import _SingleOrMulti


class _BitfountDataLoader:
    """An backend-agnostic data loader."""

    def __init__(self, dataset: _BaseBitfountDataset, batch_size: Optional[int] = None):
        self.dataset = dataset
        self.batch_size = batch_size

    def __len__(self) -> int:
        """Number of batches or number of elements if batch size is None."""
        if not self.batch_size:
            return len(self.dataset)
        return math.ceil(len(self.dataset) / self.batch_size)

    def __iter__(self) -> Iterator[List[_SingleOrMulti[Any]]]:
        """This should be implemented to allow batch by batch loading.

        Currently there are no backend-agnostic models that can operate on iterable
        datasets so it has not been implemented.

        Returns:
            An iterator over batches of x and y numpy arrays.
        """
        raise NotImplementedError

    def get_x_dataframe(
        self,
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
        """Gets the x-dataframe of the data i.e. features.

        For models incompatible with the __iter__ approach.
        """
        tabular, image, support_cols = self.dataset.x_var
        if tabular.size and image.size:
            tab_cols = [
                col
                for col in self.dataset.x_columns
                if col not in self.dataset.image_columns
            ]
            tab_df = pd.DataFrame(data=tabular, columns=tab_cols)
            tab_df[self.dataset.embedded_col_names] = tab_df[
                self.dataset.embedded_col_names
            ].astype("int64")
            img_df = pd.DataFrame(data=image, columns=self.dataset.image_columns)
            return tab_df, img_df
        elif image.size:
            img_df = pd.DataFrame(data=image, columns=self.dataset.image_columns)
            return img_df
        elif tabular.size:
            columns = self.dataset.x_columns
            tab_df = pd.DataFrame(data=tabular, columns=columns)
            tab_df[self.dataset.embedded_col_names] = tab_df[
                self.dataset.embedded_col_names
            ].astype("int64")
            return tab_df
        else:
            raise ValueError("No tabular or image data to train with.")

    def get_y_dataframe(self) -> pd.DataFrame:
        """Gets the y-dataframe of the data i.e. target.

        For models incompatible with the __iter__ approach.
        """
        columns = self.dataset.y_columns
        data = self.dataset.y_var
        dataframe = pd.DataFrame(data=data, columns=columns)
        return dataframe
