from dataclasses import dataclass

import googlecloudprofiler

from citibox.profiling import ErrorStartingProfiling
from citibox.profiling import ProfilerService
from citibox.profiling.config import Config


@dataclass
class GoogleConfig(Config):
    project_id: str
    service_account_json_file: str = None
    verbose: int = 3


class ProfilerServiceGoogle(ProfilerService):

    def __init__(self, config: GoogleConfig):
        assert isinstance(config, GoogleConfig), "The ProfilerServiceGoogle need Google config type"
        super().__init__(config=config)

    def start(self) -> None:
        super().start()

        try:
            googlecloudprofiler.start(
                service=self._config.service_name,
                verbose=self._config.verbose,
                service_version=self._config.service_version,
                project_id=self._config.project_id,
                service_account_json_file=self._config.service_account_json_file,
            )
        except (ValueError, NotImplementedError) as exc:
            self._started = False
            raise ErrorStartingProfiling(exc)
        except Exception:
            self._started = False
            raise
