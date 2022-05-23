from typing import Optional, Dict, Union, Iterable

import yfinance as yf
from lumipy.provider import BaseProvider, ColumnMeta, ParamMeta
from lumipy.query.expression.sql_value_type import SqlValType


class YFinanceProvider(BaseProvider):
    """Provider that extracts historical price data from yahoo finance using the yfinance package.

    """

    def __init__(self):

        columns = [
            ColumnMeta('Date', SqlValType.DateTime, 'The date'),
            ColumnMeta('Open', SqlValType.Double, 'Opening price'),
            ColumnMeta('High', SqlValType.Double, 'High price'),
            ColumnMeta('Low', SqlValType.Double, 'Log price'),
            ColumnMeta('Close', SqlValType.Double, 'Closing price'),
            ColumnMeta('Volume', SqlValType.Double, 'Daily volume'),
            ColumnMeta('Dividends', SqlValType.Double, 'Dividend payment on the date.'),
            ColumnMeta('StockSplits', SqlValType.Double, 'Stock split factor on the date'),
        ]
        params = [
            ParamMeta('Ticker', SqlValType.Text, 'The ticker to get data for.'),
            ParamMeta('Range', SqlValType.Text, 'How far back to get data for.', 'max'),
        ]

        super().__init__(
            'Test.YFinance.PriceHistory',
            columns,
            params,
            description='Price data from Yahoo finance for a given ticker'
        )

    def _get_data(
            self,
            data_filter: Optional[Dict[str, object]],
            limit: Union[int, None],
            **params
    ) -> Iterable[Dict[str, Union[str, int, float]]]:

        ticker = params.get('Ticker', None)
        period = params.get('Range', self.parameters['Range'].default_value)
        if ticker is not None:
            df = yf.Ticker(ticker).history(period=period).reset_index()
        else:
            raise ValueError('No ticker supplied!')

        df.columns = [c.replace(' ', '') for c in df.columns]

        return map(lambda x: x[1].to_dict(), df.iterrows())
