from lumipy.common.string_utils import indent_str
from lumipy.query.expression.direct_provider.direct_provider_base import DirectProviderBase
from lumipy.client import Client
from typing import Optional, NoReturn
import pandas as pd

from lumipy.query.expression.sql_value_type import SqlValType


class DriveSave(DirectProviderBase):
    """Class representing Drive.SaveAs direct provider use expression.

    """

    def __init__(self, drive_path: str, client: Client, drive_file_type: Optional[str] = 'csv', **batch):
        """__init__ method of the DriveSave class.

        Args:
            drive_path (str): path in drive to save files to.
            client (Client): luminesce web api client instance.
            drive_file_type: file type to save as (csv, sqlite, xlsx)
            **batch: batch of table variables to save to drive specified as keyword args. Keyword is the filename.
        """

        col_guide = {
            'VariableName': SqlValType.Text,
            'FileName': SqlValType.Text,
            'RowCount': SqlValType.Int
        }

        file_names = batch.keys()
        save_tables = [batch[k] for k in file_names]

        fn_str = '\n'.join(file_names)
        sql_def = f"""use Drive.SaveAs with {', '.join(t.get_sql() for t in save_tables)}
            --path={drive_path}
            --type:{drive_file_type}
            --fileNames
        {indent_str(fn_str, 6)}
        enduse"""

        super().__init__(
            sql_def,
            f"write_{drive_file_type}_{str(hash(fn_str + drive_path))[1:]}",
            col_guide,
            client,
            *save_tables
        )

    def print_sql(self) -> NoReturn:
        """Print the SQL that this expression resolves to.

        """

        self.select('*').print_sql()

    def go(self) -> pd.DataFrame:
        """Send query off to Luminesce, monitor progress and then get the result back as a pandas dataframe.

        Returns:
            DataFrame: the result of the query as a pandas dataframe.
        """
        return self.select('*').go()
