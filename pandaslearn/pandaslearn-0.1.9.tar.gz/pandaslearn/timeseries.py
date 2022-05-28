from typing import List

import numpy as np  # type:ignore
import pandas as pd  # type:ignore

# import pandas_ta as ta  # type:ignore
from pydantic import BaseModel
from tqdm import tqdm


class OHLCTSFeatures(BaseModel):
    df: pd.DataFrame = None

    class Config:
        arbitrary_types_allowed = True

    # moving average
    def ma(self, *, feature: pd.Series, n: int):
        return feature.rolling(n, win_type="triang", min_periods=n).mean()

    # exponentially weighted moving average
    def ema(self, *, feature: pd.Series, n: int):
        return feature.ewm(alpha=(1 / n), min_periods=n).mean()

    # price momentum
    def mom(self, *, feature: pd.Series, n: int):
        return feature.diff(n)

    # rate of change
    def roc(self, *, feature: pd.Series, n: int):
        M = feature.diff(n - 1)
        N = feature.shift(n - 1)
        return (M / N) * 100

    # relative strength index
    def rsi(self, *, feature: pd.Series, n: int):
        delta = feature.diff().dropna()
        u = delta * 0
        d = u.copy()
        u[delta > 0] = delta[delta > 0]
        d[delta < 0] = -delta[delta < 0]
        u[u.index[n - 1]] = np.mean(u[:n])  # first value is sum of avg gains
        u = u.drop(u.index[: (n - 1)])
        d[d.index[n - 1]] = np.mean(d[:n])  # first value is sum of avg losses
        d = d.drop(d.index[: (n - 1)])
        rs = (
            u.ewm(com=n - 1, adjust=False).mean()
            / d.ewm(com=n - 1, adjust=False).mean()
        )
        return 100 - 100 / (1 + rs)

    # stochastic oscillators slow & fast
    def sto(self, *, close, low, high, n, id_):
        stok = (
            (close - low.rolling(n).min())
            / (high.rolling(n).max() - low.rolling(n).min())
        ) * 100
        if id_ == 0:
            return stok
        else:
            return stok.rolling(3).mean()


class FeatureStrategy(BaseModel):
    data: pd.DataFrame = None

    class Config:
        arbitrary_types_allowed = True

    def discretize(self, *, colname: str, ret_labels: bool = False):
        large_number = 1000000
        if ret_labels:
            labels = [
                "bearish",
                "neutral_bearish",
                "neutral",
                "neutral_bullish",
                "bullish",
            ]
        else:
            labels = [-2, -1, 0, 1, 2]
        colname_stats = self.data.loc[:, colname].describe()
        self.data.loc[:, colname + "_discrete"] = pd.cut(
            x=self.data.loc[:, colname],
            bins=[
                colname_stats["min"] - large_number,
                colname_stats["mean"] - (7 / 5) * colname_stats["std"],
                colname_stats["mean"] - (2 / 3) * colname_stats["std"],
                colname_stats["mean"] + (2 / 3) * colname_stats["std"],
                colname_stats["mean"] + (7 / 5) * colname_stats["std"],
                colname_stats["max"] + large_number,
            ],
            labels=labels,
        )
        return self

    def build_sma_signal(self, start: int, end: int):
        start_label = "sma" + str(start)
        end_label = "sma" + str(end)

        start_indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=start)
        end_indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=end)

        self.data.loc[:, start_label] = (
            self.data.loc[:, "close"]
            .rolling(
                window=start_indexer,
                min_periods=start - 1,
            )
            .mean()
        )
        self.data.loc[:, end_label] = (
            self.data.loc[:, "close"]
            .rolling(
                window=end_indexer,
                min_periods=end - 1,
            )
            .mean()
        )

        colname = start_label + end_label + "_diff"
        self.data.loc[:, colname] = (
            self.data.loc[:, start_label] - self.data.loc[:, end_label]
        )
        self.discretize(colname=colname)

        return self

    def build_targets(self):
        # TODO: Sanitize OHLCVA
        self.data = self.data.iloc[30:, :]  # embargo
        # self.data.loc[:, "trend"] = np.sign(self.data.close.shift(-1) - self.data.close)
        self.data.loc[:, "return"] = (
            self.data.close.shift(-1) - self.data.close
        ) / self.data.close
        self.discretize(colname="return")

        self.data.loc[:, "past_return"] = self.data.loc[:, "return"].shift(1)
        self.data.loc[:, "spread"] = (self.data.close - self.data.open) / self.data.open
        self.data.loc[:, "volume_growth"] = (
            self.data.volume.shift(-1) - self.data.volume
        ) / self.data.volume
        self.data.loc[:, "upness"] = (self.data.high - self.data.open) / self.data.open
        self.data.loc[:, "downness"] = (self.data.open - self.data.low) / self.data.open

        features = ["past_return", "spread", "volume_growth", "upness", "downness"]

        OHLCTSFeatures()
        for feature in features:
            for i in [3, 7, 15, 30]:
                for trfm in ["ma", "ema", "roc", "rsi"]:
                    # feature_pdseries = self.data.loc[:, feature]
                    self.data.loc[:, f"{feature}_{trfm}_{i}"] = eval(
                        f"tsfeatures.{trfm}(feature=feature_pdseries, n={i})"
                    )
        # self.build_sma_signal(3, 10)
        # self.build_sma_signal(5, 20)

        self.data.drop(["return"], axis=1, inplace=True)

        offset = 30
        self.data = self.data.iloc[offset:, :]
        self.data = self.data.replace([np.inf, -np.inf], np.nan)
        self.data = self.data.fillna(method="ffill")

        return self

    def build_targets_inference(self):
        self.data.loc[:, "return"] = (
            self.data.close.shift(-1) - self.data.close
        ) / self.data.close

        self.discretize(colname="return")

        self.data.loc[:, "past_return"] = self.data.loc[:, "return"].shift(1)
        self.data.loc[:, "spread"] = (self.data.close - self.data.open) / self.data.open
        self.data.loc[:, "volume_growth"] = (
            self.data.volume.shift(-1) - self.data.volume
        ) / self.data.volume
        self.data.loc[:, "upness"] = (self.data.high - self.data.open) / self.data.open
        self.data.loc[:, "downness"] = (self.data.open - self.data.low) / self.data.open

        features = ["past_return", "spread", "volume_growth", "upness", "downness"]

        OHLCTSFeatures()
        for feature in features:
            for i in [3, 7, 15, 30]:
                for trfm in ["ma", "ema", "roc", "rsi"]:
                    # feature_pdseries = self.data.loc[:, feature]
                    self.data.loc[:, f"{feature}_{trfm}_{i}"] = eval(
                        f"tsfeatures.{trfm}(feature=feature_pdseries, n={i})"
                    )

        self.data.drop(["return", "return_discrete"], axis=1, inplace=True)

        self.data = self.data.replace([np.inf, -np.inf], np.nan)
        self.data = self.data.fillna(method="ffill")

        return self

    def drop(self, cols: List[str]):
        self.data = self.data.drop(cols, axis=1)
        return self

    def only_ohlcv(self):
        self.data = self.data.loc[
            :, ["timestamp", "open", "high", "low", "close", "volume"]
        ]
        return self

    def only_ohlcv_inference(self):
        self.data = self.data.loc[:, ["open", "high", "low", "close", "volume"]]
        return self

    def only_cv(self):
        self.data = self.data.loc[:, ["timestamp", "close", "volume"]]
        return self


if __name__ == "__main__":
    currs = ["XRP", "ETH", "BTC", "BCH", "LTC", "BNB", "DOT", "LINK", "ADA", "USDT"]
    for cur in tqdm(currs):
        train = pd.read_csv(f"data/crypto/csv/{cur}_hourly.csv")
        train = FeatureStrategy(data=train).only_ohlcv().build_targets().data
        train.to_csv(f"data/crypto/fe/{cur}.csv", index=False)
