from strangeworks.qiskit.backends.strangeworks import StrangeworksBackend

from qiskit.providers import Options


class IonqBackend(StrangeworksBackend):
    @classmethod
    def _default_options(cls):
        return Options(shots=1)

    def __init__(
        self, configuration, provider, name, client, remote, account_details, **fields
    ):
        super().__init__(
            configuration=configuration,
            provider=provider,
            name=name,
            client=client,
            remote=remote,
            account_details=account_details,
            **fields,
        )
