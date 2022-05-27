"""Classes for dealing with Transformation Processing."""
from __future__ import annotations

import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_numeric_dtype

from bitfount.data.types import DataSplit, SemanticType
from bitfount.transformations.base_transformation import (
    MultiColumnOutputTransformation,
    Transformation,
)
from bitfount.transformations.batch_operations import (
    BatchTimeOperation,
    ImageTransformation,
)
from bitfount.transformations.binary_operations import (
    AdditionTransformation,
    ComparisonTransformation,
    DivisionTransformation,
    MultiplicationTransformation,
    SubtractionTransformation,
)
from bitfount.transformations.dataset_operations import (
    CleanDataTransformation,
    NormalizeDataTransformation,
    ScalarAdditionDataTransformation,
    ScalarMultiplicationDataTransformation,
)
from bitfount.transformations.exceptions import (
    InvalidBatchTransformationError,
    MissingColumnReferenceError,
    NotColumnReferenceError,
    TransformationApplicationError,
)
from bitfount.transformations.references import _extract_col_ref
from bitfount.transformations.unary_operations import (
    InclusionTransformation,
    OneHotEncodingTransformation,
)

if TYPE_CHECKING:
    from bitfount.data.schema import TableSchema


logger = logging.getLogger(__name__)


class TransformationProcessor:
    """Processes Transformations on a given dataframe.

    Args:
        transformations: The list of transformations to apply.
        schema: The schema of the data to be transformed.
        col_refs: The set of columns referenced in those transformations.

    Attributes:
        transformations: The list of transformations to apply.
        schema: The schema of the data to be transformed.
        col_refs: The set of columns referenced in those transformations.

    ::: warning

    The Transformation processor does not add any of the newly created columns
    to the Schema. This must be done separately after processing the transformations.

    :::
    """

    def __init__(
        self,
        transformations: List[Transformation],
        schema: Optional[TableSchema] = None,
        col_refs: Optional[Set[str]] = None,
    ):
        self.transformations = transformations
        self.col_refs = set() if col_refs is None else col_refs

        self.schema = schema
        if self.schema is not None:
            self._schema_cont_cols = self.schema.get_feature_names(
                SemanticType.CONTINUOUS
            )
            self._schema_cat_cols = self.schema.get_feature_names(
                SemanticType.CATEGORICAL
            )
        else:
            self._schema_cont_cols = []
            self._schema_cat_cols = []

        self._operators: Dict[Type[Transformation], Callable] = {
            AdditionTransformation: self._do_addition,
            CleanDataTransformation: self._do_clean_data,
            ComparisonTransformation: self._do_comparison,
            DivisionTransformation: self._do_division,
            InclusionTransformation: self._do_inclusion,
            MultiplicationTransformation: self._do_multiplication,
            NormalizeDataTransformation: self._do_normalize_data,
            OneHotEncodingTransformation: self._do_one_hot_encoding,
            SubtractionTransformation: self._do_subtraction,
            ImageTransformation: self._do_image_transformation,
            ScalarMultiplicationDataTransformation: self._do_scalar_multiplication,
            ScalarAdditionDataTransformation: self._do_scalar_addition,
        }
        cols_to_reverse: Mapping[str, Tuple[float, float]]

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Performs `self.transformations` on `data` sequentially.

        Arguments to an operation are extracted by first checking if they are
        referencing another transformed column by checking for the name attribute.
        If not, we then check if they are referencing a non-transformed column by
        using a regular expression. Finally, if the regex comes back empty we take
        the argument 'as is' e.g. a string, integer, etc. After the transformations
        are complete, finally removes any columns that shouldn't be part of the final
        output.

        Args:
            data: The `pandas` dataframe to be transformed.

        Raises:
            MissingColumnReferenceError: If there is a reference to a non-existing
                column.
            TypeError: if there are clashes between column names or if unable
                to apply transformation.
        """
        data_columns = set(data.columns)
        # Check that all referenced columns are present in `data`
        missing_cols = sorted(self.col_refs.difference(data_columns))
        if missing_cols:
            raise MissingColumnReferenceError(
                [f"Reference to non-existent column: {c}" for c in missing_cols]
            )
        # Loop through transformations and perform them sequentially
        application_errors = []
        cols_to_drop = []
        for transformation in self.transformations:
            # Transformation name is always set
            transformation.name = cast(str, transformation.name)

            # Check transformation output doesn't clash with existing column
            if isinstance(transformation, MultiColumnOutputTransformation):
                clashes = data_columns.intersection(transformation.columns)
            else:
                clashes = data_columns.intersection([transformation.name])
            if clashes:
                application_errors.extend(
                    [
                        f"Output column {col_name}, "
                        f"from transformation {transformation.name}, "
                        f"clashes with an existing data column name."
                        for col_name in sorted(clashes)
                    ]
                )
                continue

            # Get operation as a function
            operation = self._operators[type(transformation)]

            # Add column(s) to `cols_to_drop` if it shouldn't end up in dataframe
            if not transformation.output:
                if isinstance(transformation, MultiColumnOutputTransformation):
                    cols_to_drop.extend(transformation.columns)
                else:  # normal transformation type
                    cols_to_drop.append(transformation.name)

            # Attempt to perform transformation. If there is a type mismatch
            # pandas will throw a type error which we catch and skip the
            # transformation.
            try:
                data = operation(data, transformation)
            except TypeError as e:
                application_errors.append(
                    f"Unable to apply transformation, skipping: "
                    f"{transformation.name}: {e}"
                )

        # Check all transformations were applied OK
        if application_errors:
            raise TransformationApplicationError(application_errors)

        # Drop any columns that should not be part of the final dataframe
        if cols_to_drop:
            return data.drop(cols_to_drop, axis=1)

        return data

    def batch_transform(self, data: np.ndarray, step: DataSplit) -> np.ndarray:
        """Performs batch transformations.

        Args:
            data: The data to be transformed at batch time as a numpy array.
            step: The step at which the data should be transformed.

        Raises:
            InvalidBatchTransformationError: If one of the specified transformations
                does not inherit from `BatchTimeOperation`.

        Returns:
            np.ndarray: The transformed data as a numpy array.
        """
        for transformation in self.transformations:
            # Check transformation is a batch time operation
            if not isinstance(transformation, BatchTimeOperation):
                raise InvalidBatchTransformationError(
                    f"{transformation._registry_name} not a batch time operation"
                )

            # Skip the transformation if it does not apply to the step
            if transformation.step != step:
                logger.debug(f"Skipping transformation: {transformation.name}")
                continue

            logger.debug(f"Applying transformation: {transformation.name}")
            # Get operation as a function
            operation = self._operators[type(transformation)]
            data = operation(data, transformation)

        return data

    @staticmethod
    def _apply_arg_conversion(
        data: pd.DataFrame, *args: Union[Transformation, str, Any]
    ) -> Union[Union[pd.Series, Any], List[Union[pd.Series, Any]]]:
        """Applies argument conversion to each of the supplied *args.

        Check, in order, if it is a:
            - Transformation instance (use transformation output column from data)
            - A column reference (use original column from data)
            - Other (use arg as is)

        Args:
            data: Data in a dataframe.
            *args: The args to convert.

        Returns: A single converted arg if only one was supplied, or a list of converted
            args in the same order they were supplied.
        """
        converted: List[Union[pd.Series, Any]] = []
        for arg in args:
            # See if it is a transformation
            if isinstance(arg, Transformation):
                converted.append(data[arg.name])
                continue

            # See if it is a column reference
            try:
                col_ref = _extract_col_ref(arg)
                converted.append(data[col_ref])
                continue
            except NotColumnReferenceError:
                pass

            # Otherwise, just use as is
            converted.append(arg)

        # If only one arg supplied, return single arg
        if len(converted) == 1:
            return converted[0]
        # Otherwise return list
        return converted

    @staticmethod
    def _get_list_of_col_refs(
        data: pd.DataFrame, cols: Union[str, List[str]], schema_cols: List[str]
    ) -> Tuple[List[str], bool]:
        """Gets the list of actual column references from a list of potentials.

        Generates a list of col names from a potential column list argument
        which could be:
            - a list of column references
            - "all": in which case use schema and data to generate list
            - a single column reference: wrap in a list

        Args:
            data:
                The data containing the columns.
            cols:
                The column reference(s) or "all".
            schema_cols:
                The list of schema columns to use to generate in case of "all".

        Returns:
            A tuple of the list of column references and a boolean indicating whether
            these have been "pre-extracted" (i.e. don't need to be compared to
            COLUMN_REFERENCE).
        """
        pre_extracted = False
        out_cols = cols

        if isinstance(out_cols, list):
            # If columns are not pre-extracted, they will have start
            # with "c:" or "col:"
            if not any(":" in col_name for col_name in out_cols):
                pre_extracted = True
            out_cols = out_cols
        elif isinstance(out_cols, str):
            if out_cols == "float":
                pre_extracted = True
                out_cols = cast(
                    list, data.select_dtypes(include=["float"]).columns.to_list()
                )
            elif out_cols == "all":
                # Extract all target columns from schema
                pre_extracted = True
                out_cols = [col for col in schema_cols if col in data.columns]
            else:
                # Wrap single column in iterable
                out_cols = [out_cols]
        return out_cols, pre_extracted

    @staticmethod
    def _do_addition(data: pd.DataFrame, t: AdditionTransformation) -> pd.DataFrame:
        """Performs addition transformation on `data` and returns it."""
        arg1, arg2 = TransformationProcessor._apply_arg_conversion(data, t.arg1, t.arg2)
        data[t.name] = arg1 + arg2
        return data

    def _do_clean_data(
        self, data: pd.DataFrame, t: CleanDataTransformation
    ) -> pd.DataFrame:
        """Cleans categorical and continuous columns in the data.

        Replaces infinities and NAs.
        """
        # Get columns
        cols, pre_extracted = self._get_list_of_col_refs(
            data, t.cols, self._schema_cat_cols + self._schema_cont_cols
        )
        if not pre_extracted:
            cols = [_extract_col_ref(col) for col in cols]

        # Clean columns
        for col_ref in cols:
            # categorical columns
            if col_ref in self._schema_cat_cols:
                data[col_ref] = data[col_ref].fillna("nan")
            # continuous columns
            elif col_ref in self._schema_cont_cols:
                data[col_ref] = data[col_ref].replace([np.inf, -np.inf], np.nan)
                data[col_ref] = data[col_ref].fillna(value=0.0)
            else:
                logger.warning(f"{col_ref} not found in Schema. Skipping cleaning.")

        return data

    @staticmethod
    def _do_comparison(data: pd.DataFrame, t: ComparisonTransformation) -> pd.DataFrame:
        """Performs comparison between arg1 and arg2 of comparison transformation."""
        arg1, arg2 = TransformationProcessor._apply_arg_conversion(data, t.arg1, t.arg2)

        arg1 = arg1.to_numpy()
        try:
            # If arg2 is a series-like
            arg2 = arg2.to_numpy()
        except AttributeError:
            # If arg2 is a constant
            arg2 = np.full_like(arg1, fill_value=arg2)
        conditions = [arg1 < arg2, arg1 == arg2, arg1 > arg2]
        choices = [-1, 0, 1]

        data[t.name] = np.select(conditions, choices, default=np.nan).tolist()

        return data

    @staticmethod
    def _do_division(data: pd.DataFrame, t: DivisionTransformation) -> pd.DataFrame:
        """Performs division transformation on `data` and returns it."""
        arg1, arg2 = TransformationProcessor._apply_arg_conversion(data, t.arg1, t.arg2)
        data[t.name] = arg1 / arg2
        return data

    @staticmethod
    def _do_inclusion(data: pd.DataFrame, t: InclusionTransformation) -> pd.DataFrame:
        # Only arg should be a column name in this transformation
        """Performs inclusion transformation on `data` and returns it."""
        arg = TransformationProcessor._apply_arg_conversion(data, t.arg)
        arg = cast(pd.Series, arg)
        data[t.name] = arg.str.contains(t.in_str)
        return data

    @staticmethod
    def _do_multiplication(
        data: pd.DataFrame, t: MultiplicationTransformation
    ) -> pd.DataFrame:
        """Performs multiplication transformation on `data` and returns it."""
        arg1, arg2 = TransformationProcessor._apply_arg_conversion(data, t.arg1, t.arg2)
        data[t.name] = arg1 * arg2
        return data

    def _do_normalize_data(
        self,
        data: pd.DataFrame,
        t: NormalizeDataTransformation,
    ) -> pd.DataFrame:
        """Normalizes numeric columns using their mean and stddev.

        Note: The default value of the transformation.cols for this
        transformation is "float". Results in mean of 0 and stddev of 1.
        """
        cols, pre_extracted = self._get_list_of_col_refs(
            data,
            t.cols,
            self._schema_cont_cols,
        )
        if not pre_extracted:
            cols = [_extract_col_ref(col) for col in cols]
        for col_ref in cols:
            if not is_numeric_dtype(data[col_ref]):
                raise TypeError(
                    f'Cannot normalize column "{col_ref}" as it is not numeric.'
                )
            mean = data[col_ref].mean()
            stddev = data[col_ref].std()
            data[col_ref] = (data[col_ref] - mean) / (1e-7 + stddev)
        if self.schema is not None:
            for col in cols:
                self.schema.features["continuous"][col].dtype = data[col].dtype

        return data

    def _do_scalar_multiplication(
        self, data: pd.DataFrame, t: ScalarMultiplicationDataTransformation
    ) -> pd.DataFrame:
        """Performs column multiplication with scalar.

        Only applicable to numeric columns.

        Raises:
            TypeError: if one of the referenced columns is not numeric.
            MissingColumnReferenceError: if one of the referenced columns is missing.
        """
        # If the scalar is a numerical value, we apply the scalar
        # multiplication to all numerical columns.
        if isinstance(t.scalar, (int, float)):
            cols, pre_extracted = self._get_list_of_col_refs(
                data, t.cols, self._schema_cont_cols
            )
            if not pre_extracted:
                cols = [_extract_col_ref(col) for col in cols]

            data[cols] = data[cols] * t.scalar
            return data
        # Otherwise, it is a dictionary mapping column names to scalar,
        # so we multiply each column with the scalar it is mapped to.
        else:
            missing_cols = set(t.scalar.keys()) - set(data.columns)
            if missing_cols:
                raise MissingColumnReferenceError(
                    [f"Reference to non-existent column: {c}" for c in missing_cols]
                )
            for col_ref, scalar in t.scalar.items():
                if not is_numeric_dtype(data[col_ref]):
                    raise TypeError(
                        f'Cannot normalize column "{col_ref}" as it is not numeric.'
                    )
                data[col_ref] = data[col_ref] * scalar
            return data

    def _do_scalar_addition(
        self, data: pd.DataFrame, t: ScalarAdditionDataTransformation
    ) -> pd.DataFrame:
        """Performs column addition with scalar.

        Only applicable to numeric columns.

        Raises:
            TypeError: if one of the referenced columns is not numeric.
            MissingColumnReferenceError: if one of the referenced columns is missing.
        """
        # If the scalar is a numerical value, we apply the scalar
        # addition to all numerical columns.
        if isinstance(t.scalar, (int, float)):
            cols, pre_extracted = self._get_list_of_col_refs(
                data, t.cols, self._schema_cont_cols
            )
            if not pre_extracted:
                cols = [_extract_col_ref(col) for col in cols]

            data[cols] = data[cols] + t.scalar
            return data
        # Otherwise, it is a dictionary mapping column names to scalar,
        # so we add the scalar to the column it is mapped to.
        else:
            missing_cols = set(t.scalar.keys()) - set(data.columns)
            if missing_cols:
                raise MissingColumnReferenceError(
                    [f"Reference to non-existent column: {c}" for c in missing_cols]
                )
            for col_ref, scalar in t.scalar.items():
                if not is_numeric_dtype(data[col_ref]):
                    raise TypeError(
                        f'Cannot normalize column "{col_ref}" as it is not numeric.'
                    )
                data[col_ref] = data[col_ref] + scalar
            return data

    @staticmethod
    def _do_one_hot_encoding(
        data: pd.DataFrame, t: OneHotEncodingTransformation
    ) -> pd.DataFrame:
        """Performs one hot encoding transformation on `data` and returns it."""
        # Get unencoded data and columns
        # Only one arg supplied so therefore is single series that's returned
        arg: pd.Series = cast(
            pd.Series, TransformationProcessor._apply_arg_conversion(data, t.arg)
        )
        ohe_cols: List[str] = sorted(t.columns)
        n_rows: int = len(arg)
        n_cols: int = len(ohe_cols)

        # Create an appropriately sized dataframe, filled with zeros
        ohe_df: pd.DataFrame = pd.DataFrame(
            data=np.zeros(shape=(n_rows, n_cols), dtype=np.int8), columns=ohe_cols
        )

        # First, set all values in the unknown column to 1 which correspond to
        # non-null values in the arg Series. These will be marked into the correct
        # column as we find matches, and if no match is found, they should be in
        # this column anyway.
        not_null_idxs = arg.index[arg.notnull()]
        ohe_df.loc[not_null_idxs, t.unknown_col] = 1

        # Iterate through the (value, target_col) pairs and set the correct column
        # to 1 for all locations the value is found. Sets the unknown column in
        # the same locations to 0.
        for val, target_col in t.values.items():
            match_idxs = arg.index[arg == val]
            ohe_df.loc[match_idxs, target_col] = 1
            ohe_df.loc[match_idxs, t.unknown_col] = 0

        return pd.concat([data, ohe_df], axis=1)

    @staticmethod
    def _do_subtraction(
        data: pd.DataFrame, t: SubtractionTransformation
    ) -> pd.DataFrame:
        """Performs subtraction transformation on `data` and returns it."""
        arg1, arg2 = TransformationProcessor._apply_arg_conversion(data, t.arg1, t.arg2)
        data[t.name] = arg1 - arg2
        return data

    @staticmethod
    def _do_image_transformation(
        data: np.ndarray, t: ImageTransformation
    ) -> np.ndarray:
        """Performs image transformation on `data` and returns it."""
        logger.debug(f"Applying image transformations: {t.transformations}")
        tfm = t.get_callable()
        return tfm(image=data)["image"]
