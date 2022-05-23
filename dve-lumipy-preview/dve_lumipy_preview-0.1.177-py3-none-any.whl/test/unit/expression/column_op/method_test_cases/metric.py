metric_method_cases_happy = {
    'column.metric.mean_squared_error(column)': (
        lambda x, y: x.metric.mean_squared_error(x),
        lambda x, y: f"mean_squared_error({x.get_sql()}, {x.get_sql()})"
    ),
    'column.metric.mean_absolute_error(column)': (
        lambda x, y: x.metric.mean_absolute_error(x),
        lambda x, y: f"mean_absolute_error({x.get_sql()}, {x.get_sql()})"
    ),
    'column.metric.mean_fractional_error(column)': (
        lambda x, y: x.metric.mean_fractional_absolute_error(x),
        lambda x, y: f"mean_fractional_absolute_error({x.get_sql()}, {x.get_sql()})"
    ),
    'column.metric.minkowski_distance(column, 3.0)': (
        lambda x, y: x.metric.minkowski_distance(x, 3.0),
        lambda x, y: f"minkowski_distance({x.get_sql()}, {x.get_sql()}, 3.0)"
    ),
    'column.metric.minkowski_distance(column, 5)': (
        lambda x, y: x.metric.minkowski_distance(x, 5),
        lambda x, y: f"minkowski_distance({x.get_sql()}, {x.get_sql()}, 5)"
    ),
    'column.metric.chebyshev_distance(column)': (
        lambda x, y: x.metric.chebyshev_distance(x),
        lambda x, y: f"chebyshev_distance({x.get_sql()}, {x.get_sql()})"
    ),
    'column.metric.manhattan_distance(column)': (
        lambda x, y: x.metric.manhattan_distance(x),
        lambda x, y: f"manhattan_distance({x.get_sql()}, {x.get_sql()})"
    ),
    'column.metric.euclidean_distance(column)': (
        lambda x, y: x.metric.euclidean_distance(x),
        lambda x, y: f"euclidean_distance({x.get_sql()}, {x.get_sql()})"
    ),
    'column.metric.canberra_distance(column)': (
        lambda x, y: x.metric.canberra_distance(x),
        lambda x, y: f"canberra_distance({x.get_sql()}, {x.get_sql()})"
    ),
    'column.metric.braycurtis_distance(column)': (
        lambda x, y: x.metric.braycurtis_distance(x),
        lambda x, y: f"braycurtis_distance({x.get_sql()}, {x.get_sql()})"
    ),
    'column.metric.cosine_distance(column)': (
        lambda x, y: x.metric.cosine_distance(x),
        lambda x, y: f"cosine_distance({x.get_sql()}, {x.get_sql()})"
    ),
    'bool_column.metric.precision_score(bool_column)': (
        lambda x, y: x.cast(bool).metric.precision_score(x.cast(bool)),
        lambda x, y: f"precision_score({x.cast(bool).get_sql()}, {x.cast(bool).get_sql()})"
    ),
    'bool_column.metric.recall_score(bool_column)': (
        lambda x, y: x.cast(bool).metric.recall_score(x.cast(bool)),
        lambda x, y: f"recall_score({x.cast(bool).get_sql()}, {x.cast(bool).get_sql()})"
    ),
    'bool_column.metric.fscore_score(bool_column, 0.5)': (
        lambda x, y: x.cast(bool).metric.f_score(x.cast(bool), 0.5),
        lambda x, y: f"fbeta_score({x.cast(bool).get_sql()}, {x.cast(bool).get_sql()}, 0.5)"
    ),
    'int_column.metric.precision_score(int_column)': (
        lambda x, y: x.cast(int).metric.precision_score(x.cast(int)),
        lambda x, y: f"precision_score({x.cast(int).get_sql()}, {x.cast(int).get_sql()})"
    ),
    'int_column.metric.recall_score(int_column)': (
        lambda x, y: x.cast(int).metric.recall_score(x.cast(int)),
        lambda x, y: f"recall_score({x.cast(int).get_sql()}, {x.cast(int).get_sql()})"
    ),
    'int_column.metric.fscore_score(int_column, 0.5)': (
        lambda x, y: x.cast(int).metric.f_score(x.cast(int), 0.5),
        lambda x, y: f"fbeta_score({x.cast(int).get_sql()}, {x.cast(int).get_sql()}, 0.5)"
    ),
}
