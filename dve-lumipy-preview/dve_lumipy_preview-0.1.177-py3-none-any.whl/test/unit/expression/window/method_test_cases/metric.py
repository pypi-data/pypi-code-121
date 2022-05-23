metric_method_cases = {
    'window.metric.mean_squared_error': (
        lambda w, x, y: w.metric.mean_squared_error(x, y),
        lambda w, x, y: f"mean_squared_error({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.mean_absolute_error': (
        lambda w, x, y: w.metric.mean_absolute_error(x, y),
        lambda w, x, y: f"mean_absolute_error({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.mean_fractional_absolute_error': (
        lambda w, x, y: w.metric.mean_fractional_absolute_error(x, y),
        lambda w, x, y: f"mean_fractional_absolute_error({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.minkowski_distance': (
        lambda w, x, y: w.metric.minkowski_distance(x, y, 3),
        lambda w, x, y: f"minkowski_distance({x.get_sql()}, {y.get_sql()}, 3) {w.get_sql()}"
    ),
    'window.metric.chebyshev_distance': (
        lambda w, x, y: w.metric.chebyshev_distance(x, y),
        lambda w, x, y: f"chebyshev_distance({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.manhattan_distance': (
        lambda w, x, y: w.metric.manhattan_distance(x, y),
        lambda w, x, y: f"manhattan_distance({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.euclidean_distance': (
        lambda w, x, y: w.metric.euclidean_distance(x, y),
        lambda w, x, y: f"euclidean_distance({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.canberra_distance': (
        lambda w, x, y: w.metric.canberra_distance(x, y),
        lambda w, x, y: f"canberra_distance({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.braycurtis_distance': (
        lambda w, x, y: w.metric.braycurtis_distance(x, y),
        lambda w, x, y: f"braycurtis_distance({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.cosine_distance': (
        lambda w, x, y: w.metric.cosine_distance(x, y),
        lambda w, x, y: f"cosine_distance({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.metric.precision_score': (
        lambda w, x, y: w.metric.precision_score(x.cast(bool), y.cast(bool)),
        lambda w, x, y: f"precision_score({x.cast(bool).get_sql()}, {y.cast(bool).get_sql()}) {w.get_sql()}"
    ),
    'window.metric.recall_score': (
        lambda w, x, y: w.metric.recall_score(x.cast(bool), y.cast(bool)),
        lambda w, x, y: f"recall_score({x.cast(bool).get_sql()}, {y.cast(bool).get_sql()}) {w.get_sql()}"
    ),
    'window.metric.f_score(default beta)': (
        lambda w, x, y: w.metric.f_score(x.cast(bool), y.cast(bool)),
        lambda w, x, y: f"fbeta_score({x.cast(bool).get_sql()}, {y.cast(bool).get_sql()}, 1.0) {w.get_sql()}"
    ),
    'window.metric.f_score': (
        lambda w, x, y: w.metric.f_score(x.cast(bool), y.cast(bool), 2.0),
        lambda w, x, y: f"fbeta_score({x.cast(bool).get_sql()}, {y.cast(bool).get_sql()}, 2.0) {w.get_sql()}"
    ),
}
