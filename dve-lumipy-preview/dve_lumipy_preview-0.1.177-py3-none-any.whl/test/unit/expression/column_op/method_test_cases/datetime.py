datetime_method_cases_happy = {
    'column.dt.strfitime(expr, %Y-%M-%D)': (
        lambda x, y: y.dt.strftime('%Y-%M-%D'),
        lambda x, y: f"strftime('%Y-%M-%D', {y.get_sql()})"
    ),
    'column.dt.unixepoch()': (
        lambda x, y: y.dt.unixepoch(),
        lambda x, y: f"strftime('%s', {y.get_sql()})"
    ),
}

datetime_method_cases_unhappy = {

}
