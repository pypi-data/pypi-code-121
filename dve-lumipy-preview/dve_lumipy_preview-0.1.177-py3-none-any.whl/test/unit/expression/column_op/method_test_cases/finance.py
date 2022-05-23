finance_method_cases_happy = {
    'column.finance.max_drawdown()': (
        lambda x, y: x.finance.max_drawdown(),
        lambda x, y: f"max_drawdown({x.get_sql()})"
    ),
    'column.finance.mean_drawdown()': (
        lambda x, y: x.finance.mean_drawdown(),
        lambda x, y: f"mean_drawdown({x.get_sql()})"
    ),
    'column.finance.max_drawdown_length()': (
        lambda x, y: x.finance.max_drawdown_length(),
        lambda x, y: f"max_drawdown_length({x.get_sql()})"
    ),
    'column.finance.mean_drawdown_length()': (
        lambda x, y: x.finance.mean_drawdown_length(),
        lambda x, y: f"mean_drawdown_length({x.get_sql()})"
    ),
    'column.finance.gain_loss_ratio()': (
        lambda x, y: x.finance.gain_loss_ratio(),
        lambda x, y: f"gain_loss_ratio({x.get_sql()})"
    ),
    'column.finance.semi_deviation()': (
        lambda x, y: x.finance.semi_deviation(),
        lambda x, y: f"semi_deviation({x.get_sql()})"
    ),
    'column.finance.information_ratio(other)': (
        lambda x, y: x.finance.information_ratio(y.dt.unixepoch()),
        lambda x, y: f"mean_stdev_ratio({x.get_sql()} - ({y.dt.unixepoch().get_sql()}))"
    ),
    'column.finance.tracking_error()': (
        lambda x, y: x.finance.tracking_error(y.dt.unixepoch()),
        lambda x, y: f"window_stdev({x.get_sql()} - ({y.dt.unixepoch().get_sql()}))"
    ),
    'column.finance.sharpe_ratio(value)': (
        lambda x, y: x.finance.sharpe_ratio(0.01),
        lambda x, y: f"mean_stdev_ratio({x.get_sql()} - 0.01)"
    ),
    'column.finance.sharpe_ratio(expr)': (
        lambda x, y: x.finance.sharpe_ratio(y.dt.unixepoch()),
        lambda x, y: f"mean_stdev_ratio({x.get_sql()} - ({y.dt.unixepoch().get_sql()}))"
    ),
    'column.finance.prices_to_returns()': (
        lambda x, y: x.finance.prices_to_returns(),
        lambda x, y: f"prices_to_returns({x.get_sql()}, 1, 1.0, 0) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.finance.prices_to_returns(interval)': (
        lambda x, y: x.finance.prices_to_returns(2),
        lambda x, y: f"prices_to_returns({x.get_sql()}, 2, 1.0, 0) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.finance.prices_to_returns(interval, time_factor)': (
        lambda x, y: x.finance.prices_to_returns(2, 12.0),
        lambda x, y: f"prices_to_returns({x.get_sql()}, 2, 12.0, 0) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.finance.prices_to_returns(interval, time_factor, compound)': (
        lambda x, y: x.finance.prices_to_returns(2, 12.0, True),
        lambda x, y: f"prices_to_returns({x.get_sql()}, 2, 12.0, 1) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.finance.returns_to_prices(initial)': (
        lambda x, y: x.finance.returns_to_prices(100.0),
        lambda x, y: f"returns_to_prices({x.get_sql()}, 100.0, 1.0, 0) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.finance.returns_to_prices(initial, time_factor)': (
        lambda x, y: x.finance.returns_to_prices(100.0, 12.0),
        lambda x, y: f"returns_to_prices({x.get_sql()}, 100.0, 12.0, 0) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.finance.returns_to_prices(interval, time_factor, compound)': (
        lambda x, y: x.finance.returns_to_prices(100.0, 12.0, True),
        lambda x, y: f"returns_to_prices({x.get_sql()}, 100.0, 12.0, 1) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
}

finance_method_cases_unhappy = {
    'column.finance.prices_to_returns(bad interval)': (
        lambda x, y: x.finance.prices_to_returns(0),
        ValueError,
        lambda x, y: f"Prices to returns interval must be an integer greater than zero - was 0."
    ),
    'column.finance.prices_to_returns(bad time factor)': (
        lambda x, y: x.finance.prices_to_returns(1, -1.0),
        ValueError,
        lambda x, y: f"Prices to returns time factor must be greater than zero - was -1.0."
    ),
    'column.finance.returns_to_prices(bad interval)': (
        lambda x, y: x.finance.returns_to_prices(0),
        ValueError,
        lambda x, y: f"Returns to prices start price must be greater than zero - was 0."
    ),
    'column.finance.returns_to_prices(bad time factor)': (
        lambda x, y: x.finance.returns_to_prices(1, -1.0),
        ValueError,
        lambda x, y: f"Prices to returns time factor must be greater than zero - was -1.0."
    ),
}
