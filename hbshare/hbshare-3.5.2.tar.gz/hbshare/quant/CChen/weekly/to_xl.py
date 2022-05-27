import pandas as pd
import numpy as np
from hbshare.quant.CChen.fund_perf import performance_analysis, performance_specific_ret, update_performance
from hbshare.quant.CChen.load_data import fund_pool_to_hb, fund_data_to_hb
from hbshare.quant.CChen.weekly.xl_cons import (
    ten2twentysix, row_num, module_2_cols, cell_format, cell_format_r, pool_board
)
import xlwings as xw
import xlsxwriter as xl
from datetime import datetime
import pymysql


class FundStats(object):
    note_str = {
        'cta': '红底色：费后净值统计\n红字体：平均保证金高于30%',
        'zx': '红底色：费后净值统计\n红字体：2020打新收益贡献年化5%以上',
        'zz': '红字体：\n2020打新收益贡献年化5%以上',
    }
    order_i = {
        '000300.SH': '沪深300',
        '000905.SH': '中证500',
        '000852.SH': '中证1000'
    }

    xw_box_line_weight = 3

    def __init__(self, start_date, end_date, output_path, fund_data_path, index_data_path, sort=1):
        self.row_num = row_num
        self.start_date = start_date
        self.end_date = end_date
        self.output_path = output_path
        self.data_path = fund_data_path
        self.index_path = index_data_path
        self.m1c = None
        self.m2c = module_2_cols
        self.sort = sort

        self.sum_cta = None
        self.sum_zx = None
        self.sum_zz = None
        self.sum_zz_o = None

        self.long_only_stats = None
        self.key_years = 4
        self.data_avg = pd.DataFrame()

    def sheet_style0(
            self, sht, input_main, nav_data, fund_dict, type1, bold_list=None, red_list=None, skip_list=['多头']
    ):

        row_n = self.row_num - 1

        input_main['index'] = input_main['index'].apply(
            lambda x: '累计收益率' if '以来累计' in x else ('年化收益率' if '以来年化' in x else x)
        )
        input_main = input_main.set_index('index')
        for t in fund_dict:
            if t in skip_list:
                continue
            input_data = input_main[fund_dict[t]].T.copy()

            # 计算分类平均
            funds_list = fund_dict[t]
            if '沪深300' in funds_list:
                funds_list.pop(funds_list.index('沪深300'))
            if '中证500' in funds_list:
                funds_list.pop(funds_list.index('中证500'))
            if '中证1000' in funds_list:
                funds_list.pop(funds_list.index('中证1000'))
            data_avg = nav_data[['t_date'] + funds_list].sort_values(by='t_date')
            data_avg = data_avg[data_avg['t_date'] >= datetime(2017, 12, 27).date()].set_index('t_date').pct_change()
            data_avg_nav = data_avg.mean(axis=1).fillna(0)
            data_avg_nav = (data_avg_nav + 1).cumprod()

            data_nav_df = data_avg_nav.reset_index().rename(columns={0: 'nav'})
            data_nav_df['type2'] = t
            if len(skip_list) == 0:
                data_nav_df['type1'] = type1 + 'a'
            else:
                data_nav_df['type1'] = type1
            self.data_avg = self.data_avg.append(data_nav_df)

            avg_date = data_avg_nav.reset_index().copy()
            avg_date.loc[:, 'year'] = pd.to_datetime(avg_date['t_date']).dt.year
            avg_date = avg_date.drop_duplicates(subset=['year'], keep='last')
            avg_date = avg_date[avg_date['year'] >= 2018].sort_values(by='year', ascending=False).reset_index(drop=True)
            avg_date.loc[:, 'year1'] = avg_date['year'].shift(1)
            avg_date = avg_date[1:5].reset_index(drop=True)

            result_key = []
            for d in range(len(avg_date)):
                rrr, _, _ = performance_analysis(data_avg_nav.reset_index(), start_date=avg_date['t_date'][d])
                result_key.append(rrr)

            result_key0, _, _ = performance_analysis(
                data_avg_nav.reset_index(), start_date=data_avg_nav.index.tolist()[-52]
            )

            result_specific = performance_specific_ret(data_avg_nav.reset_index())

            result_date = pd.DataFrame(
                {
                    '起始日期': None,
                    '最新日期': data_avg_nav.index.tolist()[-1]
                }, index=[0]
            ).T.reset_index()

            results_all = result_date.append(result_specific).append(result_key0)
            for i in result_key:
                results_all = results_all.append(i)

            results_all = results_all.rename(columns={0: '平均'})
            results_all['index'] = results_all['index'].apply(
                lambda x: '累计收益率' if '以来累计' in x else ('年化收益率' if '以来年化' in x else x)
            )
            input_data = input_data.append(results_all.set_index('index').T)
            if self.sort:
                input_data = input_data.sort_values(by=['本周', '上周', '最新日期', ], ascending=False)
            sht.range('B' + str(row_n + 1)).value = input_data
            sht.range((row_n, 5), (row_n, 2 + self.m1c)).api.Merge()
            sht.range((row_n, 5)).value = '收益'
            sht.range((row_n, 1), (row_n + 1 + len(input_data), 1)).api.Merge()
            sht.range((row_n, 1)).value = t.replace('（', '\n（')
            sht.range(
                (row_n, 1), (row_n + 1 + len(input_data), 2 + self.m1c + self.m2c * 2)
            ).api.Borders(8).LineStyle = 1
            sht.range(
                (row_n, 1),
                (row_n + 1 + len(input_data), 2 + self.m1c + self.m2c * (1 + self.key_years))
            ).api.Borders(8).Weight = self.xw_box_line_weight

            sht.range((row_n, 1), (row_n + 1 + len(input_data), 2)).api.HorizontalAlignment = -4108
            sht.range((row_n, 1), (row_n + 1 + len(input_data), 2)).api.VerticalAlignment = -4108

            sht.range(
                (row_n, 3),
                (row_n + 1, 2 + self.m1c + self.m2c * (1 + self.key_years))
            ).api.HorizontalAlignment = -4108
            sht.range(
                (row_n, 3),
                (row_n + 1, 2 + self.m1c + self.m2c * (1 + self.key_years))
            ).api.VerticalAlignment = -4108

            sht.range((row_n + 2, 3), (row_n + 2 + len(input_data), 3)).api.NumberFormat = "yyyy/mm"
            sht.range((row_n + 2, 4), (row_n + 2 + len(input_data), 4)).api.NumberFormat = "mm/dd"
            sht.range((row_n + 2, 5), (row_n + 2 + len(input_data), 2 + self.m1c)).api.NumberFormat = "0.00%"

            sht.range((row_n, 3 + self.m1c), (row_n, 2 + self.m1c + self.m2c)).api.Merge()
            sht.range((row_n, 3 + self.m1c)).value = '近一年'
            sht.range(
                (row_n, 3 + self.m1c), (row_n + 1 + len(input_data), 2 + self.m1c + self.m2c * 2)
            ).api.Borders(7).LineStyle = 2
            sht.range(
                (row_n, 3 + self.m1c), (row_n + 1 + len(input_data), 2 + self.m1c + self.m2c * 2)
            ).api.Borders(7).Weight = self.xw_box_line_weight
            sht.range(
                (row_n + 2, 3 + self.m1c),
                (row_n + 2 + len(input_data), 3 + self.m1c + self.m2c)
            ).api.NumberFormat = "0.00%"
            sht.range(
                (row_n + 2, 8 + self.m1c), (row_n + 2 + len(input_data), 12 + self.m1c)
            ).api.NumberFormat = "0.00"
            sht.range(
                (row_n + 2, 14 + self.m1c), (row_n + 2 + len(input_data), 14 + self.m1c)
            ).api.NumberFormat = "0.00"

            for y in range(self.key_years):
                sht.range(
                    (row_n, 3 + self.m1c + self.m2c * (1 + y)),
                    (row_n, 2 + self.m1c + self.m2c * (2 + y))
                ).api.Merge()
                sht.range((row_n, 3 + self.m1c + self.m2c * (1 + y))).value = input_data.columns[7 + y] + '以来'
                sht.range(
                    (row_n, 3 + self.m1c + self.m2c * (1 + y)),
                    (row_n + 1 + len(input_data), 2 + self.m1c + self.m2c * (2 + y))
                ).api.Borders(7).LineStyle = 2
                sht.range(
                    (row_n, 3 + self.m1c + self.m2c * (1 + y)),
                    (row_n + 1 + len(input_data), 2 + self.m1c + self.m2c * (2 + y))
                ).api.Borders(7).Weight = self.xw_box_line_weight
                sht.range(
                    (row_n + 2, 3 + self.m1c + self.m2c * (1 + y)),
                    (row_n + 2 + len(input_data), 2 + self.m1c + self.m2c * (1 + y + 1))
                ).api.NumberFormat = "0.00%"
                sht.range(
                    (row_n + 2, 3 + self.m1c + self.m2c * (1 + y) + 5),
                    (row_n + 2 + len(input_data), 2 + self.m1c + self.m2c * (1 + y + 1) - 2)
                ).api.NumberFormat = "0.00"
                sht.range(
                    (row_n + 2, 2 + self.m1c + self.m2c * (1 + y + 1)),
                    (row_n + 2 + len(input_data), 2 + self.m1c + self.m2c * (1 + y + 1))
                ).api.NumberFormat = "0.00"

            for i in range(len(input_data)):
                if bold_list is not None:
                    if input_data.index[i] in bold_list:
                        box = sht.range((row_n + 2 + i, 2))
                        box.api.Font.Color = 0x0000ff
                        box.api.Font.Bold = True
                if red_list is not None:
                    if input_data.index[i] in red_list:
                        box = sht.range((row_n + 2 + i, 2))
                        box.color = (192, 0, 0)

                if input_data.index[i] == '平均':
                    box = sht.range((row_n + 2 + i, 2))
                    box.api.Font.Bold = True
            row_n += (len(input_data) + 2)
        print('Sheet 0 done')

    @staticmethod
    def sheet_style1(sht, input_data, fund_dict, bold_list=None, red_list=None, skip_list=['多头']):
        sht.range('A2').value = input_data
        col_num = 2
        for i in fund_dict:
            if i in skip_list:
                continue
            sht.range((1, col_num)).value = i
            sht.range((1, col_num), (1, col_num + len(fund_dict[i]) - 1)).api.Merge()
            sht.range((1, col_num), (1, col_num + len(fund_dict[i]) - 1)).api.HorizontalAlignment = -4108
            sht.range((1, col_num), (1, col_num + len(fund_dict[i]) - 1)).api.VerticalAlignment = -4108
            sht.range((1, col_num), (99, col_num + len(fund_dict[i]) - 1)).api.Borders(10).LineStyle = 1
            sht.range((1, col_num), (99, col_num + len(fund_dict[i]) - 1)).api.Borders(7).LineStyle = 1
            col_num += len(fund_dict[i])

        for i in range(len(input_data.columns)):
            if bold_list is not None:
                if input_data.columns[i] in bold_list:
                    box = sht.range((2, 2 + i))
                    box.api.Font.Color = 0x0000ff
                    box.api.Font.Bold = True
            if red_list is not None:
                if input_data.columns[i] in red_list:
                    box = sht.range((2, 2 + i))
                    box.color = (192, 0, 0)
        print('Sheet 1 done')

    def load_index(self, table='stocks_index_ts'):
        index_data = pd.read_sql_query(
            'select t_date, close, code from ' + table
            + ' where code in ' + str(tuple(self.order_i.keys())),
            self.index_path
        ).pivot(
            index='t_date', columns='code', values='close'
        ).rename(
            columns=self.order_i
        ).reset_index()
        return index_data

    def fund_stats(self, fund_dict, month_list, fund_type):
        if fund_type.lower() == 'cta':
            output_file = self.output_path + 'CTA-' + self.end_date.strftime('%Y%m%d') + '.xlsx'
        elif fund_type.lower() == 'zx':
            output_file = self.output_path + '中性-' + self.end_date.strftime('%Y%m%d') + '.xlsx'
        elif fund_type.lower() == 'zz':
            output_file = self.output_path + '指增-' + self.end_date.strftime('%Y%m%d') + '.xlsx'
        else:
            raise ValueError('fund_type should be cta, zx or zz')

        fund_dict_i = {}
        order = []
        order_all = []
        for i in fund_dict:
            order += fund_dict[i]

        fund_list = pd.read_sql_query(
            'select * from fund_list where `name` in ' + str(tuple(set(order))), self.data_path
        )

        list_bold = fund_list[fund_list['leverage'] == 1]['name'].tolist()
        list_red = fund_list[fund_list['after_fee'] == 1]['name'].tolist()

        data_o = None
        data = update_performance(
            start_d=self.start_date,
            end_d=self.end_date,
            funds=order,
            db_path=self.data_path,
            cal_db_path=self.index_path,
            month_release=month_list
        )
        self.m1c = len(data['main']) - (1 + self.key_years) * self.m2c
        if fund_type.lower() == 'zz':
            order_all = order
            order = []
            for i in fund_dict:
                if i == '多头':
                    continue
                order += fund_dict[i]

            data_o = data
            data = update_performance(
                start_d=self.start_date,
                end_d=self.end_date,
                funds=order,
                db_path=self.data_path,
                cal_db_path=self.index_path,
                month_release=month_list,
                data_type='alpha'
            )

            index_data = self.load_index()

            nav_data = data_o['nav'].merge(index_data, on='t_date', how='left')

            index_data = nav_data[
                ['t_date', '沪深300', '中证500', '中证1000']
            ].copy().sort_values(by=['t_date']).reset_index(drop=True)

            index_key, _, _ = performance_analysis(index_data)

            index_key1, _, _ = performance_analysis(index_data, start_date=index_data['t_date'].tolist()[-52])

            index_specific = performance_specific_ret(index_data)

            index_date = pd.DataFrame(
                {
                    '起始日期': [None] * 3,
                    '最新日期': [index_data['t_date'].tolist()[-1]] * 3,
                }, index=['沪深300', '中证500', '中证1000']
            ).T.reset_index()
            index_all = index_date.append(index_specific).append(index_key1).append(index_key).reset_index(drop=True)
            index_all = index_all.set_index('index')

            data_o['main'] = data_o['main'].T.append(index_all.reset_index(drop=True).T).T
            data_o['nav'] = nav_data

            wb_zz = xl.Workbook(output_file)
            sheet1 = wb_zz.add_worksheet('超额总览')
            sheet1.set_zoom(zoom=85)
            sheet1.freeze_panes(1, 2)
            row_n = self.row_num
            for t in fund_dict:
                if t == '多头':
                    continue
                rowl = len(fund_dict[t]) + 1
                for i in range(3, 3 + self.m1c + (1 + self.key_years) * self.m2c - 1):
                    col = ten2twentysix(i)
                    if i in list(np.array([5, 7, 8, 17, 19, 20]) + self.m1c):
                        sheet1.conditional_format(col + str(row_n + 1) + ':' + col + str(row_n + rowl), cell_format_r)
                    else:
                        sheet1.conditional_format(col + str(row_n + 1) + ':' + col + str(row_n + rowl), cell_format)
                row_n += (len(fund_dict[t]) + 2 + 1)

            sheet12 = wb_zz.add_worksheet('原始总览')
            sheet12.set_zoom(zoom=85)
            sheet12.freeze_panes(1, 2)
            row_n = self.row_num
            for t in fund_dict:
                if '300' in t:
                    fund_dict_i[t] = fund_dict[t] + ['沪深300']
                elif '1000' in t:
                    fund_dict_i[t] = fund_dict[t] + ['中证1000']
                else:
                    if ('代销' in t) or ('FOF' in t) or ('多头' in t):
                        fund_dict_i[t] = fund_dict[t] + ['沪深300', '中证500', '中证1000']
                    else:
                        fund_dict_i[t] = fund_dict[t] + ['中证500']
                rowl = len(fund_dict_i[t]) + 1
                for i in range(3, 3 + self.m1c + (1 + self.key_years) * self.m2c - 1):
                    col = ten2twentysix(i)
                    if i in list(np.array([5, 7, 8, 17, 19, 20]) + self.m1c):
                        sheet12.conditional_format(col + str(row_n + 1) + ':' + col + str(row_n + rowl), cell_format_r)
                    else:
                        sheet12.conditional_format(col + str(row_n + 1) + ':' + col + str(row_n + rowl), cell_format)
                row_n += (len(fund_dict_i[t]) + 2 + 1)

            wb_zz.add_worksheet('20年始超额净值')
            wb_zz.add_worksheet('19年始超额净值')
            wb_zz.add_worksheet('原始净值')
            wb_zz.add_worksheet('超额净值')
            wb_zz.add_worksheet('原始动态回撤')
            wb_zz.add_worksheet('超额动态回撤')
            wb_zz.add_worksheet('月超额')
            wb_zz.add_worksheet('周超额')
            wb_zz.add_worksheet('周收益')
            wb_zz.close()

        else:
            wb = xl.Workbook(output_file)
            sheet1 = wb.add_worksheet('总览')
            sheet1.set_zoom(zoom=85)
            sheet1.freeze_panes(1, 2)
            row_n = self.row_num
            for t in fund_dict:
                rowl = len(fund_dict[t]) + 1
                for i in range(3, 3 + self.m1c + (1 + self.key_years) * self.m2c - 1):
                    col = ten2twentysix(i)
                    if i in list(np.array([5, 7, 8, 17, 19, 20]) + self.m1c):
                        sheet1.conditional_format(col + str(row_n + 1) + ':' + col + str(row_n + rowl), cell_format_r)
                    else:
                        sheet1.conditional_format(col + str(row_n + 1) + ':' + col + str(row_n + rowl), cell_format)
                row_n += (len(fund_dict[t]) + 2 + 1)

            wb.add_worksheet('20年始净值')
            wb.add_worksheet('19年始净值')
            wb.add_worksheet('原始净值')
            wb.add_worksheet('动态回撤')
            wb.add_worksheet('月收益')
            wb.add_worksheet('周收益')
            wb.close()

        xlsx = xw.Book(output_file)

        sht1 = xlsx.sheets('总览' if fund_type.lower() != 'zz' else '超额总览')
        sht1.range('B1').column_width = 24
        sht1.range('A1').row_height = 40
        sht1.range('B1').api.VerticalAlignment = -4108
        sht1.range(
            ten2twentysix(2 + self.m1c) + '1:' + ten2twentysix(1 + self.m1c + self.m2c * 2) + '1'
        ).column_width = 10
        sht1.range('B1').value = self.note_str[fund_type.lower()]

        self.sheet_style0(
            sht=sht1,
            input_main=data['main'],
            nav_data=data['nav'],
            type1=fund_type,
            fund_dict=fund_dict,
            bold_list=list_bold,
            red_list=list_red
        )

        sht2 = xlsx.sheets('20年始净值' if fund_type.lower() != 'zz' else '20年始超额净值')
        input_data = data['nav2020'].set_index('t_date')[order]
        self.sheet_style1(
            sht=sht2, input_data=input_data, fund_dict=fund_dict, bold_list=list_bold, red_list=list_red)

        sht3 = xlsx.sheets('19年始净值' if fund_type.lower() != 'zz' else '19年始超额净值')
        input_data = data['nav2019'].set_index('t_date')[order]
        self.sheet_style1(
            sht=sht3, input_data=input_data, fund_dict=fund_dict, bold_list=list_bold, red_list=list_red)

        sht4 = xlsx.sheets('原始净值' if fund_type.lower() != 'zz' else '超额净值')
        input_data = data['nav'].set_index('t_date')[order]
        self.sheet_style1(
            sht=sht4, input_data=input_data, fund_dict=fund_dict, bold_list=list_bold, red_list=list_red)

        sht5 = xlsx.sheets('动态回撤' if fund_type.lower() != 'zz' else '超额动态回撤')
        input_data = data['dd'].set_index('t_date')[order]
        self.sheet_style1(
            sht=sht5, input_data=input_data, fund_dict=fund_dict, bold_list=list_bold, red_list=list_red)

        sht6 = xlsx.sheets('周收益' if fund_type.lower() != 'zz' else '周超额')
        input_data = data['weekly_ret'].set_index('t_date')[order]
        self.sheet_style1(
            sht=sht6, input_data=input_data, fund_dict=fund_dict, bold_list=list_bold, red_list=list_red)

        sht7 = xlsx.sheets('月收益' if fund_type.lower() != 'zz' else '月超额')
        input_data = data['monthly_ret'].set_index('t_date')[order]
        self.sheet_style1(
            sht=sht7, input_data=input_data, fund_dict=fund_dict, bold_list=list_bold, red_list=list_red)

        if fund_type.lower() == 'zz':
            sht1.range('A1').value = '超额\n数据'
            sht1.range('A1').api.Font.Bold = True
            sht1.range('A1').api.Font.Size = 15
            sht1.range('A1').api.Font.Color = 0x0000ff

            sht12 = xlsx.sheets('原始总览')
            sht12.range('A1').value = '原始\n数据'
            sht12.range('A1').api.Font.Bold = True
            sht12.range('A1').api.Font.Size = 15
            sht12.range('A1').api.Font.Color = 0x0000ff

            sht12.range('B1').column_width = 24
            sht12.range('A1').row_height = 40
            sht12.range('B1').api.VerticalAlignment = -4108
            sht12.range(
                ten2twentysix(2 + self.m1c + 1) + '1:' + ten2twentysix(2 + self.m1c + self.m2c) + '1'
            ).column_width = 10
            sht12.range(
                ten2twentysix(2 + self.m1c + self.m2c + 1) + '1:' + ten2twentysix(2 + self.m1c + self.m2c * 2) + '1'
            ).column_width = 10
            sht12.range('B1').value = self.note_str[fund_type.lower()]
            self.sheet_style0(
                sht=sht12,
                input_main=data_o['main'],
                nav_data=data_o['nav'],
                type1=fund_type,
                fund_dict=fund_dict_i,
                bold_list=list_bold,
                red_list=list(self.order_i.values()),
                skip_list=[]
            )

            sht13 = xlsx.sheets('原始净值')
            input_data = data_o['nav'].set_index('t_date')[order_all + list(self.order_i.values())]
            self.sheet_style1(
                sht=sht13,
                input_data=input_data,
                fund_dict=fund_dict,
                bold_list=list_bold,
                red_list=list(self.order_i.values()),
                skip_list=[]
            )

            sht14 = xlsx.sheets('原始动态回撤')
            input_data = data_o['dd'].set_index('t_date')[order_all]
            self.sheet_style1(
                sht=sht14,
                input_data=input_data,
                fund_dict=fund_dict,
                bold_list=list_bold,
                red_list=list(self.order_i.values()),
                skip_list=[]
            )

            self.long_only_stats = data_o['main'][
                ['index'] + fund_dict['多头']
                ].set_index('index').T['本周'].sort_values(ascending=False)

            sht15 = xlsx.sheets('周收益')
            input_data = data_o['weekly_ret'].set_index('t_date')[order_all]
            self.sheet_style1(
                sht=sht15,
                input_data=input_data,
                fund_dict=fund_dict,
                bold_list=list_bold,
                red_list=list(self.order_i.values()),
                skip_list=[]
            )

        xlsx.save()
        xlsx.close()
        print(fund_type + ' done')

        if fund_type.lower() == 'cta':
            self.sum_cta = pool_board(
                data_df=data['main'][
                    ['index'] + list(
                        set(
                            fund_dict['长周期']
                            + fund_dict['长周期（高波动）']
                            + fund_dict['短周期']
                            + fund_dict['短周期（高波动）']
                            + fund_dict['混合']
                            + fund_dict['混合（高波动）']
                            + fund_dict['套利']
                            + fund_dict['截面']
                            + fund_dict['截面（高波动）']
                            + fund_dict['基本面']
                            + fund_dict['基本面（高波动）']
                            + fund_dict['主观']
                            # + cta_dict['转债']
                            # + cta_dict['FOF']
                            # + cta_dict['代销']
                        )
                    )
                    ],
                fund_list=fund_list
            )
        elif fund_type.lower() == 'zx':
            self.sum_zx = pool_board(
                data_df=data['main'][
                    ['index'] + list(
                        set(
                            fund_dict['高频']
                            + fund_dict['T0']
                            + fund_dict['中低频']
                            # + order_dict_zx['FOF']
                            # + order_dict_zx['代销']
                        )
                    )
                    ],
                fund_list=fund_list
            )
        elif fund_type.lower() == 'zz':
            self.sum_zz = pool_board(
                data_df=data['main'][
                    ['index'] + list(
                        set(
                            fund_dict['量价（500）']
                            + fund_dict['量价（300）']
                            + fund_dict['量价（1000）']
                            + fund_dict['机器学习']
                            + fund_dict['基本面']
                            # + fund_dict['FOF']
                            # + fund_dict['代销']
                            # + order_others
                        )
                    )
                    ],
                fund_list=fund_list
            )
            self.sum_zz_o = pool_board(
                data_df=data_o['main'][
                    ['index'] + list(
                        set(
                            fund_dict['量价（500）']
                            + fund_dict['量价（300）']
                            + fund_dict['量价（1000）']
                            + fund_dict['机器学习']
                            + fund_dict['基本面']
                            # + fund_dict['FOF']
                            # + fund_dict['代销']
                            # + order_others
                        )
                    )
                    ],
                fund_list=fund_list
            )

    def sum_info(self):
        if self.sum_cta is None or self.sum_zx is None or self.sum_zz is None or self.sum_zz_o is None:
            return
        summary_all = pd.DataFrame(
            self.sum_cta, index=[0]
        ).append(
            pd.DataFrame(
                self.sum_zx, index=[0]
            )
        ).append(
            pd.DataFrame(
                self.sum_zz, index=[0]
            )
        ).reset_index(drop=True)
        # summary_all.to_excel(self.output_path + '产品小计-' + self.end_date.strftime('%Y%m%d') + '.xlsx')
        print('产品小计 done')
        print(
            '''
            \nDear all,
            \n附件是量化产品跟踪表，净值更新截止至'''
            + self.end_date.strftime('%m/%d')
            + '''，产品净值走势图将另外更新在'''
            '''\n\tCTA：http://fdc.intelnal.howbuy.com/zeppelin/#/notebook/2G2Q7YJKV'''
            '''\n\t中性：http://fdc.intelnal.howbuy.com/zeppelin/#/notebook/2G75FWDDQ'''
            '''\n\t指增：http://fdc.intelnal.howbuy.com/zeppelin/#/notebook/2G5HM79V7'''
            '''\n\t指增α：http://fdc.intelnal.howbuy.com/zeppelin/#/notebook/2G5AB9NA2'''
            '''\n\t打开后若显示空白请点击Notebook->研究下其他文件，再点回跟踪产品净值可正常显示。'''
            '''\n\nCTA：'''
            '''\n\t上周(''' + self.end_date.strftime('%m/%d') + ''')产品'''
            + str(round(summary_all['win'][0] / summary_all['onTime'][0] * 10, 1))
            + '''成盈利，跟踪的'''
            + str(summary_all['all'][0])
            + '''个CTA产品中有'''
            + str(summary_all['all'][0] - summary_all['onTime'][0])
            + '''个未按时得到净值。'''
            '''\n\t已经得到净值数据的'''
            + str(summary_all['onTime'][0])
            + '''个产品中，盈利''' + str(summary_all['win'][0])
            + '''个，亏损''' + str(summary_all['onTime'][0] - summary_all['win'][0])
            + '''个。'''
            '''\n\t表现最好的是'''
            '''\n\t\t1. ''' + str(summary_all['bestName'][0])
            + '''（+''' + str(round(summary_all['bestRet'][0] * 100, 2))
            + '''%，''' + str(summary_all['bestType'][0])
            + '''）'''
            '''\n\t\t2. ''' + str(summary_all['bestName1'][0])
            + '''（+''' + str(round(summary_all['bestRet1'][0] * 100, 2))
            + '''%，''' + str(summary_all['bestType1'][0])
            + '''）'''
            '''\n\t\t3. ''' + str(summary_all['bestName2'][0])
            + '''（+''' + str(round(summary_all['bestRet2'][0] * 100, 2))
            + '''%，''' + str(summary_all['bestType2'][0])
            + '''）'''
            '''\n\t表现最差的是'''
            '''\n\t\t1. ''' + str(summary_all['worstName'][0])
            + '''（''' + str(round(summary_all['worstRet'][0] * 100, 2))
            + '''%，''' + str(summary_all['worstType'][0]) + '''）'''
            '''\n\t\t2. ''' + str(summary_all['worstName1'][0])
            + '''（''' + str(round(summary_all['worstRet1'][0] * 100, 2))
            + '''%，''' + str(summary_all['worstType1'][0]) + '''）'''
            '''\n\t\t3. ''' + str(summary_all['worstName2'][0])
            + '''（''' + str(round(summary_all['worstRet2'][0] * 100, 2))
            + '''%，''' + str(summary_all['worstType2'][0])
            + '''）\n\tCTA产品本周平均收益：'''
            + str(round(summary_all['average'][0] * 100, 2))
            + '''% \n\n中性：'''
            '''\n\t上周（'''+ self.end_date.strftime('%m/%d') + '''）产品'''
            + str(round(summary_all['win'][1] / summary_all['onTime'][1] * 10, 1))
            + '''成盈利，跟踪的'''
            + str(summary_all['all'][1])
            + '''个产品中有'''
            + str(summary_all['all'][1] - summary_all['onTime'][1])
            + '''个未按时得到净值。'''
            '''\n\t已经得到净值数据的''' + str(summary_all['onTime'][1])
            + '''个产品中，盈利''' + str(summary_all['win'][1])
            + '''个，亏损''' + str(summary_all['onTime'][1] - summary_all['win'][1])
            + '''个。'''
              '''\n\t表现最好的是'''
              '''\n\t\t1. ''' + str(summary_all['bestName'][1])
            + '''（+''' + str(round(summary_all['bestRet'][1] * 100, 2))
            + '''%，''' + str(summary_all['bestType'][1])
            + '''）'''
              '''\n\t\t2. ''' + str(summary_all['bestName1'][1])
            + '''（+''' + str(round(summary_all['bestRet1'][1] * 100, 2))
            + '''%，''' + str(summary_all['bestType1'][1])
            + '''）'''
              '''\n\t\t3. ''' + str(summary_all['bestName2'][1])
            + '''（+''' + str(round(summary_all['bestRet2'][1] * 100, 2))
            + '''%，''' + str(summary_all['bestType2'][1])
            + '''）'''
              '''\n\t最差的是'''
              '''\n\t\t1. ''' + str(summary_all['worstName'][1])
            + '''（''' + str(round(summary_all['worstRet'][1] * 100, 2))
            + '''%，''' + str(summary_all['worstType'][1])
            + '''）'''
              '''\n\t\t2. ''' + str(summary_all['worstName1'][1])
            + '''（''' + str(round(summary_all['worstRet1'][1] * 100, 2))
            + '''%，''' + str(summary_all['worstType1'][1])
            + '''）'''
              '''\n\t\t3. ''' + str(summary_all['worstName2'][1])
            + '''（''' + str(round(summary_all['worstRet2'][1] * 100, 2))
            + '''%，''' + str(summary_all['worstType2'][1])
            + '''）\n\t中性产品本周平均收益：'''
            + str(round(summary_all['average'][1] * 100, 2))
            + '''%\n\n指增:'''
              '''\n\t上周（''' + self.end_date.strftime('%m/%d')
            + '''）产品''' + str(round(summary_all['win'][2] / summary_all['onTime'][2] * 10, 1))
            + '''成跑赢指数，跟踪的''' + str(summary_all['all'][2])
            + '''个产品中有''' + str(summary_all['all'][2] - summary_all['onTime'][2])
            + '''个未按时得到净值。'''
              '''\n\t已经得到净值数据的''' + str(summary_all['onTime'][2])
            + '''个产品中，正超额''' + str(summary_all['win'][2])
            + '''个，负超额''' + str(summary_all['onTime'][2] - summary_all['win'][2])
            + '''个。'''
              '''\n\t表现最好的是'''
              '''\n\t\t1. ''' + str(summary_all['bestName'][2])
            + '''（超额+''' + str(round(summary_all['bestRet'][2] * 100, 2))
            + '''%，''' + str(summary_all['bestType'][2])
            + '''）'''
              '''\n\t\t2. ''' + str(summary_all['bestName1'][2])
            + '''（超额+''' + str(round(summary_all['bestRet1'][2] * 100, 2))
            + '''%，''' + str(summary_all['bestType1'][2])
            + '''）'''
              '''\n\t\t3. ''' + str(summary_all['bestName2'][2])
            + '''（超额+''' + str(round(summary_all['bestRet2'][2] * 100, 2))
            + '''%，''' + str(summary_all['bestType2'][2])
            + '''）'''
              '''\n\t最差的是'''
              '''\n\t\t1. ''' + str(summary_all['worstName'][2])
            + '''（超额''' + str(round(summary_all['worstRet'][2] * 100, 2))
            + '''%，''' + str(summary_all['worstType'][2])
            + '''）'''
              '''\n\t\t2. ''' + str(summary_all['worstName1'][2])
            + '''（超额''' + str(round(summary_all['worstRet1'][2] * 100, 2))
            + '''%，''' + str(summary_all['worstType1'][2])
            + '''）'''
              '''\n\t\t3. ''' + str(summary_all['worstName2'][2])
            + '''（超额''' + str(round(summary_all['worstRet2'][2] * 100, 2))
            + '''%，''' + str(summary_all['worstType2'][2])
            + '''）\n\t指增产品本周平均超额：'''
            + str(round(summary_all['average'][2] * 100, 2)) + '''%'''
        )
        r_dt = self.long_only_stats
        print(
            '''\n量化多头：'''
        )
        for i in range(len(r_dt)):
            print('\t' + r_dt.index[i] + '：' + str(round(r_dt[i] * 100, 2)) + '%')

    def avg_to_hb(self, sql_path, table, db, sql_ip, sql_user, sql_pass):
        sql_l = '''
        (
        id bigint not null AUTO_INCREMENT,
        t_date  date,
        type1  varchar(100),
        type2  varchar(100),
        nav float,
        primary key (id)
        )
        '''
        db = pymysql.connect(host=sql_ip, user=sql_user, password=sql_pass, database=db)
        cursor = db.cursor()

        sql = 'create table if not exists `' + table + '` ' + sql_l + ' comment=\'量化产品跟踪池\''
        cursor.execute(sql)
        print(table + ' generated')

        cursor.execute('truncate table ' + table)
        print('Clear ' + table)
        db.close()
        self.data_avg.to_sql(table, sql_path, if_exists='append', index=False)



