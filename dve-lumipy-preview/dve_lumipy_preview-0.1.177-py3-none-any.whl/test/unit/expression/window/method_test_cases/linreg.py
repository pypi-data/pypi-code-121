linreg_method_cases = {
    'window.linreg.alpha': (
        lambda w, x, y: w.linreg.alpha(x, y),
        lambda w, x, y: f"linear_regression_alpha({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.linreg.beta': (
        lambda w, x, y: w.linreg.beta(x, y),
        lambda w, x, y: f"linear_regression_beta({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.linreg.alpha_std_err': (
        lambda w, x, y: w.linreg.alpha_std_err(x, y),
        lambda w, x, y: f"linear_regression_alpha_error({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.linreg.beta_std_err': (
        lambda w, x, y: w.linreg.beta_std_err(x, y),
        lambda w, x, y: f"linear_regression_beta_error({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
}