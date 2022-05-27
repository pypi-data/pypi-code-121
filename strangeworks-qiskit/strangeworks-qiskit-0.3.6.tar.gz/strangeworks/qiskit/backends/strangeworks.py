from qiskit import assemble
from qiskit.providers import BackendV1 as Backend
from qiskit.providers.models.backendstatus import BackendStatus
from qiskit.providers.models.backendproperties import BackendProperties
from qiskit.qobj import QasmQobj, PulseQobj

from strangeworks.qiskit.backends._utils import get_account_slug
from strangeworks.qiskit.jobs.strangeworksjob import StrangeworksJob

from typing import Any, Dict

import warnings, copy


class StrangeworksBackend(Backend):
    def __init__(
        self, configuration, provider, name, client, remote, account_details, **fields
    ):
        super().__init__(configuration, provider=provider, **fields)
        self._name = name
        self._client = client
        self._remote = remote
        self.account_details = account_details

    def run(self, circuits, **kwargs):
        # these types require assembly before being able to send to the cloud
        if not isinstance(circuits, (QasmQobj, PulseQobj)):
            circuits = assemble(circuits, self, **self.__get_run_config(**kwargs))

        backend_and_job_fields = kwargs
        backend_and_job_fields.update(self.account_details)
        job = StrangeworksJob(
            self, None, circuits, self._remote, **backend_and_job_fields
        )
        job.submit()
        return job

    def __get_run_config(self, **kwargs: Any) -> Dict:
        """Return the consolidated runtime configuration."""
        run_config_dict = copy.copy(self.options.__dict__)
        for key, val in kwargs.items():
            if val is not None:
                run_config_dict[key] = val
                if (
                    key not in self.options.__dict__
                    and not self.configuration().simulator
                ):
                    warnings.warn(
                        f"{key} is not available in backend options and may be ignored by this backend",  # type: ignore[unreachable]
                        stacklevel=4,
                    )
        return run_config_dict

    def name(self):
        return self._name

    def __repr__(self):
        return self.name()

    def __str__(self):
        return self.name()

    def status(self):
        backend = self.name()
        account_slug = get_account_slug(backend)
        status = self._client.fetch_backend_status(account_slug, backend)
        return BackendStatus.from_dict(status)

    def properties(self):
        backend = self.name()
        account_slug = get_account_slug(backend)
        properties = self._client.fetch_backend_properties(account_slug, backend)
        if properties:
            return BackendProperties.from_dict(properties)
        return None

    def is_remote(self):
        return self._remote
