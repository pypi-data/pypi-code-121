import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.request


def stock_history_us_individual(code: str = "AAPL",
                                start_date: str = '',
                                end_date: str = '') -> pd.DataFrame:
    url = "https://www.nasdaq.com/market-activity/stocks/{}/historical".format(
        code.lower())
    url = 'https://api.nasdaq.com/api/quote/AAPL/historical?assetclass=stocks&fromdate=2019-01-01&limit=18&todate=2019-12-20'
    header = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }
    rst = requests.get(url, headers=header)
    print(rst)
    return pd.DataFrame()
