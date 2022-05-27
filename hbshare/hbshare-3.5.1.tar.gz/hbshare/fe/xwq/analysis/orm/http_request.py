# -*- coding: utf-8 -*-

import json
import requests
import sys
import traceback
import time
import pandas as pd
from hbshare.fe.xwq.analysis.utils.const_var import TimeDateFormat
from hbshare.fe.xwq.analysis.utils.timedelta_utils import TimeDateUtil


class Curl_Request:
    def __init__(self):
        pass

    def curl_request(self, url, method, data=None, max_times=30):
        """
        处理请求的函数
        """
        valid = False
        times = 0
        dic = None
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                          'AppleWebKit/573.36 (KHTML, like Gecko) '
                          'Chrome/73.0.3683.86 Safari/573.36',
            'Authorization': 'Bearer '
        }
        while not valid and times < max_times:
            try:
                if method == 'GET':
                    r = requests.get(url, headers=headers)
                elif method == 'POST':
                    r = requests.post(url, data=json.dumps(data), headers=headers)
                elif method == 'POST JSON':
                    r = requests.post(url, json=data, headers=headers)
                else:
                    r = requests.put(url, json=data, headers=headers)
                dic = json.loads(r.text)
                valid = True
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                valid = False
                times += 1
                time.sleep(5)
        return dic

    def get_df(self, url, method, data):
        df = self.curl_request(url, method, data)
        pages = df['body']['pages']
        df = pd.DataFrame(df['body']['records'])
        if pages > 1:
            for page in range(2, pages + 1):
                data['page'] = page
                temp_df = self.curl_request(url, method, data)
                df = pd.concat([df, pd.DataFrame(temp_df['body']['records'])], axis=0)
        return df

    def get_duration_between_dates(self, start, end):
        url = 'http://ams-data.intelnal.howbuy.com/data/fund/sac/zsjq'
        method = 'POST'
        data = {
            "tradingDay": {
                "startDate": "{0} 00:00:00".format(TimeDateUtil.convert_format(start, TimeDateFormat.YMD.value, TimeDateFormat.YMDHYPHEN.value)),
                "endDate": "{0} 00:00:00".format(TimeDateUtil.convert_format(end, TimeDateFormat.YMD.value, TimeDateFormat.YMDHYPHEN.value))
            },
            "fields": [
                "zqdm",
                "jyrq",
                "jq",
                "dataSource",
                "pages"
            ],
            "page": 1,
            "perPage": 2000
        }
        df = self.get_df(url, method, data)
        return df

if __name__ == '__main__':
    res = Curl_Request().get_duration_between_dates('20150101', '20220506')