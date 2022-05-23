
main_method_cases_happy = {
    'column.sum': (
        lambda x, y: x.sum(),
        lambda x, y: f"total({x.get_sql()})"
    ),
    'column.count': (
        lambda x, y: x.count(),
        lambda x, y: f"count({x.get_sql()})"
    ),
    'column.mean': (
        lambda x, y: x.mean(),
        lambda x, y: f"avg({x.get_sql()})"
    ),
    'column.min': (
        lambda x, y: x.min(),
        lambda x, y: f"min({x.get_sql()})"
    ),
    'column.max': (
        lambda x, y: x.max(),
        lambda x, y: f"max({x.get_sql()})"
    ),
    'column.cast(float)': (
        lambda x, y: x.cast(float),
        lambda x, y: f"cast({x.get_sql()} AS DOUBLE)"
    ),
    'column.cast(int)': (
        lambda x, y: x.cast(int),
        lambda x, y: f"cast({x.get_sql()} AS INT)"
    ),
    'column.cast(str)': (
        lambda x, y: x.cast(str),
        lambda x, y: f"cast({x.get_sql()} AS TEXT)"
    ),
    'column.cast(bool)': (
        lambda x, y: x.cast(bool),
        lambda x, y: f"cast({x.get_sql()} AS BOOLEAN)"
    ),
    'column.exp': (
        lambda x, y: x.exp(),
        lambda x, y: f"exp({x.get_sql()})"
    ),
    'column.log': (
        lambda x, y: x.log(),
        lambda x, y: f"log({x.get_sql()})"
    ),
    'column.log10': (
        lambda x, y: x.log10(),
        lambda x, y: f"log10({x.get_sql()})"
    ),
    'column.ceil': (
        lambda x, y: x.ceil(),
        lambda x, y: f"ceil({x.get_sql()})"
    ),
    'column.floor': (
        lambda x, y: x.floor(),
        lambda x, y: f"floor({x.get_sql()})"
    ),
    'column.abs': (
        lambda x, y: x.abs(),
        lambda x, y: f"abs({x.get_sql()})"
    ),
    'column.round': (
        lambda x, y: x.round(),
        lambda x, y: f"round({x.get_sql()}, 0)"
    ),
    'column.round(3)': (
        lambda x, y: x.round(3),
        lambda x, y: f"round({x.get_sql()}, 3)"
    ),
    'column.sign': (
        lambda x, y: x.sign(),
        lambda x, y: f"sign({x.get_sql()})"
    ),

    'column.is_null': (
        lambda x, y: x.is_null(),
        lambda x, y: f"{x.get_sql()} IS NULL"
    ),
    'column.is_not_null': (
        lambda x, y: x.is_not_null(),
        lambda x, y: f"{x.get_sql()} IS NOT NULL"
    ),
    'column.is_in(list)': (
        lambda x, y: x.is_in([1, 2, 3]),
        lambda x, y: f"{x.get_sql()} IN (1, 2, 3)"
    ),
    'column.is_in(*args)': (
        lambda x, y: x.is_in(1, 2, 3),
        lambda x, y: f"{x.get_sql()} IN (1, 2, 3)"
    ),
    'column.is_in(tuple)': (
        lambda x, y: x.is_in((1, 2, 3)),
        lambda x, y: f"{x.get_sql()} IN (1, 2, 3)"
    ),
    'column.is_in(set)': (
        lambda x, y: x.is_in({1, 2, 3}),
        lambda x, y: f"{x.get_sql()} IN (1, 2, 3)"
    ),
    'column.not_in(list)': (
        lambda x, y: x.not_in([1, 2, 3]),
        lambda x, y: f"{x.get_sql()} NOT IN (1, 2, 3)"
    ),
    'column.not_in(*args)': (
        lambda x, y: x.not_in(1, 2, 3),
        lambda x, y: f"{x.get_sql()} NOT IN (1, 2, 3)"
    ),
    'column.not_in(tuple)': (
        lambda x, y: x.not_in((1, 2, 3)),
        lambda x, y: f"{x.get_sql()} NOT IN (1, 2, 3)"
    ),
    'column.not_in(set)': (
        lambda x, y: x.not_in({1, 2, 3}),
        lambda x, y: f"{x.get_sql()} NOT IN (1, 2, 3)"
    ),
    'column.between(value, value)': (
        lambda x, y: x.between(0, 1),
        lambda x, y: f"{x.get_sql()} BETWEEN 0 AND 1"
    ),
    'column.not_between(value, value)': (
        lambda x, y: x.not_between(0, 1),
        lambda x, y: f"{x.get_sql()} NOT BETWEEN 0 AND 1"
    ),
    'column.coalesce(expr, 42)': (
        lambda x, y: x.coalesce(y.cast(float), 42.0),
        lambda x, y: f"coalesce({x.get_sql()}, {y.cast(float).get_sql()}, 42.0)"
    ),

    'column.diff()': (
        lambda x, y: x.diff(),
        lambda x, y: f"{x.get_sql()} - LAG({x.get_sql()}, 1, null) OVER( ROWS BETWEEN 1 PRECEDING AND CURRENT ROW )"
    ),
    'column.diff(sort)': (
        lambda x, y: x.diff(y.ascending()),
        lambda x,
               y: f"{x.get_sql()} - LAG({x.get_sql()}, 1, null) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN 1 PRECEDING AND CURRENT ROW )"
    ),
    'column.diff(sort, offset)': (
        lambda x, y: x.diff(y.ascending(), 3),
        lambda x,
               y: f"{x.get_sql()} - LAG({x.get_sql()}, 3, null) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN 3 PRECEDING AND CURRENT ROW )"
    ),
    'column.frac_diff()': (
        lambda x, y: x.frac_diff(),
        lambda x,
               y: f"({x.get_sql()} - LAG({x.get_sql()}, 1, null) OVER( ROWS BETWEEN 1 PRECEDING AND CURRENT ROW )) / (cast(LAG({x.get_sql()}, 1, null) OVER( ROWS BETWEEN 1 PRECEDING AND CURRENT ROW ) AS DOUBLE))"
    ),
    'column.frac_diff(sort)': (
        lambda x, y: x.frac_diff(y.ascending()),
        lambda x,
               y: f"({x.get_sql()} - LAG({x.get_sql()}, 1, null) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN 1 PRECEDING AND CURRENT ROW )) / (cast(LAG({x.get_sql()}, 1, null) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN 1 PRECEDING AND CURRENT ROW ) AS DOUBLE))"
    ),
    'column.frac_diff(sort, offset)': (
        lambda x, y: x.frac_diff(y.ascending(), 3),
        lambda x,
               y: f"({x.get_sql()} - LAG({x.get_sql()}, 3, null) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN 3 PRECEDING AND CURRENT ROW )) / (cast(LAG({x.get_sql()}, 3, null) OVER( ORDER BY {y.ascending().get_sql()} ROWS BETWEEN 3 PRECEDING AND CURRENT ROW ) AS DOUBLE))"
    ),
    'column.prod()': (
        lambda x, y: x.prod(),
        lambda x, y: f"cumeprod({x.get_sql()})"
    )
}

main_method_cases_unhappy = {
    'column.is_in()': (
        lambda x, y: x.is_in(),
        ValueError,
        lambda x, y: "The input to is_in was empty. This method expects a collection of values as *args, or a single collection object such as a list or a tuple."
    ),
    'column.not_in()': (
        lambda x, y: x.not_in(),
        ValueError,
        lambda x, y: "The input to not_in was empty. This method expects a collection of values as *args, or a single collection object such as a list or a tuple."
    ),
    'column.between(bad interval)': (
        lambda x, y: x.between(1, 0),
        ValueError,
        lambda x, y: 'Invalid interval given to BETWEEN. Upper limit must be greater than the lower limit.'
    ),
    'column.not_between(bad interval)': (
        lambda x, y: x.not_between(1, 0),
        ValueError,
        lambda x, y: 'Invalid interval given to NOT BETWEEN. Upper limit must be greater than the lower limit.'
    ),
    'column.diff(not an ordering)': (
        lambda x, y: x.diff(y),
        TypeError,
        lambda x, y: f"All arguments to the WindowOrder must be orderings. Try calling ascending() on the column"
    ),
    'column.frac_dist(not an ordering)': (
        lambda x, y: x.frac_diff(y),
        TypeError,
        lambda x, y: f"All arguments to the WindowOrder must be orderings. Try calling ascending() on the column"
    ),
    'column.coalesce(no args)': (
        lambda x, y: x.coalesce(),
        ValueError,
        lambda x, y: f"Coalesce expression must be given at least two values! Received 1."
    ),
    'column.cast(not a type)': (
        lambda x, y: x.cast(42),
        TypeError,
        lambda x, y: "Invalid input to cast: 42. Supported inputs are the types int, bool, str, float."
    ),
    'column.cast(bad type)': (
        lambda x, y: x.cast(list),
        TypeError,
        lambda x, y: "Invalid input to cast: <class 'list'>. Supported inputs are the types int, bool, str, float."
    ),
}
