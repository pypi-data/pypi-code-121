finance_method_cases = {
    'window.finance.drawdown': (
        lambda w, x, y: w.finance.drawdown(x),
        lambda w, x, y: f"drawdown({x.get_sql()}) {w.get_sql()}"
    ),
    'window.finance.max_drawdown': (
        lambda w, x, y: w.finance.max_drawdown(x),
        lambda w, x, y: f"max_drawdown({x.get_sql()}) {w.get_sql()}"
    ),
    'window.finance.mean_drawdown': (
        lambda w, x, y: w.finance.mean_drawdown(x),
        lambda w, x, y: f"mean_drawdown({x.get_sql()}) {w.get_sql()}"
    ),
    'window.finance.drawdown_length': (
        lambda w, x, y: w.finance.drawdown_length(x),
        lambda w, x, y: f"drawdown_length({x.get_sql()}) {w.get_sql()}"
    ),
    'window.finance.max_drawdown_length': (
        lambda w, x, y: w.finance.max_drawdown_length(x),
        lambda w, x, y: f"max_drawdown_length({x.get_sql()}) {w.get_sql()}"
    ),
    'window.finance.mean_drawdown_length': (
        lambda w, x, y: w.finance.mean_drawdown_length(x),
        lambda w, x, y: f"mean_drawdown_length({x.get_sql()}) {w.get_sql()}"
    ),
    'window.finance.gain_loss_ratio': (
        lambda w, x, y: w.finance.gain_loss_ratio(x),
        lambda w, x, y: f"gain_loss_ratio({x.get_sql()}) {w.get_sql()}"
    ),
    'window.finance.semi_deviation': (
        lambda w, x, y: w.finance.semi_deviation(x),
        lambda w, x, y: f"semi_deviation({x.get_sql()}) {w.get_sql()}"
    ),
    'window.finance.information_ratio': (
        lambda w, x, y: w.finance.information_ratio(x, y),
        lambda w, x, y: f"mean_stdev_ratio({x.get_sql()} - ({y.get_sql()})) {w.get_sql()}"
    ),
    'window.finance.tracking_error': (
        lambda w, x, y: w.finance.tracking_error(x, y),
        lambda w, x, y: f"window_stdev({x.get_sql()} - ({y.get_sql()})) {w.get_sql()}"
    ),
    'window.finance.sharpe_ratio(column)': (
        lambda w, x, y: w.finance.sharpe_ratio(x, 0.01),
        lambda w, x, y: f"mean_stdev_ratio({x.get_sql()} - 0.01) {w.get_sql()}"
    ),
    'window.finance.gain_mean(column)': (
        lambda w, x, y: w.finance.gain_mean(x),
        lambda w, x, y: f"avg({x.get_sql()}) {w.filter(x >= 0).get_sql()}"
    ),
    'window.finance.loss_mean(column)': (
        lambda w, x, y: w.finance.loss_mean(x),
        lambda w, x, y: f"avg({x.get_sql()}) {w.filter(x < 0).get_sql()}"
    ),
    'window.finance.gain_stdev(column)': (
        lambda w, x, y: w.finance.gain_stdev(x),
        lambda w, x, y: f"window_stdev({x.get_sql()}) {w.filter(x >= 0).get_sql()}"
    ),
    'window.finance.loss_stdev(column)': (
        lambda w, x, y: w.finance.loss_stdev(x),
        lambda w, x, y: f"window_stdev({x.get_sql()}) {w.filter(x < 0).get_sql()}"
    ),
    'window.finance.downside_deviation(column, value)': (
        lambda w, x, y: w.finance.downside_deviation(x, 0.01),
        lambda w, x, y: f"window_stdev({x.get_sql()}) {w.filter(x < 0.01).get_sql()}"
    )
}
