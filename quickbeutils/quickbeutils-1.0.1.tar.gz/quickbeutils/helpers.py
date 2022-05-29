from quickbelog import Log
CONFIG_EMPTY_VALUES = [None, 'NONE', '']


def verify_config(conf: dict):
    is_ok = True
    for k, v in conf.items():
        v = str(v).strip().upper()
        if v in CONFIG_EMPTY_VALUES:
            Log.error(f'Please configure {k} environment variable.')
            is_ok = False

    if not is_ok:
        raise ValueError('Configuration is missing, please check previous log errors.')
