import multiprocessing

bind = "0.0.0.0:8080"
workers = multiprocessing.cpu_count() + 1  # not much IO in model prediction processing, so maintaining 1:1 process:cpu ratio, plus 1 for standby
timeout = 120  # Workers silent for more than this many seconds are killed and restarted
graceful_timeout = 120  # After receiving a restart signal, workers have this much time to finish serving requests
worker_class = 'uvicorn.workers.UvicornWorker'
worker_tmp_dir = "/mnt/mem"
daemon = True

capture_output = True
loglevel = 'info'
#errorlog = '-'

enable_stdio_inheritance = True


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")
