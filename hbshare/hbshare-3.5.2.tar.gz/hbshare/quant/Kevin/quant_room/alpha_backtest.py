"""
alpha标的超额回测模块
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os
import hbshare as hbs
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_trading_day_list
from Arbitrage_backtest import cal_annual_return, cal_annual_volatility, cal_sharpe_ratio, cal_max_drawdown
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
plt.style.use('seaborn')


class AlphaBacktest:
    def __init__(self, data_path, start_date, end_date, mode="ratio"):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.mode = mode
        self._load_data()

    def _load_data(self):
        data_with_header = pd.read_excel(
            os.path.join(self.data_path, r"指增-{}.xlsx".format(self.end_date)), sheet_name='原始净值')
        data = pd.read_excel(
            os.path.join(self.data_path, "指增-{}.xlsx".format(self.end_date)), sheet_name='原始净值', header=1)
        data['t_date'] = data['t_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        data.index = data['t_date']
        cols = data_with_header.columns.tolist()

        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")

        data_param = []
        type_list = [x for x in cols if not x.startswith('Unnamed')]
        for i in range(len(type_list) - 1):
            if type_list[i] in ['量价（500）', '机器学习', '基本面']:
                s_index, e_index = cols.index(type_list[i]), cols.index(type_list[i + 1])
                data_slice = data[data.columns[s_index: e_index]]
                data_slice = data_slice[data_slice.index >= self.start_date].reindex(trading_day_list)
                data_param.append(data_slice)
            else:
                pass

        self.nav_data = pd.concat(data_param, axis=1).dropna(how='all', axis=0).sort_index()

    def run(self):
        nav_df = self.nav_data.copy()

        nav_df['trade_date'] = nav_df.index
        nav_df['month'] = nav_df['trade_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d').month)
        nav_df['next_month'] = nav_df['month'].shift(-1).fillna(0.).astype(int)
        nav_df.loc[nav_df['month'] != nav_df['next_month'], 'isMonthEnd'] = 1
        month_list = nav_df[nav_df['isMonthEnd'] == 1].index.tolist()
        cols = [x for x in nav_df.columns if x not in ['trade_date', 'month', 'next_month', 'isMonthEnd']]

        ret_df = []
        for i in range(6, len(month_list) - 1, 3):
            if i + 3 > len(month_list) - 1:
                start_date, pre_date, t_date, future_date = month_list[i - 6], month_list[i - 3], \
                                                            month_list[i], month_list[-1]
            else:
                start_date, pre_date, t_date, future_date = month_list[i - 6], month_list[i - 3], \
                                                            month_list[i], month_list[i + 3]
            period_df = nav_df.loc[start_date: future_date, cols].dropna(how='any', axis=1)
            quarter_ret = period_df.loc[[start_date, pre_date, t_date, future_date]].pct_change().dropna().T

            quantile_df = quarter_ret.rank() / quarter_ret.shape[0]
            # 剔除连续两个季度处于前25%分位的管理人
            selected_df = quantile_df[(quantile_df[pre_date] < 0.75) | (quantile_df[t_date] < 0.75)]

            # print(t_date, period_df.shape[1], selected_df.shape[0])

            # 前一个季度超额排名前50%
            selected_df = selected_df[selected_df[t_date] >= 0.50]
            # selected_df = selected_df.sort_values(by=t_date, ascending=False)[:10]
            tmp = period_df.loc[t_date: future_date] / period_df.loc[t_date]
            port_ret = tmp[selected_df.index].mean(axis=1).pct_change().dropna()
            # 对照组1
            group1 = quarter_ret[quarter_ret[t_date] < quarter_ret[t_date].quantile(0.5)]
            group1_ret = tmp[group1.index].mean(axis=1).pct_change().dropna()
            # 对照组2
            group2 = quarter_ret[quarter_ret[t_date] >= quarter_ret[t_date].quantile(0.5)]
            group2_ret = tmp[group2.index].mean(axis=1).pct_change().dropna()
            # 对照组3
            group3_ret = tmp.mean(axis=1).pct_change().dropna()

            period_ret = port_ret.to_frame('port').merge(
                group1_ret.to_frame('group1'), left_index=True, right_index=True).merge(
                group2_ret.to_frame('group2'), left_index=True, right_index=True).merge(
                group3_ret.to_frame('group3'), left_index=True, right_index=True)

            ret_df.append(period_ret)

        ret_df = pd.concat(ret_df).sort_index()

        # 中证500
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format('000905', nav_df.index[0], nav_df.index[-1])
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(columns={"TCLOSE": "benchmark"}).set_index(
            'TRADEDATE')['benchmark']
        benchmark_ret = data.reindex(nav_df.index).pct_change().dropna().reindex(ret_df.index)

        excess_return = ret_df.sub(benchmark_ret.squeeze(), axis=0)

        (1 + excess_return).cumprod().plot.line(title="excess return compare line")

        excess_nav = (1 + excess_return).cumprod()
        performance_df = pd.DataFrame(
            index=excess_nav.columns, columns=["累计超额", "超额年化", "超额年化波动", "最大回撤",
                                               "Sharpe比率", "Calmar比率", "投资胜率", "平均损益比"])
        performance_df.loc[:, "累计超额"] = excess_nav.iloc[-1] - 1
        performance_df.loc[:, "超额年化"] = excess_return.apply(cal_annual_return, axis=0)
        performance_df.loc[:, '超额年化波动'] = excess_return.apply(cal_annual_volatility, axis=0)
        performance_df.loc[:, "最大回撤"] = excess_nav.apply(cal_max_drawdown, axis=0)
        performance_df.loc[:, "Sharpe比率"] = excess_return.apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
        performance_df['Calmar比率'] = performance_df['超额年化'] / performance_df['最大回撤'].abs()
        performance_df.loc[:, "投资胜率"] = excess_return.apply(lambda x: x.gt(0).sum() / len(x), axis=0)
        performance_df.loc[:, "平均损益比"] = excess_return.apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
        # 格式处理
        performance_df['累计超额'] = performance_df['累计超额'].apply(lambda x: format(x, '.2%'))
        performance_df['超额年化'] = performance_df['超额年化'].apply(lambda x: format(x, '.2%'))
        performance_df['超额年化波动'] = performance_df['超额年化波动'].apply(lambda x: format(x, '.2%'))
        performance_df['最大回撤'] = performance_df['最大回撤'].apply(lambda x: format(x, '.2%'))
        performance_df['Sharpe比率'] = performance_df['Sharpe比率'].round(2)
        performance_df['Calmar比率'] = performance_df['Calmar比率'].round(2)
        performance_df['投资胜率'] = performance_df['投资胜率'].apply(lambda x: format(x, '.2%'))
        performance_df['平均损益比'] = performance_df['平均损益比'].round(2)

        performance_df = performance_df.T
        performance_df.index.name = "指标名称"
        performance_df = performance_df.reset_index()
        fig = ff.create_table(performance_df)
        fig.layout.autosize = False
        fig.layout.width = 400
        fig.layout.height = 400

        plot_ly(fig, filename="D:\\123.html", auto_open=False)

        tmp = excess_nav['group2'].to_frame("超额")
        tmp['trade_date'] = tmp.index
        tmp['trade_dt'] = tmp['trade_date'].apply(lambda x: datetime.strptime(x, "%Y%m%d"))
        tmp['month'] = tmp['trade_dt'].apply(lambda x: x.month)
        tmp['year'] = tmp['trade_dt'].apply(lambda x: x.year)
        month_end = tmp[tmp['month'].shift(-1) != tmp['month']]['trade_date'].tolist()

        month_excess = tmp.reindex(month_end)['超额'].pct_change().dropna()
        month_excess = pd.merge(month_excess, tmp[['month', 'year']], left_index=True, right_index=True)
        month_excess = pd.pivot_table(month_excess, index='year', columns='month', values='超额').sort_index()
        month_excess = month_excess.T.reindex(np.arange(1, 13)).sort_index().T
        month_excess.columns = [str(x) + '月' for x in month_excess.columns]
        month_excess['全年'] = (1 + month_excess.fillna(0.)).prod(axis=1) - 1
        for i in range(len(month_excess.index)):
            values = month_excess.iloc[i].values
            month_excess.iloc[i, :] = [format(x, '.2%') if x == x else x for x in values]

        month_excess.to_csv('D:\\456.csv', encoding="gbk")


if __name__ == '__main__':
    AlphaBacktest("D:\\量化产品跟踪\\指数增强", '20180620', '20220318').run()