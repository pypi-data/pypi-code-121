import pandas as pd
import numpy as np
import re

class IDataAccessLayer:
    def save_news_data(self, news_df: pd.DataFrame, month, year, if_raw):
        pass

    def get_news_data(self, month: int, year: int, if_raw: bool, if_format: bool):
        pass

    def get_news_data_all(self, if_raw):
        pass


class H5DataAccessLayer(IDataAccessLayer):
    def __init__(self, file_path, data_provider):
        self.file_path = file_path
        self.data_provider = data_provider

    def save_news_data(self, news_df: pd.DataFrame, month, year, if_raw):
        key = self._get_news_h5_key(if_raw=if_raw, year=year, month=month)
        news_df.to_hdf(self.file_path, key)

    def get_news_data(self, month: int, year: int, if_raw: bool, if_format: bool):
        key = self._get_news_h5_key(month=month, year=year, if_raw=if_raw)
        raw = pd.read_hdf(self.file_path, key)
        return self._format_raw_data(raw_data=raw)

    def get_news_data_all(self, if_raw):
        store = pd.HDFStore(self.file_path)
        keys = store.keys()
        store.close()

        pattern_str = f"^/{self.data_provider}-(.*)-raw$" if if_raw else f"^/{self.data_provider}-(.*)$"
        pattern = re.compile(pattern_str)

        dfs = []
        for key in keys:
            pattern_result = pattern.search(key)

            if pattern_result:
                print(f"reading key: {key}")
                dfs.append(pd.read_hdf(self.file_path, key))

        result = pd.concat(dfs, axis=0) if len(dfs) > 0 else None

        result = self._format_raw_data(raw_data=result)

        return result

    def _format_raw_data(self, raw_data: pd.DataFrame):
        return raw_data.set_index("id").sort_index().drop_duplicates()

    def _get_news_h5_key(self, month, year, if_raw):
        key = self.data_provider if not if_raw else f"{self.data_provider}-{year}-{month}-raw"
        return key
