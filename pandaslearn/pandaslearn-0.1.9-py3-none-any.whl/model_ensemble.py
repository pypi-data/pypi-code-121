from pathlib import Path
from typing import List, Optional, Union

import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel
from scipy import stats

from .model import Model
from .trainer import Trainer


class ModelEnsemble(BaseModel):
    paths: Optional[List[Union[str, Path]]]
    models: Optional[List[Model]]
    predictions: Optional[List[pd.DataFrame]]

    class Config:
        arbitrary_types_allowed = True

    def load_models(self, *, paths: Optional[List[Union[str, Path]]]):
        print("####################### single models vs pipelines vs sweepers!")
        self.models = []
        if self.paths is None:
            self.paths = Path(paths)
        for path in self.paths:
            path = str(path)
            self.models += [joblib.load(path)]
        return self

    def load_predictions(
        self, *, paths: Optional[List[Union[str, Path]]], index_col: str
    ):
        self.predictions = []
        if self.paths is None:
            self.paths = Path(paths)
        self.predictions = [
            pd.read_csv(str(path), index_col=index_col) for path in self.paths
        ]
        # TODO: check colnames match
        # TODO: check rowcounts match
        return self

    def load_folder(self, *, path: Union[str, Path], index_col: str):
        self.predictions = []
        path = Path(path)
        self.paths = list(path.glob("*.csv"))
        self.predictions = [
            pd.read_csv(str(path), index_col=index_col) for path in self.paths
        ]
        # TODO: check colnames match
        # TODO: check rowcounts match
        return self

    @property
    def all_preds(self):
        df = pd.concat(self.predictions, axis=1)
        df.columns = [Path(path).stem for path in self.paths]
        return df

    @property
    def mean_preds(self):
        # TODO: terribly inefficient
        preds = self.all_preds.values
        idx = self.all_preds.index
        mean_preds: np.array = np.mean(preds, axis=1)
        return pd.DataFrame({"id": idx, "claim": mean_preds})

    @property
    def rankmean_preds(self):
        # TODO: terribly inefficient
        preds = self.all_preds.values
        idx = self.all_preds.index
        ranked = []

        for i in range(preds.shape[1]):
            rank_data = stats.rankdata(preds[:, i])
            ranked.append(rank_data)
        ranked = np.column_stack(ranked)
        return pd.DataFrame({"id": idx, "claim": np.mean(ranked, axis=1)})
