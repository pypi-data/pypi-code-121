"""
私募基金估值表持仓入库
"""
import os
import pandas as pd
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB


class HoldingExtractor:
    def __init__(self, data_path, table_name, fund_name, is_increment=1):
        self.data_path = data_path
        self.table_name = table_name
        self.fund_name = fund_name
        self.is_increment = is_increment

    def _load_portfolio_weight(self):
        filenames = os.listdir(self.data_path)
        filenames = [x for x in filenames if x.split('.')[-1] in ['xls', 'xlsx']]

        portfolio_weight_list = []
        for name in filenames:
            if self.fund_name in ['因诺聚配中证500指数增强', '凡二中证500增强9号1期',
                                  '赫富500指数增强一号', '宽德金选中证500指数增强6号']:
                data = pd.read_excel(
                    os.path.join(self.data_path, name), sheet_name=0, header=3).dropna(subset=['科目代码'])
                sh = data[data['科目代码'].str.startswith('11020101')]
                sz = data[data['科目代码'].str.startswith('11023101')]
                cyb = data[data['科目代码'].str.startswith('11024101')]
                kcb = data[data['科目代码'].str.startswith('1102C101')]
                df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
                df['ticker'] = df['科目代码'].apply(lambda x: x[-6:])
                df.rename(columns={"科目名称": "sec_name", "市值占净值%": "weight"}, inplace=True)
                if self.fund_name == "因诺聚配中证500指数增强":
                    date = name.split('_')[-2]
                elif self.fund_name == "凡二中证500增强9号1期":
                    date = name.split('.')[0].split('__')[-2]
                    df['weight'] = df['weight'].str.strip('%').astype(float)
                elif self.fund_name == '赫富500指数增强一号':
                    date = name.split('_')[-1].split('.')[0][:-3].replace('-', '')
                elif self.fund_name == '宽德金选中证500指数增强6号':
                    date = name.split('_')[-1].split('.')[0]
                else:
                    date = None
            elif self.fund_name in ['量客卓宇六号', '星阔广厦12号中证500指数增强', '星阔广厦1号中证500指数增强', '星阔山海6号']:
                date = name[-12:].split('.')[0]
                data = pd.read_excel(
                    os.path.join(self.data_path, name), sheet_name=0, header=7).dropna(subset=['科目代码'])
                sh = data[data['科目代码'].str.endswith('SH')]
                sz = data[data['科目代码'].str.endswith('SZ')]
                df = pd.concat([sh, sz], axis=0)
                df['ticker'] = df['科目代码'].apply(lambda x: x.split(' ')[0][-6:])
                df.rename(columns={"科目名称": "sec_name", "市值占比": "weight"}, inplace=True)
                df['weight'] *= 100.
            elif self.fund_name in ['启林广进中证1000指数增强']:
                date = name.split('.')[0].split('-')[-1]
                data = pd.read_excel(
                    os.path.join(self.data_path, name), sheet_name=0, header=3).dropna(subset=['科目代码'])
                sh = data[data['科目代码'].str.startswith('11020101')]
                sz = data[data['科目代码'].str.startswith('11023101')]
                cyb = data[data['科目代码'].str.startswith('11024101')]
                kcb = data[data['科目代码'].str.startswith('1102C101')]
                df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
                df['ticker'] = df['科目代码'].apply(lambda x: x[-6:])
                df.rename(columns={"科目名称": "sec_name", "市值占净值%": "weight"}, inplace=True)
            elif self.fund_name in ['乾象中证500指数增强1号']:
                date = name.split('_')[-1].split('.')[0]
                data = pd.read_excel(
                    os.path.join(self.data_path, name), sheet_name=0, header=6).dropna(subset=['科目代码'])
                sh = data[data['科目代码'].str.startswith('1102.01.01')]
                sz = data[data['科目代码'].str.startswith('1102.33.01')]
                cyb = data[data['科目代码'].str.startswith('1102.34.01')]
                kcb = data[data['科目代码'].str.startswith('1102.02.01')]
                df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
                df['ticker'] = df['科目代码'].apply(lambda x: x.split(' ')[0].split('.')[-1])
                # 处理一下分红
                ratio = data[data['科目代码'] == '资产净值']['市值占比'].values[0] / \
                    data[data['科目代码'] == '资产合计']['市值占比'].values[0]
                df.rename(columns={"科目名称": "sec_name", "市值占比": "weight"}, inplace=True)
                df['weight'] *= ratio * 100.
            elif self.fund_name in ['伯兄卢比孔']:
                date = name.split('_')[-1].split('.')[0][:-3].replace('-', '')
                data = pd.read_excel(
                    os.path.join(self.data_path, name), sheet_name=0, header=3).dropna(subset=['科目代码'])
                sh = data[data['科目代码'].str.startswith('11021101')]
                cyb = data[data['科目代码'].str.startswith('11021501')]
                sz = data[data['科目代码'].str.startswith('11023201')]
                kcb = data[data['科目代码'].str.startswith('1102D201')]
                df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
                df['ticker'] = df['科目代码'].apply(lambda x: x[-6:])
                df.rename(columns={"科目名称": "sec_name", "市值占净值%": "weight"}, inplace=True)
            elif self.fund_name in ['白鹭精选量化鲲鹏十号']:
                date = name.split('_')[-1].split('.')[0][:-3].replace('-', '')
                data = pd.read_excel(
                    os.path.join(self.data_path, name), sheet_name=0, header=3).dropna(subset=['科目代码'])
                sh = data[data['科目代码'].str.startswith('11020101')]
                cyb = data[data['科目代码'].str.startswith('11024101')]
                sz = data[data['科目代码'].str.startswith('11023101')]
                kcb = data[data['科目代码'].str.startswith('1102C201')]
                df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
                df['ticker'] = df['科目代码'].apply(lambda x: x[-6:])
                df.rename(columns={"科目名称": "sec_name", "市值占净值%": "weight"}, inplace=True)
            elif self.fund_name in ['世纪前沿指数增强2号', '伯兄建康']:
                date = name.split('.')[0][-8:]
                hd = 2 if date >= '20210630' else 0
                data = pd.read_excel(
                    os.path.join(self.data_path, name), sheet_name=0, header=hd).dropna(subset=['科目代码'])
                sh = data[data['科目代码'].str.startswith('11020101')]
                sz = data[data['科目代码'].str.startswith('11023101')]
                cyb = data[data['科目代码'].str.startswith('11024101')]
                kcb = data[data['科目代码'].str.startswith('1102C101')]
                df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
                df['ticker'] = df['科目代码'].apply(lambda x: x[-6:])
                df.rename(columns={"科目名称": "sec_name", "市值占净值(%)": "weight"}, inplace=True)
            else:
                date = None
                df = pd.DataFrame()

            df['trade_date'] = date
            portfolio_weight_list.append(df[['trade_date', 'ticker', 'sec_name', 'weight']])

        portfolio_weight_df = pd.concat(portfolio_weight_list)
        portfolio_weight_df = portfolio_weight_df.groupby(
            ['trade_date', 'ticker', 'sec_name'])['weight'].sum().reset_index()
        portfolio_weight_df['fund_name'] = self.fund_name

        return portfolio_weight_df

    def writeToDB(self):
        if self.is_increment == 1:
            data = self._load_portfolio_weight()
            trading_day_list = data['trade_date'].unique().tolist()
            sql_script = "delete from {} where trade_date in ({}) and fund_name = '{}'".format(
                self.table_name, ','.join(trading_day_list), self.fund_name)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table {}(
                id int auto_increment primary key,
                trade_date date not null,
                ticker varchar(10),
                sec_name varchar(20),
                weight decimal(5, 4),
                fund_name varchar(20))
            """.format(self.table_name)
            create_table(self.table_name, sql_script)
            data = self._load_portfolio_weight()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    # HoldingExtractor(data_path='D:\\研究基地\\A-机器学习类\\因诺\\聚配500估值表及绩效报告',
    #                  table_name="private_fund_holding", fund_name="因诺聚配中证500指数增强").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\星阔广厦1号中证500指增', table_name="private_fund_holding",
    #                  fund_name="星阔广厦1号中证500指数增强").writeToDB()
    HoldingExtractor(data_path='D:\\估值表基地\\星阔山海6号', table_name="private_fund_holding",
                     fund_name="星阔山海6号").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\启林城上进取1号', table_name="private_fund_holding",
    #                  fund_name="启林城上进取1号").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\凡二中证500增强9号1期', table_name="private_fund_holding",
    #                  fund_name="凡二中证500增强9号1期").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\伯兄卢比孔', table_name="private_fund_holding",
    #                  fund_name="伯兄卢比孔").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\伯兄建康', table_name="private_fund_holding",
    #                  fund_name="伯兄建康").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\世纪前沿指数增强2号', table_name="private_fund_holding",
    #                  fund_name="世纪前沿指数增强2号").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\启林广进中证1000指数增强', table_name="private_fund_holding",
    #                  fund_name="启林广进中证1000指数增强").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\乾象中证500指数增强1号', table_name="private_fund_holding",
    #                  fund_name="乾象中证500指数增强1号").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\赫富500指数增强一号', table_name="private_fund_holding",
    #                  fund_name="赫富500指数增强一号").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\白鹭精选量化鲲鹏十号', table_name="private_fund_holding",
    #                  fund_name="白鹭精选量化鲲鹏十号").writeToDB()
    # HoldingExtractor(data_path='D:\\估值表基地\\宽德金选中证500指数增强6号', table_name="private_fund_holding",
    #                  fund_name="宽德金选中证500指数增强6号").writeToDB()