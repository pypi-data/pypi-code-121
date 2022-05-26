from .profiler_service import ProfilerService


class Profiling:

    def __init__(self, profiler_service: ProfilerService):
        self._profiler_service = profiler_service

    def start(self):
        self._profiler_service.start()


class ErrorStartingProfiling(Exception):
    pass
