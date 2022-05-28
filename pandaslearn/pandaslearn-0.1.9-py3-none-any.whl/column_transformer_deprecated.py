from sklearn.base import BaseEstimator, TransformerMixin
from typing import Callable, List, Any, Union
import pandas as pd
from pydantic import BaseModel
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures


class CustomTransformer(BaseEstimator, TransformerMixin, BaseModel):
    # TODO: implement a `remainder` param - drop or passthrough
    # TODO:fix type, isinstance(TransformerMixin, StandardScaler) is False!
    tfmr: Any
    columns: List[Any]
    feature_format: str = "df"  # "df" or "np"

    class Config:
        arbitrary_types_allowed = True

    def __repr__(self):
        return str(self.tfmr)

    def fit(self, X, y=None):
        x1 = X[self.columns]

        if self.feature_format == "np":
            print(f"{x1.iloc[:,0]}")
            x1 = pd.Series(x1.iloc[:, 0]).ravel()
            # "np" format required only when features need to be 1-d
            print(f"x1{x1}")
            print(f"type(x1){type(x1)}")
            print(f"x.shape after: {x1.shape}")

        self.tfmr = self.tfmr.fit(x1)
        return self

    def transform(self, X, y=None):
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
        return out

    def get_feature_names(self):
        return self.columns


class CustomFuncTransformer(BaseEstimator, TransformerMixin, BaseModel):
    func: Callable
    columns: List[str]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        assert isinstance(X, pd.DataFrame)
        x1 = X[self.columns]
        x2 = X.drop(columns=self.columns)
        if self.func is None:
            return X
        return pd.concat([self.func(x1), x2], axis=1)

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
        return x**0.5

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
