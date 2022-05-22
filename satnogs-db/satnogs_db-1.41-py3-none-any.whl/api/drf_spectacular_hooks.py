"""SatNOGS DB API hooks for drf-spectcular"""

EXCLUDED_PATHS = [
    '/api/satellites/{satellite_entry__norad_cat_id}/',
]


def exclude_paths_hook(endpoints):
    """ Excluding paths that are defined in EXCLUDED_PATHS list """
    return [
        (path, path_regex, method, callback) for path, path_regex, method, callback in endpoints
        if path not in EXCLUDED_PATHS
    ]
