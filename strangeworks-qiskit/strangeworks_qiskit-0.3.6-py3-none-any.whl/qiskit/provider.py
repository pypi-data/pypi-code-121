from qiskit import Aer
from qiskit.providers import ProviderV1 as Provider
from qiskit.providers.providerutils import filter_backends
from qiskit.providers.models import BackendConfiguration
import strangeworks

from strangeworks.qiskit.runtimes import StrangeworksRuntimeService
from strangeworks.qiskit._runtime_client import RuntimeClient
from strangeworks.qiskit._hw_api import SWClient
from strangeworks.qiskit.backends import backend_resolution


class StrangeworksProvider(Provider):
    """The Strangeworks Provider allows access to Strangeworks backends and runtime
    wrappers for the Qiskit IBMQ Runtime services"""

    def __init__(self):
        self._sw = SWClient(strangeworks.client)

        self._runtime = StrangeworksRuntimeService(
            provider=self, runtime_client=RuntimeClient(strangeworks.client)
        )
        self._backends = None

    def backends(self, name=None, filters=None, **kwargs):
        if not self._backends:
            self._backends = self._discover_backends()

        backends = self._backends
        if name:
            backends = [b for b in backends if b.name() == name]

        return filter_backends(backends, filters, **kwargs)

    def _discover_backends(self):
        backends = []
        response = self._sw.get_backends()
        for res in response:
            account_slug = res.get("account_id", "")
            account_details = res.get("account_details", {})
            bs = res.get("backends", [])
            for c in bs:
                sw_name = c.get("sw_name", "")
                configuration = c.get("configuration", {})
                if sw_name == "" or not configuration:
                    print(f"skipping {sw_name} with config {configuration}")
                    continue

                cls = backend_resolution(sw_name, configuration)
                if not cls:
                    continue

                conf = BackendConfiguration.from_dict(configuration)
                account_details["account_slug"] = account_slug
                b = cls(conf, self, sw_name, self._sw, True, account_details)
                backends.append(b)

        # we also support all of the aer backends!
        for b in Aer.backends():
            cls = backend_resolution(
                f"ibm.simulator.{b.name()}", b.configuration().to_dict()
            )
            if not cls:
                continue
            backends.append(
                cls(b.configuration(), self, b.name(), self._sw, False, {}, b)
            )

        return backends

    @property
    def runtime(self) -> StrangeworksRuntimeService:
        """Return the runtime service.
        Returns:
            The runtime service instance.
        Raises:
            IBMQNotAuthorizedError: If the account is not authorized to use the service.
        """
        if self._runtime:
            return self._runtime
        else:
            raise Exception("You are not authorized to use the runtime service.")


def get_backend(name=None, **kwargs):
    sw = StrangeworksProvider()
    return sw.get_backend(name, **kwargs)
