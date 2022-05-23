stats_method_cases = {
    'window.stats.covariance': (
        lambda w, x, y: w.stats.covariance(x, y, 1),
        lambda w, x, y: f"covariance({x.get_sql()}, {y.get_sql()}, 1) {w.get_sql()}"
    ),
    'window.stats.empirical_cdf': (
        lambda w, x, y: w.stats.empirical_cdf(x, 1),
        lambda w, x, y: f"empirical_cume_dist_function({x.get_sql()}, 1) {w.get_sql()}"
    ),
    'window.stats.pearson_r': (
        lambda w, x, y: w.stats.pearson_r(x, y),
        lambda w, x, y: f"pearson_correlation({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.spearman_r': (
        lambda w, x, y: w.stats.spearman_r(x, y),
        lambda w, x, y: f"spearman_rank_correlation({x.get_sql()}, {y.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.median_abs_deviation': (
        lambda w, x, y: w.stats.median_abs_deviation(x),
        lambda w, x, y: f"median_absolute_deviation({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.skewness': (
        lambda w, x, y: w.stats.skewness(x),
        lambda w, x, y: f"skewness({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.kurtosis': (
        lambda w, x, y: w.stats.kurtosis(x),
        lambda w, x, y: f"kurtosis({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.root_mean_square': (
        lambda w, x, y: w.stats.root_mean_square(x),
        lambda w, x, y: f"root_mean_square({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.harmonic_mean': (
        lambda w, x, y: w.stats.harmonic_mean(x),
        lambda w, x, y: f"harmonic_mean({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.geometric_mean': (
        lambda w, x, y: w.stats.geometric_mean(x),
        lambda w, x, y: f"geometric_mean({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.geometric_stdev': (
        lambda w, x, y: w.stats.geometric_stdev(x),
        lambda w, x, y: f"exp(window_stdev(log({x.get_sql()})) {w.get_sql()})"
    ),
    'window.stats.entropy': (
        lambda w, x, y: w.stats.entropy(x),
        lambda w, x, y: f"entropy({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.interquartile_range': (
        lambda w, x, y: w.stats.interquartile_range(x),
        lambda w, x, y: f"interquartile_range({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.interquantile_range': (
        lambda w, x, y: w.stats.interquantile_range(x, 0.1, 0.9),
        lambda w, x, y: f"interquantile_range({x.get_sql()}, 0.1, 0.9) {w.get_sql()}"
    ),
    'window.stats.coef_of_variation': (
        lambda w, x, y: w.stats.coef_of_variation(x),
        lambda w, x, y: f"coefficient_of_variation({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.mean_stdev_ratio': (
        lambda w, x, y: w.stats.mean_stdev_ratio(x),
        lambda w, x, y: f"mean_stdev_ratio({x.get_sql()}) {w.get_sql()}"
    ),
    'window.stats.median': (
        lambda w, x, y: w.stats.median(x),
        lambda w, x, y: f"quantile({x.get_sql()}, 0.5) {w.get_sql()}"
    ),
    'window.stats.lower_quartile': (
        lambda w, x, y: w.stats.lower_quartile(x),
        lambda w, x, y: f"quantile({x.get_sql()}, 0.25) {w.get_sql()}"
    ),
    'window.stats.upper_quartile': (
        lambda w, x, y: w.stats.upper_quartile(x),
        lambda w, x, y: f"quantile({x.get_sql()}, 0.75) {w.get_sql()}"
    ),
    'window.stats.quantile': (
        lambda w, x, y: w.stats.quantile(x, 0.9),
        lambda w, x, y: f"quantile({x.get_sql()}, 0.9) {w.get_sql()}"
    ),
    'window.stats.stdev': (
        lambda w, x, y: w.stats.stdev(x),
        lambda w, x, y: f"window_stdev({x.get_sql()}) {w.get_sql()}"
    ),
}