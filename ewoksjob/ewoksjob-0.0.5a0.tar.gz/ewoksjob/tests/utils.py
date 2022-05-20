import os


def has_redis_server():
    with os.popen("redis-server --version") as output:
        return bool(output.read())


def get_result(future, **kwargs):
    if hasattr(future, "get"):
        return future.get(**kwargs)
    else:
        return future.result(**kwargs)
