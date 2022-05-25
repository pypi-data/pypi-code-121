from strangeworks.qiskit.backends.strangeworks import StrangeworksBackend
from qiskit.qobj.utils import MeasLevel, MeasReturnType
from qiskit.providers import Options


class AwsSimulator(StrangeworksBackend):
    @classmethod
    def _default_options(cls):
        return Options(
            shots=10,
            memory=False,
            qubit_lo_freq=None,
            meas_lo_freq=None,
            schedule_los=None,
            meas_level=MeasLevel.CLASSIFIED,
            meas_return=MeasReturnType.AVERAGE,
            memory_slots=None,
            memory_slot_size=100,
            rep_time=None,
            rep_delay=None,
            init_qubits=True,
            use_measure_esp=None,
        )

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


class GeneralAWSBackend(StrangeworksBackend):
    @classmethod
    def _default_options(cls):
        return Options()

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
