"""
A股市场月末的概念标签
"""
from WindPy import w
import pandas as pd
import hbshare as hbs
from datetime import datetime, timedelta
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB

w.start()

selected_concept = ['顺周期', '资源股', '半导体产业', '光伏', '锂电池', '大消费', '元宇宙', '新基建']


class StockConception:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = "stock_conception"
        self._load_calendar()

    def _load_calendar(self):
        start_date = self.start_date.replace('-', '')
        end_date = self.end_date.replace('-', '')
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            start_date, end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        self.calendar_df = df

    def get_stock_concept_data(self):
        trading_day_list = self.calendar_df[self.calendar_df['isMonthEnd'] == 1]['calendarDate'].tolist()
        all_concept = []
        for date in trading_day_list:
            # 股票池
            sql_script = "SELECT SYMBOL, TDATE, VATURNOVER, TCAP FROM finchina.CHDQUOTE WHERE TDATE = {}".format(date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
            data = data[data['SYMBOL'].str[0].isin(['0', '3', '6'])]
            data = data[data['VATURNOVER'] > 1e-6]
            data['sec_code'] = data['SYMBOL'].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')
            ticker_list = data['sec_code'].tolist()
            # 概念数据
            res = w.wss(','.join(ticker_list), 'concept', "tradeDate={}".format(date))
            if res.ErrorCode != 0:
                df = pd.DataFrame()
                print("fetch concept data error: trade_date = {}".format(date))
            else:
                df = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Fields)
                df.index.name = 'sec_code'
            # process
            concept_list = []
            for sec in df.index.tolist():
                sub_list = df.loc[sec, 'CONCEPT'].split(';')
                concept_list = list(set(concept_list).union(set(sub_list)))

            concept_df = pd.DataFrame(index=df.index, columns=concept_list)
            for sec in concept_df.index.tolist():
                sub_list = df.loc[sec, 'CONCEPT'].split(';')
                concept_df.loc[sec, sub_list] = 1

            concept_df = concept_df[selected_concept].dropna(how='all')
            concept_df.reset_index(inplace=True)
            concept_df['trade_date'] = date
            concept_df['ticker'] = concept_df['sec_code'].apply(lambda x: x.split('.')[0])
            concept_df = concept_df[['trade_date', 'ticker'] + selected_concept]
            concept_df = pd.melt(concept_df, id_vars=['trade_date', 'ticker'],
                                 value_vars=selected_concept, var_name='concept').dropna()
            concept_df = concept_df[['trade_date', 'ticker', 'concept']]

            all_concept.append(concept_df)

        all_concept = pd.concat(all_concept)

        return all_concept

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_stock_concept_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table stock_conception(
                id int auto_increment primary key,
                trade_date date not null,
                ticker varchar(10),
                concept varchar(10)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_stock_concept_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    StockConception('2021-01-01', '2022-01-31', is_increment=0).get_construct_result()