import datetime
import time

import pandas as pd
import requests
from zeno_etl_libs.config.common import Config


class Dizprz:
    def __init__(self):
        configobj = Config.get_instance()
        secrets = configobj.get_secrets()
        self.api_token = secrets["LEARNTRON_API_TOKEN"]

    def __send_payload(self, offset, fetch_count, from_date, to_date):
        fromTimePeriod = from_date.strftime("%Y-%m-%d")
        toTimePeriod = to_date.strftime("%Y-%m-%d")
        url = f"https://disprzexternalapi.disprz.com/api/analytics/getLearnerAnalytics?offset={offset}" \
              f"&fetchCount={fetch_count}&fetchCompletionDetails=true&fetchUdfDetails=true" \
              f"&fromTimePeriod={fromTimePeriod}&toTimePeriod={toTimePeriod}&fetchJourneySpecificDetails=true" \
              f"&journeyId=0&fetchModuleSpecificDetails=true"
        """ this to get the total count when offset is zero (first call) """
        if offset == 0:
            url = url + "&fetchTotalCount=true"

        headers = {
            'Learntron-Api-Token': self.api_token,
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def get_disprz_dataframe(self):
        total_count = 20000  # some value > offset to start with
        fetch_count = 1000  # batch size
        offset = 0
        disprz_data = list()  # entire data list

        print("Start fetching the disprz data")
        start_time = time.time()
        to_date = datetime.datetime.today()
        from_date = to_date - datetime.timedelta(days=400)  # last 365 days
        while offset < total_count:
            data = self.__send_payload(offset=offset, fetch_count=fetch_count, from_date=from_date, to_date=to_date)
            if offset == 0 and data:
                total_count = data[0]['totalCount']
                print(f"total data at disprz is: {total_count}")

            offset += fetch_count
            disprz_data += data
            print(f"total: {total_count}, offset: {offset}, length: {len(data)}")

        df = pd.DataFrame(disprz_data)
        print(f"total count: {total_count}, df len: {len(df)}")
        print(f"total time taken was: {time.time() - start_time} sec")
        if total_count == len(df):
            print(f"fetched all data from disprz successfully")
        return df
