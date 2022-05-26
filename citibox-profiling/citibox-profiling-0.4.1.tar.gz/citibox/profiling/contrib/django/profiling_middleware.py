import logging
import tracemalloc

from citibox.profiling import Profiling, GoogleConfig, ProfilerServiceGoogle

from django.conf import settings

logger = logging.getLogger(__name__)


class ProfilingMiddleware:
    _started = False
    CONFIG = settings.PROFILING

    def __init__(self, get_response):
        self.get_response = get_response
        self._url_fingerprint = ''

        if not self._started and self.CONFIG.get('ACTIVE', False):
            self._start_profiler()
            self._started = True

    def __call__(self, request):
        tracemalloc.start()
        response = self.get_response(request)
        current, peak = tracemalloc.get_traced_memory()
        current = current / 10 ** 6
        peak = peak / 10 ** 6
        logger.info(f'Current memory usage is {current}MB; Peak was {peak}MB', extra={
            'current_memory': current,
            'peak_memory': peak,
            'url_fingerprint': self._url_fingerprint,
        })
        tracemalloc.stop()
        return response

    def _start_profiler(self):
        profiling_config = GoogleConfig(
            service_name=self.CONFIG['SERVICE_NAME'],
            service_version=self.CONFIG['SERVICE_VERSION'],
            project_id=self.CONFIG['PROJECT_ID'],
            service_account_json_file=self.CONFIG['SERVICE_ACCOUNT_JSON_FILE'],
        )
        profiling = Profiling(profiler_service=ProfilerServiceGoogle(config=profiling_config))
        profiling.start()

    def process_view(self, request, view_func, view_args, view_kwargs):
        self._url_fingerprint = self._get_url_fingerprint(request.path, view_kwargs)

    def _get_url_fingerprint(self, req_url: str, params_values: dict):
        fingerprint = req_url
        for key, value in params_values.items():
            fingerprint = fingerprint.replace(value, f'{{{key}}}') if value else fingerprint

        return fingerprint
