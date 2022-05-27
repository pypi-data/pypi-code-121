""" Module contains data-transfer-object for finetune datasets. """
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional

from docarray import DocumentArray

from now.finetuning.settings import FinetuneSettings

_SEED = 42
MAX_VAL_SET_SIZE = 5000


@dataclass
class FinetuneDataset:
    index: DocumentArray

    train: Optional[DocumentArray] = None
    val: Optional[DocumentArray] = None
    val_query: Optional[DocumentArray] = None
    val_index: Optional[DocumentArray] = None

    def as_dict(self) -> Dict[str, Optional[DocumentArray]]:
        return {
            'train': self.train,
            'val': self.val,
            'val_query': self.val_query,
            'val_index': self.val_index,
        }


def build_finetuning_dataset(
    dataset: DocumentArray, finetune_setting: FinetuneSettings
) -> FinetuneDataset:
    ds = FinetuneDataset(index=dataset)

    split_index = max(
        int(len(dataset) * finetune_setting.train_val_split_ration),
        len(dataset) - MAX_VAL_SET_SIZE,
    )

    ds.train = deepcopy(dataset[:split_index])
    ds.val = deepcopy(dataset[split_index:])

    ds.val_index = deepcopy(ds.val)
    ds.val_query = deepcopy(
        ds.val_index.sample(k=finetune_setting.num_val_queries, seed=_SEED)
    )

    return ds
