__all__ = ('log',)

import os


def log(method):
    def wrapper(*args, **kwargs):
        if os.getenv('IS_ENABLE_API_LOG'):
            if method.__name__ == '__init__':
                print(f'INIT: {args[0]}')
            elif method.__name__ == '_get':
                print(f'GET SERVICE {args[0]}')
            elif method.__name__ == 'flush_cache':
                print(f'FLUSH CACHE {args[0]}')
        result = method(*args, **kwargs)
        return result

    return wrapper
