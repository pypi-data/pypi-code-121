from typing import Any, Callable, List

import numpy as np
import pandas as pd
from pydantic import BaseModel
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


class CustomTransformer(BaseEstimator, TransformerMixin, BaseModel):
    # TODO: implement a `remainder` param - drop or passthrough
    # TODO:fix type, isinstance(TransformerMixin, StandardScaler) is False!
    tfmr: Any
    columns: List[Any] = None

    class Config:
        arbitrary_types_allowed = True

    def __repr__(self):
        return str(self.tfmr)

    def fit(self, X, y=None):
        assert isinstance(X, pd.DataFrame)
        x1 = X[self.columns]
        self.tfmr = self.tfmr.fit(x1)
        return self

    def transform(self, X, y=None):
        assert isinstance(X, pd.DataFrame)
        if self.columns is not None:
            for col in self.columns:
                assert col in X.columns

        x1 = X[self.columns]
        idx = x1.index
        x2 = X.drop(columns=self.columns)
        if self.tfmr is None:
            return X
        x1_prime = self.tfmr.transform(x1)
        try:
            columns = self.tfmr[0].get_feature_names()
        except AttributeError:
            columns = self.columns
        x1 = pd.DataFrame(x1_prime, index=idx, columns=columns)
        out = pd.concat([x1, x2], axis=1)
        return out[sorted(out.columns.tolist())]

    def get_feature_names(self):
        return self.columns


class CustomFuncTransformer(BaseEstimator, TransformerMixin, BaseModel):
    func: Callable
    columns: List[Any] = None

    def __repr__(self):
        return self.func.__name__

    def fit(self, X, y=None):
        assert isinstance(X, pd.DataFrame)
        return self

    def transform(self, X):
        assert isinstance(X, pd.DataFrame)
        if self.func is None:
            raise ValueError(1)
            return X
        if self.columns is not None:
            for col in self.columns:
                assert col in X.columns
                # try:
                #     assert col in X.columns
                # except Exception as e:
                #     print(f"col {col} not found in {X.columns}")
                #     print(e)

        x1 = X[self.columns]
        df = self.func(x1)
        df.columns = [
            self.func.__name__
        ]  # TODO: generate a sequence of names for >1 cols
        out = pd.concat([df, X], axis=1)
        print(f"########################### out.columns: {out.columns}")
        print(f"########################### len(out.columns): {len(out.columns)}")
        print(f"########################### out.shape: {out.shape}")
        self.columns = sorted(out.columns.tolist())
        print(self.columns, len(self.columns))
        return out[self.columns]

    def get_feature_names(self):
        return self.columns


if __name__ == "__main__":
    df = pd.DataFrame(
        {
            "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "b": [
                "hello",
                "world",
                "hello world",
                "a",
                "a b c",
                "a",
                "b",
                "c",
                "d",
                "e",
            ],
            "c": [True, False, False, True, False, False, False, True, False, False],
            "d": [1, 2, 3, None, np.nan, None, 7, 8, 9, 10],
            "e": ["", None, "", None, "a b c", "a", "b", "c", "d", "e"],
        }
    )

    def sqrt(x):
        return x ** 0.5

    pipeline = Pipeline(
        [
            ("scaler1", CustomFuncTransformer(func=sqrt, columns=["a"])),
            ("scaler2", CustomFuncTransformer(func=sqrt, columns=["d"])),
            ("scaler3", CustomFuncTransformer(func=sqrt, columns=["c"])),
            ("scaler4", CustomFuncTransformer(func=sqrt, columns=["a"])),
            ("scaler5", CustomFuncTransformer(func=sqrt, columns=["d"])),
            ("scaler6", CustomTransformer(tfmr=StandardScaler(), columns=["a"])),
        ]
    )
    transformed = pipeline.fit_transform(df)
    print(transformed)
