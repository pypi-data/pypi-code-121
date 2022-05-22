from dataclasses import dataclass

import numpy as np

from ..base import BaseTransformer


@dataclass
class MeanCompressor(BaseTransformer):
    """指定幅ごとに平均を取ることで配列サイズを削減する。

    Attributes
    ----------
    width : int
        平均を取るときの幅

    Examples
    --------
    `MeanCompressor`は時系列データのデータサイズを削減したい時に使用できる。

    >>> from magnifier.transformer.compressing import MeanCompressor
    >>> X = np.arange(24).reshape(2, 12)
    >>> X
    array([[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11],
        [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]])
    >>> MeanCompressor(width=3).transform(X)
    array([[ 1.,  4.,  7., 10.],
        [13., 16., 19., 22.]])
    >>> MeanCompressor(width=2).transform(X)
    array([[ 0.5,  2.5,  4.5,  6.5,  8.5, 10.5],
        [12.5, 14.5, 16.5, 18.5, 20.5, 22.5]])
    """

    width: int = 1

    def __post_init__(self) -> None:
        if self.width < 1:
            raise ValueError(f"self.width must be >= 1, but given: {self.width}.")

    def transform(self, X: np.ndarray) -> np.ndarray:
        """指定幅ごとに平均を取る。

        Parameters
        ----------
        X : np.ndarray (n_samples, sample_width)
            サイズ削減前配列

        Returns
        -------
        np.ndarray (n_samples, sample_width // self.width)
            サイズ削減後配列
        """
        self._check_X(X)

        return X.reshape(X.shape[0], X.shape[1] // self.width, self.width).mean(axis=2)

    def _check_X(self, X: np.ndarray) -> None:
        if not isinstance(X, np.ndarray):
            raise TypeError(f"Type of X must be np.ndarray, but given: {type(X)}")
        if X.ndim != 2:
            raise ValueError(
                f"Number of dimensions of X must be 2, but given: {X.shape}."
            )
        if X.shape[1] % self.width != 0:
            raise ValueError(
                f"X.shape[1] must be divisible by {self.width}, but given: {X.shape}."
            )
