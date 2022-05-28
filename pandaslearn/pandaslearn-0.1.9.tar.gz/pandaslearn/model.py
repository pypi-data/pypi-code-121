from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel

from .dataset import Dataset

# TODO: extend Model to an sklearn transformer


class Model(BaseModel):
    model: Optional[Any]
    model_config: Optional[Dict[str, Any]]
    fit_config: Optional[Dict[str, Any]]
    oof: Optional[Any]  # np.array
    oof_target: Optional[Any]
    preds: Optional[Any]  # np.array
    importances: Optional[pd.DataFrame]
    log_cache: List[str] = []
    logger: Any = None

    class Config:
        arbitrary_types_allowed = True

    def add_to_log(self, message: str):
        self.log_cache += [message]

    def log(self, messages: Union[str, List[str]]):
        if isinstance(messages, str):
            messages = [messages]
        if self.logger is None:
            fns = [print, self.add_to_log]
        else:
            fns = [self.logger.logger.info]
        [[fn(message) for fn in fns] for message in messages]

    def prepare(self, *, dataset: Dataset):
        """Initialises oof, oof_target, preds, importances to shape [n_samples] (all set to 0). Also initialises model using model_config"""
        self.oof = np.zeros(dataset.data.train.shape[0])
        self.oof_target = np.zeros(dataset.data.train.shape[0])
        self.preds = np.zeros(dataset.data.test.shape[0])
        self.importances = pd.DataFrame()
        self.model = self.model(**self.model_config)
        self.log(
            messages=[
                "Initialized oof, preds, importances and model",
                f"oof shape:{dataset.data.train.shape[0]}",
                f"oof_target shape:{dataset.data.train.shape[0]}",
                f"preds shape:{dataset.data.test.shape[0]}",
                f"importances shape:{self.importances.shape}",
                f"model config: {self.model_config}",
            ]
        )
        return self
