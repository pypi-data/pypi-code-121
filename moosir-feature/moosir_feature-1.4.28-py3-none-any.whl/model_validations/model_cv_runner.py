import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_predict
from .model_validator import CustomTsCv

def predict_on_cv(model,
                  features: pd.DataFrame,
                  targets: pd.DataFrame,
                  cv: CustomTsCv) -> pd.DataFrame:
    """
      - it is to fit and predict the model on all cv test section

      - input cv needs to make all datapoint one time and only one time as a test
        - otherwise exception: "cross_val_predict only works for partitions TimeSeriesSplit"

      - returns
        - predictions for all targets index/rows
        index  pred_<target_column_name>
        ----- --------------------------
    """
    assert len(features) == len(targets), "features and targets not the same size"
    assert len(targets.columns) == 1, "targets with multiple columns not supported"

    assert cv.train_shuffle_block_size is None, "predict results distorted when shuffle indexes on split"
    result = cross_val_predict(model, features, targets, cv=cv)

    predictions = targets.copy()
    predictions[predictions.columns[0]] = result
    predictions.columns = [f"pred_{c}" for c in predictions.columns]

    return predictions