main_method_cases = {
    'window.first': (
        lambda w, x, y: w.first(x),
        lambda w, x, y: f'FIRST_VALUE({x.get_sql()}) {w.get_sql()}'
    ),
    'window.last': (
        lambda w, x, y: w.last(x),
        lambda w, x, y: f'LAST_VALUE({x.get_sql()}) {w.get_sql()}'
    ),
    'window.lag': (
        lambda w, x, y: w.lag(x, 1, None),
        lambda w, x, y: f"LAG({x.get_sql()}, 1, null) {w.get_sql()}"
    ),
    'window.lead': (
        lambda w, x, y: w.lead(x, 1, None),
        lambda w, x, y: f"LEAD({x.get_sql()}, 1, null) {w.get_sql()}"
    ),
    'window.nth_value': (
        lambda w, x, y: w.nth_value(x, 3),
        lambda w, x, y: f"NTH_VALUE({x.get_sql()}, 3) {w.get_sql()}"
    ),
    'window.mean': (
        lambda w, x, y: w.mean(x),
        lambda w, x, y: f'avg({x.get_sql()}) {w.get_sql()}'
    ),
    'window.count': (
        lambda w, x, y: w.count(x),
        lambda w, x, y: f'count({x.get_sql()}) {w.get_sql()}'
    ),
    'window.min': (
        lambda w, x, y: w.min(x),
        lambda w, x, y: f'min({x.get_sql()}) {w.get_sql()}'
    ),
    'window.max': (
        lambda w, x, y: w.max(x),
        lambda w, x, y: f'max({x.get_sql()}) {w.get_sql()}'
    ),
    'window.sum': (
        lambda w, x, y: w.sum(x),
        lambda w, x, y: f'total({x.get_sql()}) {w.get_sql()}'
    ),
    'window.cume_dist': (
        lambda w, x, y: w.cume_dist(),
        lambda w, x, y: f'CUME_DIST() {w.get_sql()}'
    ),
    'window.dense_rank': (
        lambda w, x, y: w.dense_rank(),
        lambda w, x, y: f'DENSE_RANK() {w.get_sql()}'
    ),
    'window.ntile': (
        lambda w, x, y: w.ntile(3),
        lambda w, x, y: f'NTILE(3) {w.get_sql()}'
    ),
    'window.rank': (
        lambda w, x, y: w.rank(),
        lambda w, x, y: f'RANK() {w.get_sql()}'
    ),
    'window.row_number': (
        lambda w, x, y: w.row_number(),
        lambda w, x, y: f'ROW_NUMBER() {w.get_sql()}'
    ),
    'window.percent_rank': (
        lambda w, x, y: w.percent_rank(),
        lambda w, x, y: f'PERCENT_RANK() {w.get_sql()}'
    ),
    'window.prod': (
        lambda w, x, y: w.prod(x),
        lambda w, x, y: f'cumeprod({x.get_sql()}) {w.get_sql()}'
    ),
}