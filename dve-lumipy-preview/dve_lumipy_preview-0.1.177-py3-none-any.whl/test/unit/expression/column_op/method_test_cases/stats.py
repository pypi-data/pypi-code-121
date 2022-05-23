stats_method_cases_happy = {
    'column.stats.covariance(other)': (
        lambda x, y: x.stats.covariance(y.dt.unixepoch()),
        lambda x, y: f"covariance({x.get_sql()}, {y.dt.unixepoch().get_sql()}, 1)"
    ),
    'column.stats.covariance(other, ddof)': (
        lambda x, y: x.stats.covariance(y.dt.unixepoch(), 0),
        lambda x, y: f"covariance({x.get_sql()}, {y.dt.unixepoch().get_sql()}, 0)"
    ),
    'column.stats.empirical(value)': (
        lambda x, y: x.stats.empirical_cdf(1.23),
        lambda x, y: f"empirical_cume_dist_function({x.get_sql()}, 1.23)"
    ),
    'column.stats.pearson_r(other)': (
        lambda x, y: x.stats.pearson_r(y.dt.unixepoch()),
        lambda x, y: f"pearson_correlation({x.get_sql()}, {y.dt.unixepoch().get_sql()})"
    ),
    'column.stats.spearman_r(other)': (
        lambda x, y: x.stats.spearman_r(y.dt.unixepoch()),
        lambda x, y: f"spearman_rank_correlation({x.get_sql()}, {y.dt.unixepoch().get_sql()})"
    ),
    'column.stats.median_abs_deviation()': (
        lambda x, y: x.stats.median_abs_deviation(),
        lambda x, y: f"median_absolute_deviation({x.get_sql()})"
    ),
    'column.stats.skewness()': (
        lambda x, y: x.stats.skewness(),
        lambda x, y: f"skewness({x.get_sql()})"
    ),
    'column.stats.kurtosis()': (
        lambda x, y: x.stats.kurtosis(),
        lambda x, y: f"kurtosis({x.get_sql()})"
    ),
    'column.stats.root_mean_square()': (
        lambda x, y: x.stats.root_mean_square(),
        lambda x, y: f"root_mean_square({x.get_sql()})"
    ),
    'column.stats.harmonic_mean()': (
        lambda x, y: x.stats.harmonic_mean(),
        lambda x, y: f"harmonic_mean({x.get_sql()})"
    ),
    'column.stats.geometric_mean()': (
        lambda x, y: x.stats.geometric_mean(),
        lambda x, y: f"geometric_mean({x.get_sql()})"
    ),
    'column.stats.geometric_stdev()': (
        lambda x, y: x.stats.geometric_stdev(),
        lambda x, y: f"exp(window_stdev(log({x.get_sql()})))"
    ),
    'column.stats.entropy()': (
        lambda x, y: x.stats.entropy(),
        lambda x, y: f"entropy({x.get_sql()})"
    ),
    'column.stats.interquartile_range()': (
        lambda x, y: x.stats.interquartile_range(),
        lambda x, y: f"interquartile_range({x.get_sql()})"
    ),
    'column.stats.interquantile_range(value1, value2)': (
        lambda x, y: x.stats.interquantile_range(0.1, 0.9),
        lambda x, y: f"interquantile_range({x.get_sql()}, 0.1, 0.9)"
    ),
    'column.stats.coef_of_variation()': (
        lambda x, y: x.stats.coef_of_variation(),
        lambda x, y: f"coefficient_of_variation({x.get_sql()})"
    ),
    'column.stats.mean_stdev_ratio()': (
        lambda x, y: x.stats.mean_stdev_ratio(),
        lambda x, y: f"mean_stdev_ratio({x.get_sql()})"
    ),
    'column.stats.median()': (
        lambda x, y: x.stats.median(),
        lambda x, y: f"quantile({x.get_sql()}, 0.5)"
    ),
    'column.stats.lower_quartile()': (
        lambda x, y: x.stats.lower_quartile(),
        lambda x, y: f"quantile({x.get_sql()}, 0.25)"
    ),
    'column.stats.upper_quartile()': (
        lambda x, y: x.stats.upper_quartile(),
        lambda x, y: f"quantile({x.get_sql()}, 0.75)"
    ),
    'column.stats.quantile(value)': (
        lambda x, y: x.stats.quantile(0.1),
        lambda x, y: f"quantile({x.get_sql()}, 0.1)"
    ),
    'column.stats.stdev()': (
        lambda x, y: x.stats.stdev(),
        lambda x, y: f"window_stdev({x.get_sql()})"
    ),
}

stats_method_cases_unhappy = {
    'column.stats.interquantile_range(bad interval)': (
        lambda x, y: x.stats.interquantile_range(0.9, 0.1),
        ValueError,
        lambda x, y: "Upper quantile must be greater than lower quantile (Was upper = 0.1, lower = 0.9)"
    ),
    'column.stats.interquantile_range(bad lower)': (
        lambda x, y: x.stats.interquantile_range(-1.0, 0.1),
        ValueError,
        lambda x, y: "Lower quantile is only defined between 0 and 1. Was -1.0"
    ),
    'column.stats.interquantile_range(bad upper)': (
        lambda x, y: x.stats.interquantile_range(0.9, 2.0),
        ValueError,
        lambda x, y: "Upper quantile is only defined between 0 and 1. Was 2.0"
    ),
}
