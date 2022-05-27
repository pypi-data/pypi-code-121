"""
私募基金深度报告业绩分析模块
"""
import pandas as pd
import numpy as np
from datetime import datetime
import hbshare as hbs
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list
from Arbitrage_backtest import cal_annual_return, cal_annual_volatility, cal_sharpe_ratio, cal_max_drawdown
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go
import plotly.figure_factory as ff

plotly.offline.init_notebook_mode(connected=True)


class FundNavAnalysor:
    def __init__(self, start_date, end_date, benchmark_id, nav_series):
        self.start_date = start_date
        self.end_date = end_date
        self.benchmark_id = benchmark_id
        self.nav_series = nav_series
        self._load_data()

    def _load_data(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        # nav_series = self.nav_series.copy()
        nav_series = self.nav_series.reindex(trading_day_list).dropna()
        # nav_series = self.nav_series.reindex(trading_day_list).fillna(method='ffill').dropna()
        # benchmark
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        map_dict = {"000905": "中证500", "000300": "沪深300", "000852": "中证1000", "881001": "万得全A"}
        benchmark_name = map_dict[self.benchmark_id]
        data = pd.DataFrame(res['data']).rename(columns={"TCLOSE": benchmark_name}).set_index(
            'TRADEDATE')[[benchmark_name]]
        benchmark_df = data.reindex(nav_series.index)

        assert (nav_series.shape[0] == benchmark_df.shape[0])

        nav_df = pd.merge(nav_series, benchmark_df, left_index=True, right_index=True)
        return_df = nav_df.pct_change().fillna(0.)
        return_df['超额'] = return_df[return_df.columns[0]] - return_df[benchmark_name]
        # return_df['超额'] = return_df[return_df.columns[0]]

        self.nav_df = (1 + return_df).cumprod()
        self.return_df = return_df[1:]

    @staticmethod
    def plotly_line(df, title_text, sava_path, figsize=(1200, 500)):
        fig_width, fig_height = figsize
        data = []

        for col in df.columns[:2]:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines"
            )
            data.append(trace)

        for col in df.columns[2:]:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines",
                line=dict(color='darkgray', width=2, dash='dot')
            )
            data.append(trace)

        date_list = df.index.tolist()
        n = int(len(date_list) / 12)
        tick_vals = [i for i in range(0, len(df), n)]
        tick_text = [date_list[i] for i in range(0, len(df), n)]

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            # xaxis=dict(showgrid=True),
            xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
            legend=dict(orientation="h", x=0.35, y=1.1),
            template='simple_white',
            # paper_bgcolor='#edeeee',
            # plot_bgcolor='#edeeee',
        )
        fig = go.Figure(data=data, layout=layout)

        plot_ly(fig, filename=sava_path, auto_open=False)

    def run(self):
        nav_df = self.nav_df.copy()
        return_df = self.return_df.copy()
        # 净值指标
        performance_df = pd.DataFrame(
            index=nav_df.columns, columns=["累计收益", "年化收益率", "年化波动率", "最大回撤",
                                           "Sharpe比率", "Calmar比率", "投资胜率", "平均损益比"])
        performance_df.loc[:, "累计收益"] = nav_df.iloc[-1] - 1
        performance_df.loc[:, "年化收益率"] = return_df.apply(cal_annual_return, axis=0)
        performance_df.loc[:, '年化波动率'] = return_df.apply(cal_annual_volatility, axis=0)
        performance_df.loc[:, "最大回撤"] = nav_df.apply(cal_max_drawdown, axis=0)
        performance_df.loc[:, "Sharpe比率"] = return_df.apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
        performance_df['Calmar比率'] = performance_df['年化收益率'] / performance_df['最大回撤'].abs()
        performance_df.loc[:, "投资胜率"] = return_df.apply(lambda x: x.gt(0).sum() / len(x), axis=0)
        performance_df.loc[:, "平均损益比"] = return_df.apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
        # 格式处理
        performance_df['累计收益'] = performance_df['累计收益'].apply(lambda x: format(x, '.2%'))
        performance_df['年化收益率'] = performance_df['年化收益率'].apply(lambda x: format(x, '.2%'))
        performance_df['年化波动率'] = performance_df['年化波动率'].apply(lambda x: format(x, '.2%'))
        performance_df['最大回撤'] = performance_df['最大回撤'].apply(lambda x: format(x, '.2%'))
        performance_df['Sharpe比率'] = performance_df['Sharpe比率'].round(2)
        performance_df['Calmar比率'] = performance_df['Calmar比率'].round(2)
        performance_df['投资胜率'] = performance_df['投资胜率'].apply(lambda x: format(x, '.2%'))
        performance_df['平均损益比'] = performance_df['平均损益比'].round(2)
        # 分月度超额收益
        nav_df['trade_date'] = nav_df.index
        nav_df['trade_dt'] = nav_df['trade_date'].apply(lambda x: datetime.strptime(x, "%Y%m%d"))
        nav_df['month'] = nav_df['trade_dt'].apply(lambda x: x.month)
        nav_df['year'] = nav_df['trade_dt'].apply(lambda x: x.year)
        month_end = nav_df[nav_df['month'].shift(-1) != nav_df['month']]['trade_date'].tolist()

        month_excess = nav_df.reindex(month_end)['超额'].pct_change().dropna()
        month_excess = pd.merge(month_excess, nav_df[['month', 'year']], left_index=True, right_index=True)
        month_excess = pd.pivot_table(month_excess, index='year', columns='month', values='超额').sort_index()
        month_excess = month_excess.T.reindex(np.arange(1, 13)).sort_index().T
        month_excess.columns = [str(x) + '月' for x in month_excess.columns]
        month_excess['全年'] = (1 + month_excess.fillna(0.)).prod(axis=1) - 1
        for i in range(len(month_excess.index)):
            values = month_excess.iloc[i].values
            month_excess.iloc[i, :] = [format(x, '.2%') if x == x else x for x in values]
        # plot
        df = nav_df[nav_df.columns[:3]]
        self.plotly_line(df, "产品净值曲线", "D:\\量化产品跟踪\\深度报告相关\\净值曲线.html", figsize=(1200, 500))

        performance_df = performance_df.T
        performance_df.index.name = "指标名称"
        performance_df = performance_df.reset_index()
        fig = ff.create_table(performance_df)
        fig.layout.autosize = False
        fig.layout.width = 400
        fig.layout.height = 400

        plot_ly(fig, filename="D:\\量化产品跟踪\\深度报告相关\\收益指标统计.html", auto_open=False)

        month_excess.to_csv('D:\\量化产品跟踪\\深度报告相关\\月度超额收益.csv', encoding="gbk")


if __name__ == '__main__':
    nv_series = get_fund_nav_from_sql('20211231', '20220311', {"白鹭精选量化鲲鹏十号": "SQB109"})
    # nv_series = pd.read_excel("C:\\Users\\kai.zhang\\Desktop\\FACTSHEET 基准比较 - 副本.xlsx", sheet_name=0, index_col=0)
    # nv_series['trade_date'] = nv_series.index
    # nv_series['trade_date'] = nv_series['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    # nv_series = nv_series.set_index('trade_date')['量派睿核十号']

    # nv_series = pd.read_excel('D:\\研究基地\\D-量价类\\翰荣\\翰荣指数增强策略净值分析2022.04.08.xlsx', sheet_name=0, header=1)
    # nv_series['日期'] = nv_series['日期'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    # nv_series = nv_series.set_index('日期')['策略净值']

    # nv_series = pd.read_excel("D:\\研究基地\\B-套利类\\展弘\\量化套利一号\\量化套利1号修正图.xlsx", sheet_name=0, index_col=0)
    # nv_series['trade_date'] = nv_series.index
    # nv_series['trade_date'] = nv_series['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    # nv_series.rename(columns={"修正净值": "量化套利1号-修正"}, inplace=True)
    # nv_series = nv_series.set_index('trade_date')['量化套利1号-修正'].dropna()

    # nv_series1 = get_fund_nav_from_sql('20200306', '20211231', {"白鹭alpha": "SJM897"})
    # return_series1 = nv_series1.pct_change().fillna(0.)
    # nv_series2 = get_fund_nav_from_sql('20211231', '20220318', {"白鹭alpha": "SQB109"})
    # return_series2 = nv_series2.pct_change().dropna()
    # return_series = pd.concat([return_series1, return_series2], axis=0).sort_index()
    # nv_series = (1 + return_series).cumprod()

    # nv_series = pd.read_excel(
    #     "D:\\研究基地\\L-From_路遥\\1-跟踪代销\\天演\\净值文件\\天演资本代表产品净值20220106.xlsx", sheet_name="300指增", header=1, index_col=0)
    # nv_series['trade_date'] = nv_series.index
    # nv_series['trade_date'] = nv_series['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    # nv_series.rename(columns={"复权净值": "天演300指增"}, inplace=True)
    # nv_series = nv_series.set_index('trade_date')['天演300指增']
    # FundNavAnalysor('20191231', '20211231', '000300', nv_series).run()

    # nv_series = get_fund_nav_from_sql('20210420', '20220429', {"白鹭精选量化鲲鹏十号": "SQB109"})
    # nv_series = get_fund_nav_from_sql('20210420', '20220429', {"伯兄建康": "SQT564"})
    # nv_series = get_fund_nav_from_sql('20200424', '20220325', {"泰铼联泰1号": "SJH121"})

    # 启林1000指增
    # nv_series1 = get_fund_nav_from_sql('20201023', '20211008', {"启林1000指增": "SJT863"})
    # nv_series2 = get_fund_nav_from_sql('20211008', '20220513', {"启林1000指增": "SSU078"})
    # nv_series2 = nv_series2 * nv_series1.loc['20211008']
    # nv_series = pd.concat([nv_series1, nv_series2[1:]])

    nv_series = get_fund_nav_from_sql('20201231', '20220513', {"幻方": "SNA691"})

    FundNavAnalysor('20201231', '20220513', '000905', nv_series).run()