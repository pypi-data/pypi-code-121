import pandas as pd

from lumipy.query.expression.direct_provider.direct_provider_base import DirectProviderBase
from lumipy.client import Client
from typing import Optional

from lumipy.query.expression.sql_value_type import SqlValType


class DriveRead(DirectProviderBase):
    """Data source class that represents reading a data file in drive.

    """

    def __init__(self, full_path: str, client: Client, file_type: str, excel_range: Optional[str] = None):
        """__init__ method of the DriveRead class

        Args:
            full_path (str): full path to the drive file.
            client (Client): luminesce web api client instance.
            file_type (str): type of the file (csv, excel or sqlite)
            excel_range (Optional[str]): range of excel file to read. Optional, only valid for excel file reads.
        """
        range_str = f'--range={excel_range}' if excel_range is not None else ''
        top_row = client.query_and_fetch(f"""
        @x = use Drive.{file_type} limit 1 
            --file={full_path} 
            {range_str}
        enduse;
         
        select * from @x
        """)
        if top_row.shape[0] == 0:
            raise ValueError(f"The file ({full_path}) appears to be empty.")

        names = top_row.columns
        types = [self._infer_type_of_str(s) for s in top_row.iloc[0].tolist()]
        # Type inference
        guide = {c: t for c, t in zip(names, types)}

        sql_def = f"""use Drive.{file_type}
        --file={full_path}
        {range_str}
        enduse"""
        var_name = f"get_{str(hash(full_path))[1:]}"
        super().__init__(
            sql_def,
            var_name,
            guide,
            client
        )

    # noinspection PyBroadException
    @staticmethod
    def _infer_type_of_str(s: str) -> SqlValType:
        try:
            int(s)
            return SqlValType.Int
        except:
            pass

        try:
            float(s)
            return SqlValType.Double
        except:
            pass

        try:
            pd.to_datetime(s)
            return SqlValType.DateTime
        except:
            pass

        return SqlValType.Text
