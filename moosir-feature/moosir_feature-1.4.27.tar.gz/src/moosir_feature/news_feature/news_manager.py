import pandas as pd
import numpy as np
import investpy
from .data_access import *
from .feature_extractor_news import *


months = np.arange(1, 13)
# years =  [2015, 2016, 2017, 2018, 2019, 2020, 2021]
IMPORTANCE = "high"
# download it for a month, year, day
# download if it is not there or overwrite existing
# flush state
# clean data and store

class NewsFeatureManager():
    def __init__(self, dal: IDataAccessLayer, data_provider_tz: str, countries: list):
        self.dal = dal
        self.data_provider_tz = data_provider_tz
        self.countries = countries


    def _save_month(self, month_n: int, year: int):
        from_date = f"01/{month_n:02d}/{year}"
        end_date = f"01/{month_n + 1:02d}/{year}" if month_n < 12 else f"01/{1:02d}/{year + 1}"
        data = investpy.economic_calendar(time_zone=self.data_provider_tz,
                                          from_date=from_date,
                                          to_date=end_date,
                                          countries=self.countries,
                                          importances=[IMPORTANCE])

        return data

    def save_news_years(self, years):
        for year in years:
            for month_n in months:
                month = f"{month_n:02d}"
                print(f"start processing -  month: {month}, year: {year}")
                data = self._save_month(month_n=month_n, year=year)
                # save
                print("saving news data ==============================")
                self.dal.save_news_data(data, month=month, year=year, if_raw=True)

    def save_news_months(self, months:list, year:int):
        for month in months:
            data = self._save_month(month_n=month, year=year)
            self.dal.save_news_data(news_df=data, month=month, year=year, if_raw=True)

    def get_news(self):
        news_data = self.dal.get_news_data_all(if_raw=True)
        cleaned = clean_data(news_data=news_data)
        return cleaned

    def get_news_month(self, month: int, year: int):
        news_data = self.dal.get_news_data(month=month, year=year, if_raw=True, if_format=True)
        cleaned = clean_data(news_data=news_data)
        return cleaned

# def all_together():
#     download_news()
#     DATA_PROVIDER = "investingcom"
#     dal = H5DataAccessLayer(data_provider=DATA_PROVIDER, resolution="random", symbol="random")
#
#     clean_data["event"] = clean_data["currency"].str.lower() + "_" + clean_data["event"]
