from functools import partial
import pandas as pd

from .base import *
from .exceptions import *


class TableColumnsExistExpectations(ExpectationBase):
    """
    Check whether table has required columns

    Configuration has to specify a list of columns::

           {
             'expectation': 'table_columns_exist',
             'params': {
                 'columns': ['alpha', 'beta']
                 }
             }
           }

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "table_columns_exist"
        self.description = "Check whether columns exist (in any order)"

    def validate_args(self, config):
        super().validate_args(config)

        # Add extra
        self.args_validator_attrs_list(config, ["columns"])

    def generate(self, df):
        """
        Not implemented
        """
        return {
            "expectation": self.name,
            "description": self.description,
            "params": {"columns": list(df.columns)},
        }

    def validate(self, df, config):
        """
        Check if the specified columns are present in the dataframe
        """

        result = ExpectationResultBase()
        update = partial(
            result.add_result, expectation=self.name, description=self.description
        )

        if not isinstance(df, pd.DataFrame):
            update(passed=False, extra={"reason": "Not a dataframe"})
            return result

        columns = config["params"]["columns"]
        if isinstance(columns, str):
            columns = [columns]

        missing = [c for c in columns if c not in df.columns]
        if len(missing) > 0:
            update(
                passed=False,
                extra={"reason": "Missing columns: {}".format(",".join(missing))},
            )
            return result

        update(passed=True)
        return result


class TableColumnsPositionExpectations(ExpectationBase):
    """
    Check whether table has the right columns in right positions.

    Configuration has to specify the columns and their corresponding
    positions in the test dataframe::

           {
             'expectation': 'table_columns_exist_with_position',
             'params': {
                 'columns': {
                    'alpha': 0,
                    'beta': 2
                 }
             }
           }

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "table_columns_exist_with_position"
        self.description = "Check whether columns exist (in particular order)"

    def validate_args(self, config):
        super().validate_args(config)

        # Add extra
        self.args_validator_attrs_list(config, ["columns"])

    def generate(self, df):
        """
        Not implementated yet.
        """
        columns = df.columns
        columns = {col: position for col, position in enumerate(columns)}
        return {
            "expectation": self.name,
            "description": self.description,
            "params": {"columns": columns},
        }

    def validate(self, df, config):
        """
        Validate the names and positions of columns
        """

        result = ExpectationResultBase()
        update = partial(
            result.add_result, expectation=self.name, description=self.description
        )

        if not isinstance(df, pd.DataFrame):
            update(passed=False, extra={"reason": "Not a dataframe"})
            return result

        columns = config["params"]["columns"]
        if not isinstance(columns, dict):
            raise InvalidConfigurationExpectation("Columns should be a dict")

        invalid = []
        existing = list(df.columns)
        for col, position in columns.items():
            if (
                (not isinstance(position, int))
                or (position >= len(existing))
                or (existing[position] != col)
            ):
                invalid.append(col)

        if len(invalid) > 0:
            update(
                passed=False,
                extra={
                    "reason": "Missing/Wrong position columns: {}".format(
                        ",".join(invalid)
                    )
                },
            )
            return result

        update(passed=True)
        return result
