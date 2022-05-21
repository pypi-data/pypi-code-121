from multiprocessing import cpu_count
from jwtserver.functions.config import load_config

config = load_config().server


def max_workers():
    return cpu_count()


bind = f'{config.host}:{config.port}'
max_requests = 1000
worker_class = 'uvicorn.workers.UvicornWorker'
workers = max_workers()
threads = max_workers() * 2
reload = True
name = 'troll'
