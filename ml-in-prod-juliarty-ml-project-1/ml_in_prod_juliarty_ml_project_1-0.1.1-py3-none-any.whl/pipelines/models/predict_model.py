from typing import Union

import pandas as pd
import numpy as np

from .train_model import SklearnClassifierModel


def predict(
    model: SklearnClassifierModel, features: Union[pd.DataFrame, np.ndarray]
) -> Union[pd.Series, np.ndarray]:
    return model.predict(features)
