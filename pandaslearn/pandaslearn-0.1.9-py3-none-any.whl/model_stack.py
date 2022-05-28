import time
from typing import Any, List

import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, FilePath
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from .model import Model


class ModelStack(BaseModel):
    paths: List[FilePath]
    submission: Any
    model_list: List[Model] = []

    class Config:
        arbitrary_types_allowed = True

    def load_models_from_disk(self):
        for path in self.paths:
            t = joblib.load(str(path))
            self.model_list += [t.model]
            self.submission = t.dataset.data.submission

        return self

    def __len__(self):
        return len(self.model_list)

    def stack(self):
        skf = StratifiedKFold(n_splits=5)
        test_pred, total_auc = 0, 0

        oof_preds = [np.expand_dims(x.oof, axis=1) for x in self.model_list]
        oof_preds = np.concatenate(oof_preds, axis=1)

        test_preds = [np.expand_dims(x.preds, axis=1) for x in self.model_list]
        test_preds = np.concatenate(test_preds, axis=1)

        oof_targets = np.expand_dims(self.model_list[0].oof_target, axis=1)

        for fold, (trn_idx, val_idx) in enumerate(
            skf.split(
                X=oof_preds,
                y=oof_targets,
            )
        ):
            start = time.time()

            X_train, y_train = oof_preds[trn_idx], oof_targets[trn_idx]
            X_valid, y_valid = oof_preds[val_idx], oof_targets[val_idx]

            lr = LogisticRegression(
                n_jobs=-1, random_state=2021, C=1000, max_iter=10000
            )
            lr.fit(X_train, y_train)

            valid_pred = lr.predict_proba(X_valid)[:, 1]
            test_pred += lr.predict_proba(test_preds)[:, 1]
            auc = roc_auc_score(y_valid, valid_pred)
            total_auc += auc / 5

            elapsed = time.time() - start
            print(f"Fold {fold} - AUC: {auc:.6f}, Elapsed Time: {elapsed:.2f}sec\n")

        print(f"Stacking OOF roc = {total_auc}")
        self.submission["claim"] = test_pred
        return self.submission
