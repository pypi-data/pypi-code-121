import pandas as pd

table_style = [
    dict(selector="tr:hover", props=[("background", "#D6EEEE")]),
    dict(
        selector="th",
        props=[
            ("color", "#fff"),
            ("border", "1px solid #eee"),
            ("padding", "12px 35px"),
            ("border-collapse", "collapse"),
            ("background", "#1D4477"),
            ("font-size", "18px"),
        ],
    ),
    dict(
        selector="td",
        props=[
            ("border", "1px solid #eee"),
            ("padding", "10px 20px"),
            ("border-collapse", "collapse"),
            ("font-size", "15px"),
        ],
    ),
    dict(
        selector="table",
        props=[
            ("font-family", "Helvetica"),
            ("margin", "25px auto"),
            ("border-collapse", "collapse"),
            ("border", "1px solid #eee"),
            ("border-bottom", "2px solid #00cccc"),
        ],
    ),
    dict(selector="caption", props=[("caption-side", "bottom")]),
    dict(
        selector="tr:nth-child(even)",
        props=[
            ("background-color", "#f2f2f2"),
        ],
    ),
]


def color_accounting(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, green otherwise.
    """
    color = "red" if val < 0 else "green"
    return "color: %s" % color


def generate_table(
    df: pd.DataFrame, precision: int = None, accounting_col_columns: list = None
):
    if accounting_col_columns:
        res = df.style.applymap(
            color_accounting, subset=accounting_col_columns
        ).set_table_styles(table_style)
    else:
        res = df.style.set_table_styles(table_style)

    if precision:
        res = res.format(precision=2)
    return res.to_html()
