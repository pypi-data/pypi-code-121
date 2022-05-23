cume_method_cases_happy = {
    'column.cume.sum()': (
        lambda x, y: x.cume.sum(),
        lambda x, y: f"total({x.get_sql()}) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.cume.sum(order)': (
        lambda x, y: x.cume.sum(y.ascending()),
        lambda x, y: f"total({x.get_sql()}) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.cume.min()': (
        lambda x, y: x.cume.min(),
        lambda x, y: f"min({x.get_sql()}) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.cume.min(order)': (
        lambda x, y: x.cume.min(y.ascending()),
        lambda x, y: f"min({x.get_sql()}) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.cume.max()': (
        lambda x, y: x.cume.max(),
        lambda x, y: f"max({x.get_sql()}) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.cume.max(order)': (
        lambda x, y: x.cume.max(y.ascending()),
        lambda x, y: f"max({x.get_sql()}) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.cume.prod()': (
        lambda x, y: x.cume.prod(),
        lambda x, y: f"cumeprod({x.get_sql()}) OVER( ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.cume.prod(order)': (
        lambda x, y: x.cume.prod(y.ascending()),
        lambda x, y: f"cumeprod({x.get_sql()}) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
    'column.cume.dist()': (
        lambda x, y: x.cume.dist(),
        lambda x, y: f"CUME_DIST() OVER( ORDER BY {x.ascending().get_sql()} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW )"
    ),
}
