"""Useful transformers for working with metatypes."""
import datetime
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder

from ..base.types import Metatype, get_delimiter, is_delimiter_metatype, is_target_metatype, is_classification_metatype

def to_float(df):
    return df.astype(float)

def to_category(df):
    return df.astype('category')

def to_datetime(df):
    return df.apply(pd.to_datetime)

def from_timestamp(df):
    def float_to_timestamp(x):
        if pd.isnull(x):
            return x
        return datetime.datetime.fromtimestamp(x)
    return df.astype(float).applymap(float_to_timestamp)

def to_text(df):
    return df.astype(str).mask(pd.isnull(df))

def from_delim(df, delim):
    def split_delim(x):
        return [y.strip() for y in x.split(delim)]
    return df.astype(str).applymap(split_delim).mask(pd.isnull(df))

def delim_pipe(df):
    return from_delim(df, '|')

def delim_semicolon(df):
    return from_delim(df, ';')

class FunctionTransformer(BaseEstimator, TransformerMixin):
    """
    Transformer that applies a function to X.

    Args:
        func: callable with a single argument that accepts X.

    Note:
        Annonymous functions, i.e lambdas, do not pickle and should be avoided.
    """
    def __init__(self, func):
        self.func = func

    def fit(self, X, y = None):
        return self

    def transform(self, X, y = None):
        """
        Applies function to X.

        Args:
            X: DataFrame or numpy array.
            y: optional.

        Returns:
            func(X).
        """
        return self.func(X)

class CategoricalListTransformer(BaseEstimator, TransformerMixin):
    """
    Converts a list to array with ones where a category is present and zeros if not.

    Args:
        null_as_zeros: missing values transformed to rows of zeros if True, nans otherwise.
    """
    def __init__(self, null_as_zeros = False):
        self.null_as_zeros = null_as_zeros

    def fit(self, X, y = None):
        """
        Fits transformer to X.

        Args:
            X: Series, DataFrame or numpy array.
            y: optional.

        Returns:
            self.
        """
        if isinstance(X, pd.Series):
            X = X.to_frame()

        if isinstance(X, pd.DataFrame):
            self.columns = X.columns
            X = X.to_numpy()

        if X.ndim == 1:
            X = np.expand_dims(X, 1)

        self.categories = []
        for i in range(X.shape[1]):
            uniques = set()
            for row in X[:,i]:
                if isinstance(row, list):
                    for x in row:
                        uniques.add(x)

            self.categories.append({x : i for i, x in enumerate(uniques)})
        return self

    def transform(self, X):
        """
        Applies function to X.

        Args:
            X: Series, DataFrame or numpy array.
            y: optional.

        Returns:
            numpy array.
        """
        if isinstance(X, pd.Series):
            X = X.to_frame()

        if isinstance(X, pd.DataFrame):
            if list(X.columns) != list(self.columns):
                raise ValueError('when transforming X, columns must be the same as fit') 
            X = X.to_numpy()

        if X.ndim == 1:
            X = np.expand_dims(X, 1)

        transforms = []
        for j, cat in enumerate(self.categories):
            data = np.zeros((X.shape[0], len(cat)))
            for i, row in enumerate(X[:,j]):
                if isinstance(row, list):
                    if row:
                        idx = [cat[x] for x in row if x in cat]
                        data[i,idx] = 1
                elif not self.null_as_zeros:
                    data[i,:] = np.nan
            transforms.append(data)

        return np.concatenate(transforms, axis=1) 

class BinaryTransformer(BaseEstimator, TransformerMixin):
    """Converts binary categoricals to bools."""
    def fit(self, X, y = None):
        """
        Fits transformer to X.

        Args:
            X: DataFrame.
            y: optional.

        Returns:
            self.
        """
        self.categories = dict()
        for col, s in X.items():
            cat = s.dropna().unique()
            if len(cat) != 2:
                raise ValueError('non-binary feature: %s' % col)
            self.categories[col] = sorted(list(cat))
        return self

    def transform(self, X):
        """
        Transforms binary categoricals to bool

        Args:
            X: DataFrame.

        Returns:
            DataFrame with object dtype where null values are preserved.
        """
        transforms = []
        for col, s in X.items():
            cat = self.categories[col]
            binary = s == cat[1]
            transforms.append(binary)
        return pd.concat(transforms, axis=1).mask(pd.isnull(X)).astype('O')

class ColumnTransformer(BaseEstimator, TransformerMixin):
    """ColumnTransformer specifically for DataFrame.

    Args:
        column_transformers: iterable of tuples - see sklearn ColumnTransformer. 

    Note:
        The ColumnTransformer from sklearn interprets integers as positional columns and not column names, and only strings are used to reference DataFrame columns by name. 
        Here, indexes references DataFrame column names in all cases.
    """
    def __init__(self, column_transformers):
        self.column_transformers = column_transformers

    def fit(self, X, y = None):
        """
        Fits transformer to X.

        Args:
            X: DataFrame.
            y: optional.

        Returns:
            self.
        """
        if not isinstance(X, pd.DataFrame):
            raise TypeError('X should be a DataFrame')

        for name, transformer, columns in self.column_transformers:
            transformer.fit(X[columns], y)

        return self

    def transform(self, X):
        """
        Applies transformers to columns

        Args:
            X: DataFrame.

        Returns:
            numpy array
        """
        if not isinstance(X, pd.DataFrame):
            raise TypeError('X should be a DataFrame')

        return np.concatenate([_expand_dim(np.array(transformer.transform(X[columns]))) for name, transformer, columns in self.column_transformers], axis=1)


class MetatypeTransformer(BaseEstimator, TransformerMixin):
    """
    Transformer that converts Metatypes.

    Args:
        X_metatypes: list of Metatypes.
        valid_metatypes: set of Metatypes (optional).
        binary_as_categorical: convert features with two categories to categoricals.

    Note:
        This transformer is intended for input data and it is recommended to use it as the first step in a pipeline. 
    """

    def __init__(self, X_metatypes, valid_metatypes = None, binary_as_categorical = False):
        _check_metatypes(X_metatypes)
        self.X_metatypes = X_metatypes

        if valid_metatypes is not None:
            _check_metatypes(valid_metatypes)
        self.valid_metatypes = valid_metatypes

        self.binary_as_categorical = binary_as_categorical
        self.transformers = []
        self.columns = []

    def _is_valid_metatype(self, metatype):
        return self.valid_metatypes is None or metatype in self.valid_metatypes

    def fit(self, X, y = None):
        """
        Fits transformer to X.

        Args:
            X: DataFrame with same number of columns as X_metatypes.
            y: optional.

        Returns:
            self.
        """
        if not X.shape[1] == len(self.X_metatypes):
            raise ValueError('number of columns must equal length of metatypes')

        def get_transformer(metatype):
            transformers = dict()
            transformers[Metatype.NUMERICAL] = FunctionTransformer(to_float)

            if self.binary_as_categorical:
                transformers[Metatype.BINARY] = FunctionTransformer(to_category)
            else:
                transformers[Metatype.BINARY] = BinaryTransformer()

            transformers[Metatype.CATEGORICAL] = FunctionTransformer(to_category)
            transformers[Metatype.DATETIME] = FunctionTransformer(to_datetime)
            transformers[Metatype.TIMESTAMP] = FunctionTransformer(from_timestamp)
            transformers[Metatype.TEXT] = FunctionTransformer(to_text)
            transformers[Metatype.DELIM_PIPE] = FunctionTransformer(delim_pipe)
            transformers[Metatype.DELIM_SEMICOLON] = FunctionTransformer(delim_semicolon)
            return transformers.get(metatype)

        valid_metatypes = set()
        self.transformers = []
        for metatype, columns in group_metatypes(X, self.X_metatypes).items():
            if self._is_valid_metatype(metatype):
                transformer = get_transformer(metatype)
                if transformer:
                    self.transformers.append((transformer.fit(X[columns]), columns))
                    valid_metatypes.add(metatype)

        self.columns = [col for col, metatype in zip(X, self.X_metatypes) if metatype in valid_metatypes]
        return self

    def transform(self, X):
        """
        Transforms binary categoricals to bool.

        Args:
            X: DataFrame with same number of columns as metatypes.

        Returns:
            DataFrame.

        Note:
            Metatypes 'datetime' and 'timestamp' are both converted to datetime objects, and delimiter metatypes are converted to lists.
        """
        output = pd.concat([transformer.transform(X[columns]) for transformer, columns in self.transformers], axis=1)
        return output[self.columns]

    def transform_metatypes(self):
        """
        Transforms metatypes to output metatypes.

        Returns:
            List of Metatypes.
        """
        def transform_metatype(metatype):
            if metatype == Metatype.TIMESTAMP:
                return Metatype.DATETIME
            if is_delimiter_metatype(metatype):
                return Metatype.LIST
            if metatype == Metatype.BINARY and self.binary_as_categorical:
                return Metatype.CATEGORICAL
            return metatype

        return [transform_metatype(x) for x in self.X_metatypes if self._is_valid_metatype(x)]

class TargetTransformer(BaseEstimator, TransformerMixin):
    """
    Transformer that works for both numerical and categorical targets.

    Args:
        y_metatypes: list of metatype strings ('numerical', 'binary' or 'categorical').

    Note:
        This transformer is intended to be used for translation between underlying model and output of algo. 
    """

    @staticmethod
    def _label_transform(s, encoder):
        return encoder.transform(s)

    @staticmethod
    def _label_inverse_transform(s, encoder):
        return encoder.inverse_transform(s.ravel().astype(int))

    def __init__(self, y_metatypes):
        for metatype in y_metatypes:
            if not is_target_metatype(metatype):
                raise ValueError('invalid target metatype')
        self.y_metatypes = y_metatypes

    def fit(self, y):
        """
        Fits transformer to y.

        Args:
            y: DataFrame with same number of columns as y_metatypes.

        Returns:
            self.
        """
        if not isinstance(y, pd.DataFrame):
            raise TypeError('y must be a dataframe')
        if y.shape[1] != len(self.y_metatypes):
            raise ValueError('wrong number of columns')

        self.label_encoders = {col : (metatype, LabelEncoder()) for col, metatype in zip(y, self.y_metatypes) if is_classification_metatype(metatype, strict=True)}
        self.columns = y.columns

        for col, s in y.items():
            if col in self.label_encoders:
                metatype, le = self.label_encoders[col]
                cat = s.dropna().unique()
                if metatype == Metatype.BINARY and len(cat) != 2:
                    raise ValueError('binary feature must have 2 categories: %s' % col)
                le.fit(cat)

        return self

    def transform(self, y):
        """
        Label encodes 'binary' and 'categorical' features, while 'numerical' features are represented as floats. 

        Args:
            y: DataFrame with same number of columns as metatypes.

        Returns:
            DataFrame.
        """
        if not isinstance(y, pd.DataFrame):
            raise TypeError('y must be a dataframe')
        if y.shape[1] != len(self.y_metatypes):
            raise ValueError('wrong number of columns')

        processed = []
        for col, s in y.items():
            if col in self.label_encoders:
                le = self.label_encoders[col][1]
                processed.append(pd.Series(TargetTransformer._label_transform(s, le), dtype=int, name = col))
            else:
                processed.append(s.astype(float))

        return pd.concat(processed, axis=1)

    def inverse_transform(self, y, index = None):
        """
        Inverse transforms 'binary' and 'categorical' features, while 'numerical' features are represented as floats.

        Args:
            y: DataFrame or numpy array with y.shape[1] == len(y_metatypes).
            index: optional index for DataFrame.

        Returns:
            DataFrame.

        Note:
            The output of this transformation should be the output of the algo.
        """
        if isinstance(y, np.ndarray):
            y = pd.DataFrame(y, index = index, columns = self.columns)
        elif list(y.columns) != list(self.columns):
            raise ValueError('unexpected columns in y')

        processed = []
        for col, s in y.items():
            if col in self.label_encoders:
                le = self.label_encoders[col][1]
                processed.append(pd.Series(TargetTransformer._label_inverse_transform(s, le), index = y.index, dtype = 'category', name = col))
            else:
                processed.append(s.astype(float))

        return pd.concat(processed, axis=1)

    def classes(self):
        """
        Returns classes\_ for underlying LabelEncoders in sequence of the (classification-metatype) columns in y.

        Returns:
            List of (col, classes\_) tuples.

        Note:
            This is useful for constructing predict_proba and decision_function outputs, where classes\_ should be used as columns in a DataFrame.
        """
        return [(col, le[1].classes_) for col, le in self.label_encoders.items()]

def group_metatypes(columns, metatypes):
    """Group columns according to metatypes.

    Args:
        columns: iterable.
        metatypes: iterable with same length as columns.

    Returns: 
        dict with metatype keys and lists with columns as values
    """
    groups = dict()
    for col, metatype in zip(columns, metatypes):
        if metatype in groups:
            groups[metatype].append(col)
        else:
            groups[metatype] = [col]
    return groups

def _expand_dim(x):
    if x.ndim == 1:
        return np.expand_dims(x, 1)
    return x

def _check_metatypes(metatypes):
    """checks if metatypes are valid.

    Args:
        metatypes: iterable.
    
    Returns: None

    Raises: 
        ValueError
    """
    for x in metatypes:
        Metatype(x)