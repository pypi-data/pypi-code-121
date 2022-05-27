import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted, check_array
from scipy.signal import convolve2d
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import statsmodels.tsa.api as tsa
from scipy.stats import dweibull


# Define the Adstock Class as a custom Transformer
class ExponentialCarryover(BaseEstimator, TransformerMixin):
    def __init__(self, strength=0.5, length=1):
        self.strength = strength
        self.length = length

    def fit(self, X, y=None):
        X = check_array(X)
        self._check_n_features(X, reset=True)
        self.sliding_window_ = (
                self.strength ** np.arange(self.length + 1)
        ).reshape(-1, 1)

        return self

    def transform(self, X: np.ndarray):
        check_is_fitted(self)
        X = check_array(X)
        self._check_n_features(X, reset=False)
        convolution = convolve2d(X, self.sliding_window_)

        if self.length > 0:
            convolution = convolution[: -self.length]

        return convolution


# Define the Saturation Class as a custom Transformer
class ExponentialSaturation:
    def __init__(self, a=1.):
        self.a = a

    def transform(self, X):
        return 1 - np.exp(-self.a * X)


class ExponentialSaturation(BaseEstimator, TransformerMixin):
    def __init__(self, a=1.):
        self.a = a

    def fit(self, X, y=None):
        X = check_array(X)
        self._check_n_features(X, reset=True)  # from BaseEstimator

        return self

    def transform(self, X):
        check_is_fitted(self)
        X = check_array(X)
        self._check_n_features(X, reset=False)  # from BaseEstimator

        return 1 - np.exp(-self.a * X)


def trasformation(media, organic):
    trasf = []
    for x in media:
        trasf.append(
            (x, Pipeline([
                ('carryover', ExponentialCarryover()),
                ('saturation', ExponentialSaturation())
            ]), [x]),
        )
    for x in organic:
        trasf.append(
            (x, Pipeline([
                ('inputer', SimpleImputer())
            ]), [x]),
        )
    return trasf


def create_model(medias, organic, model):
    trasf = ColumnTransformer(
        trasformation(medias, organic)
    )

    steps = [
        ('trasformation', trasf),
        ('regression', model)
    ]
    pipeline = Pipeline(steps)

    return pipeline


# Function to return Adstocked variables
def adstock_geometric_old(x, theta):
    return tsa.filters.recursive_filter(x, theta)


# Function to return Adstock weibull pdf variables
def adstock_weibull_pdf(x, scale, shape):
    return (shape / scale) * (x / scale) ** (shape - 1) * np.exp(-(x / scale) ** shape)


# Function to return Adstock weibull cdf variables
def adstock_weibull_cdf(x, scale, shape):
    return 1 - np.exp(-(x / scale) ** shape)


# Function to return Saturated variables
def saturation(x, beta):
    return x ** beta


def saturation_robyn(x, coeff, alpha, gamma):
    return coeff * (x ** alpha / (x ** alpha + gamma ** alpha))


def saturation_hill(x, alpha, gamma):
    if isinstance(x, list):
        gammaTrans = round(np.percentile(np.linspace(start=min(x), stop=max(x), num=100), 100 * gamma), 4)
        x_scurve = x ** alpha / (x ** alpha + gammaTrans ** alpha)
    else:
        x_scurve = x ** alpha / (x ** alpha + gamma ** alpha)
    return x_scurve


def adstock_geometric(x, theta):
    x_decayed = np.concatenate(([x[1]], np.repeat(0, len(x) - 1)))
    for xi in range(1, len(x_decayed)):
        x_decayed[xi] = x[xi] + theta * x_decayed[xi - 1]

    thetaVecCum = []
    thetaVecCum.insert(0, theta)
    for t in range(1, len(x)):
        thetaVecCum.insert(t, thetaVecCum[t - 1] * theta)

    all = {'x': x, 'x_decayed': x_decayed, 'thetaVecCum': thetaVecCum}

    return pd.Series(x_decayed)


def adstock_weibull(x, scale, shape, weibull_type="pdf"):
    windlen = len(x)
    x_bin = [*range(1, windlen + 1)]
    scaleTrans = round(np.percentile(x_bin, 100 * scale), 0)

    if weibull_type == 'pdf':

        def normalize(x):
            decimal_x = x.iloc[:, 0].apply(float)

            if (max(decimal_x) - min(decimal_x)) == 0:
                return np.concatenate(([1], np.repeat(0, windlen - 1)))
            else:
                return (decimal_x - min(decimal_x)) / (max(decimal_x) - min(decimal_x))

        thetaVecCum = normalize(adstock_weibull_pdf(pd.DataFrame(x_bin), scaleTrans, shape))
        thetaVecCumArray = np.array(thetaVecCum.values.tolist())

    # elif weibull_type == 'cdf':
    # thetaVec = np.concatenate((1, 1 - pweibull(head(x_bin, -1), shape = shape, scale = scaleTrans)) # plot(thetaVec)
    # thetaVecCum <- cumprod(thetaVec) # plot(thetaVecCum)

    def x_decayed(x_val, x_pos):
        x_vec = np.concatenate((np.repeat(0, x_pos - 1), np.repeat(x_val, windlen - x_pos + 1)))
        thetaVecCumLag = np.roll(thetaVecCumArray, x_pos - 1)
        # shift(thetaVecCum, x_pos - 1, fill = 0)
        x_prod = x_vec * thetaVecCumLag
        thetaVecCumLag[x_pos - 1] = 0
        return x_prod

    x_decay = np.sum(list(map(x_decayed, x, x_bin)), axis=1)

    all = {'x': np.array(x), 'x_decayed': np.array(x_decay[::-1]), 'thetaVecCum': thetaVecCum.values.tolist()}

    return pd.Series(x_decay[::-1])
