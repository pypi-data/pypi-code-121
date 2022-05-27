from datetime import datetime, timedelta

def cache(time_to_live=60 * 60 * 24):
    values = {}

    def wrapper(func):
        def deco(*args, **kwargs):
            kws = kwargs.items()
            key = tuple(args)+tuple(kws)
            value = values.get(key)
            if not value or value['expires'] < datetime.now():
                data = func(*args, **kwargs)
                value = {
                    'data': data,
                    'expires': datetime.now() + timedelta(seconds=time_to_live)
                }
                values[key] = value

            return value['data']

        return deco

    return wrapper