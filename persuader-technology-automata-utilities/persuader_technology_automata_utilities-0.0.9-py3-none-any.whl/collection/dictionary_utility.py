def as_data(data, key, default=None):
    if key in data:
        return data[key]
    return default
