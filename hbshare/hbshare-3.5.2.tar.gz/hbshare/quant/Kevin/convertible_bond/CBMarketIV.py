"""
Wind计算的转债的隐含波动率
"""
from hbshare.fe.common.util.data_loader import get_trading_day_list
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import hbshare as hbs
from WindPy import w

w.start()


class CBMarketIV:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = "cb_market_iv"
        self._load_data()

    def _load_data(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date)
        # data set
        res = w.wset("cbissue", "startdate=2012-01-01;enddate={}".format(datetime.now().strftime('%Y-%m-%d')))
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("Fetching cbissue data error!")
        else:
            data = pd.DataFrame(res.Data, index=res.Fields, columns=res.Codes).T
        # preprocess
        issue_data = data[data['issue_type'].isin(['优先配售和上网定价', '优先配售,网上定价和网下配售'])]
        issue_data = issue_data[['bond_code', 'bond_name', 'listing_date', 'interest_end_date']].dropna()
        issue_data['listing_date'] = issue_data['listing_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        issue_data['interest_end_date'] = issue_data['interest_end_date'].apply(
            lambda x: datetime.strftime(x, '%Y%m%d'))
        # iv data
        iv_list = []
        for date in tqdm(trading_day_list):
            exist_cb = issue_data[(issue_data['listing_date'] < date) & (issue_data['interest_end_date'] > date)]
            cb_code_list = exist_cb['bond_code'].unique()
            res = w.wss(','.join(cb_code_list), "impliedvol", "tradeDate={};rfIndex=7".format(date))
            if res.ErrorCode != 0:
                data = pd.DataFrame()
                print("fetch implied volatility data error: trade_date = {}".format(date))
            else:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times)
            data.columns = ['iv']
            data.index.name = 'bond_code'
            data = data.reset_index().dropna()
            data['trade_date'] = date
            iv_list.append(data)

        iv_df = pd.concat(iv_list)
        iv_df['ticker'] = iv_df['bond_code'].apply(lambda x: x.split('.')[0])
        iv_df['iv'] = iv_df['iv'].round(4)
        self.iv_df = iv_df[['trade_date', 'ticker', 'iv']]

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.iv_df
            sql_script = "delete from {} where trade_date >= {} and trade_date <= {}".format(
                self.table_name, self.start_date, self.end_date)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table cb_market_iv(
                id int auto_increment primary key,
                trade_date date not null,
                ticker varchar(20),
                iv decimal(7, 4)) 
            """
            create_table(self.table_name, sql_script)
            data = self.iv_df
            WriteToDB().write_to_db(data, self.table_name)


class CBMarketPrice:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = "cb_market_price"
        self._load_data()

    def _load_data(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date)
        # data set
        res = w.wset("cbissue", "startdate=2012-01-01;enddate={}".format(datetime.now().strftime('%Y-%m-%d')))
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("Fetching cbissue data error!")
        else:
            data = pd.DataFrame(res.Data, index=res.Fields, columns=res.Codes).T
        # preprocess
        issue_data = data[data['issue_type'].isin(['优先配售和上网定价', '优先配售,网上定价和网下配售'])]
        issue_data = issue_data[['bond_code', 'bond_name', 'listing_date', 'interest_end_date']].dropna()
        issue_data['listing_date'] = issue_data['listing_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        issue_data['interest_end_date'] = issue_data['interest_end_date'].apply(
            lambda x: datetime.strftime(x, '%Y%m%d'))
        # price data
        price_list = []
        for date in tqdm(trading_day_list):
            exist_cb = issue_data[(issue_data['listing_date'] < date) & (issue_data['interest_end_date'] > date)]
            cb_code_list = exist_cb['bond_code'].unique()
            # convprice
            res = w.wss(','.join(cb_code_list), 'convpremiumratio,convprice,underlyingcode', "tradeDate={}".format(date))
            if res.ErrorCode != 0:
                data = pd.DataFrame()
                print("fetch convprice data error: trade_date = {}".format(date))
            else:
                data = pd.DataFrame(data=res.Data, index=res.Fields, columns=res.Codes).T
            data.columns = ['premium', 'convprice', 'sec_code']
            data.index.name = 'cb_code'
            conv_price = data.reset_index().dropna()
            conv_price['ticker'] = conv_price['sec_code'].apply(lambda x: x.split('.')[0])
            # close price
            sql_script = "SELECT SYMBOL, TDATE, TCLOSE FROM finchina.CHDQUOTE WHERE" \
                         " TDATE = {}".format(date)
            data = pd.DataFrame(hbs.db_data_query("readonly", sql_script, page_size=5000)['data']).rename(
                columns={"SYMBOL": "ticker", "TCLOSE": "stock_price"})
            # merge
            data = pd.merge(conv_price, data[['ticker', 'stock_price']], on='ticker')
            data['trade_date'] = date
            price_list.append(data)

        price_df = pd.concat(price_list)
        price_df['ticker'] = price_df['cb_code'].apply(lambda x: x.split('.')[0])
        self.price_df = price_df[['trade_date', 'ticker', 'premium', 'convprice', 'stock_price']]

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.price_df
            sql_script = "delete from {} where trade_date >= {} and trade_date <= {}".format(
                self.table_name, self.start_date, self.end_date)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table cb_market_price(
                id int auto_increment primary key,
                trade_date date not null,
                ticker varchar(20),
                premium decimal(6, 2),
                convprice decimal(6, 2),
                stock_price decimal(6, 2)) 
            """
            create_table(self.table_name, sql_script)
            data = self.price_df
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    # CBMarketIV('20180101', '20201231').get_construct_result()
    CBMarketPrice('20190101', '20191231', is_increment=1).get_construct_result()
