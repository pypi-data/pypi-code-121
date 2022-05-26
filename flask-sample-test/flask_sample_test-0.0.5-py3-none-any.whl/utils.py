from functools import wraps

from flask_sample_test.sample_test import SampleEnvironment


def with_env(env: SampleEnvironment):

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with env:
                func(*args, **kwargs)
        return wrapper
    return decorate
