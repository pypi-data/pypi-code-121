linreg_method_cases_happy = {
    "column.linreg.alpha(column)": (
        lambda x, y: x.linreg.alpha(x),
        lambda x, y: f"linear_regression_alpha({x.get_sql()}, {x.get_sql()})",
    ),
    "column.linreg.beta(column)": (
        lambda x, y: x.linreg.beta(x),
        lambda x, y: f"linear_regression_beta({x.get_sql()}, {x.get_sql()})",
    ),
    "column.linreg.alpha_std_err(column)": (
        lambda x, y: x.linreg.alpha_std_err(x),
        lambda x, y: f"linear_regression_alpha_error({x.get_sql()}, {x.get_sql()})",
    ),
    "column.linreg.beta_std_err(column)": (
        lambda x, y: x.linreg.beta_std_err(x),
        lambda x, y: f"linear_regression_beta_error({x.get_sql()}, {x.get_sql()})",
    ),
}
