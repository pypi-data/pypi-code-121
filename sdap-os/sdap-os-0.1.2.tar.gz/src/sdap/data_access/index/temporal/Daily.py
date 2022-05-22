from datetime import datetime, timedelta
from typing import List
import xarray

class Daily:
    def __init__(self, format='%Y%j'):
        self.format = format
        self.delta = timedelta(days=1)


    def get_code(self, date_time: datetime):
        return date_time.strftime(self.format)

    def get_datetime(self, code):
        return datetime.strptime(code, self.format)

    def get_xa_codes(self, da: xarray.DataArray):
        # type must be datetime64

        return da.dt.strftime(self.format)

    def get_codes(self, temporal_range: List[str]):

        codes = []
        current_time = temporal_range[0]
        while current_time < temporal_range[1]:
            codes.append(current_time.strftime(self.format))
            current_time += self.delta

        return codes


