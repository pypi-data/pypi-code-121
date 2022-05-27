import pandas as pd
import numpy as np
from datetime import datetime
import hbshare as hbs
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from hbshare.fe.common.util.data_loader import get_trading_day_list
import statsmodels.api as sm
import plotly
import plotly.graph_objs as go
from plotly.offline import plot as plot_ly


class IndexPremium:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_pe_ttm where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        pe_data = data.set_index('trade_date')['ZZ500']

        sql_script = "SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE from funddb.ZSJY WHERE" \
                     " ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format('000905', self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data'])
        benchmark_df = data.set_index('TRADEDATE')['TCLOSE']

        df = pd.merge(pe_data.to_frame('pe_ttm'), benchmark_df.to_frame('index'), left_index=True, right_index=True)
        df['future_ret'] = df['index'].shift(-252) / df['index'] - 1
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency='week')
        df = df.reindex(trading_day_list).dropna()
        df['trade_date'] = df.index
        df['year'] = df['trade_date'].apply(lambda x: datetime.strptime(x, "%Y%m%d").year)
        self.market_df = df[['pe_ttm', 'future_ret', 'year']]

    def run(self):
        market_df = self.market_df

        # func = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
        # n = 5 * 52
        # rolling_pct = market_df['pe_ttm'].rolling(window=n, center=False, min_periods=n).apply(func)
        # market_df['pe_ttm'] = rolling_pct
        # market_df = market_df[market_df.index >= '20100101'].dropna()

        data = []
        for year in sorted(market_df['year'].unique()):
            period_df = market_df[market_df['year'] == year].sort_values(by='pe_ttm')
            trace = go.Scatter(
                x=period_df['pe_ttm'].tolist(),
                y=period_df['future_ret'],
                name='{}'.format(year),
                mode='markers'
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text="中证500估值 VS 持有一年收益（分年度）"),
            autosize=False, width=1200, height=800,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.1%'),
            xaxis=dict(showgrid=True),
            template='plotly_white'
        )

        # regression
        model = sm.OLS(market_df['future_ret'], sm.add_constant(market_df['pe_ttm'])).fit()
        const, beta = model.params[0], model.params[1]

        t = np.linspace(market_df['pe_ttm'].min(), market_df['pe_ttm'].max(), 100)

        trace0 = go.Scatter(
            x=t,
            y=const + beta * t,
            name="拟合线",
            mode='lines'
        )
        data.append(trace0)

        figure = go.Figure(data=data, layout=layout)
        plot_ly(figure, filename='D:\\123.html', auto_open=False)

#
#     date_list = df.index.tolist()
#     n = int(len(date_list) / 12)
#     tick_vals = [i for i in range(0, len(df), n)]
#     tick_text = [date_list[i] for i in range(0, len(df), n)]
#
#     layout = go.Layout(
#         title=dict(text="中证500估值和持有一年收益走势图"),
#         autosize=False, width=1200, height=600,
#         yaxis=dict(tickfont=dict(size=12), showgrid=False),
#         yaxis2=dict(tickfont=dict(size=12), tickformat=',.1%', overlaying='y', side="right"),
#         xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
#         legend=dict(orientation="h", x=0.4),
#         template='plotly_white')
#
#     figure = go.Figure(data=data, layout=layout)
#     plot_ly(figure, filename='D:\\123.html', auto_open=False)


if __name__ == '__main__':
    IndexPremium('20050101', '20220419').run()