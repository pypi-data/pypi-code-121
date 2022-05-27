from strangeworks.qiskit.backends.strangeworks import StrangeworksBackend

from typing import Dict, List, Union, Optional, Any

from qiskit.circuit import QuantumCircuit, Parameter
from qiskit.pulse import Schedule, LoConfig
from qiskit.pulse.channels import PulseChannel
from qiskit.providers.options import Options
from qiskit.qobj import QasmQobj, PulseQobj, QobjHeader
from qiskit.qobj.utils import MeasLevel, MeasReturnType
from qiskit.util import deprecate_arguments

from qiskit import assemble

import warnings, copy


class IBMQBackend(StrangeworksBackend):
    qobj_warning_issued = False

    @classmethod
    def _default_options(cls) -> Options:
        """Default runtime options."""
        return Options(
            shots=1024,
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

    @deprecate_arguments({"qobj": "circuits"})
    def run(
        self,
        circuits: Union[
            QasmQobj,
            PulseQobj,
            QuantumCircuit,
            Schedule,
            List[Union[QuantumCircuit, Schedule]],
        ],
        job_name: Optional[str] = None,
        job_share_level: Optional[str] = None,
        job_tags: Optional[List[str]] = None,
        experiment_id: Optional[str] = None,
        validate_qobj: bool = None,
        header: Optional[Dict] = None,
        shots: Optional[int] = None,
        memory: Optional[bool] = None,
        qubit_lo_freq: Optional[List[int]] = None,
        meas_lo_freq: Optional[List[int]] = None,
        schedule_los: Optional[
            Union[
                List[Union[Dict[PulseChannel, float], LoConfig]],
                Union[Dict[PulseChannel, float], LoConfig],
            ]
        ] = None,
        meas_level: Optional[Union[int, MeasLevel]] = None,
        meas_return: Optional[Union[str, MeasReturnType]] = None,
        memory_slots: Optional[int] = None,
        memory_slot_size: Optional[int] = None,
        rep_time: Optional[int] = None,
        rep_delay: Optional[float] = None,
        init_qubits: Optional[bool] = None,
        parameter_binds: Optional[List[Dict[Parameter, float]]] = None,
        **run_config: Dict,
    ):
        sim_method = None
        if self.configuration().simulator:
            sim_method = getattr(self.configuration(), "simulation_method", None)
        if isinstance(circuits, (QasmQobj, PulseQobj)):
            if not self.qobj_warning_issued:
                warnings.warn(
                    "Passing a Qobj to Backend.run is deprecated and will "
                    "be removed in a future release. Please pass in circuits "
                    "or pulse schedules instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                self.qobj_warning_issued = True
            qobj = circuits
            if sim_method and not hasattr(qobj.config, "method"):
                qobj.config.method = sim_method
            if qobj.header == QobjHeader():
                qobj.header.backend_name = getattr(
                    self.configuration(), "backend_name", self.name()
                )
                qobj.header.backend_version = self.version
        else:
            qobj_header = run_config.pop("qobj_header", None)
            header = header or qobj_header
            run_config_dict = self._get_run_config(
                qobj_header=header,
                shots=shots,
                memory=memory,
                qubit_lo_freq=qubit_lo_freq,
                meas_lo_freq=meas_lo_freq,
                schedule_los=schedule_los,
                meas_level=meas_level,
                meas_return=meas_return,
                memory_slots=memory_slots,
                memory_slot_size=memory_slot_size,
                rep_time=rep_time,
                rep_delay=rep_delay,
                init_qubits=init_qubits,
                **run_config,
            )
            if parameter_binds:
                run_config_dict["parameter_binds"] = parameter_binds
            if sim_method and "method" not in run_config_dict:
                run_config_dict["method"] = sim_method
            qobj = assemble(circuits, self, **run_config_dict)
        return super().run(qobj)

    def _get_run_config(self, **kwargs: Any) -> Dict:
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
                        f"{key} is not a recognized runtime"  # type: ignore[unreachable]
                        f" option and may be ignored by the backend.",
                        stacklevel=4,
                    )
        return run_config_dict


class IBMQSimulator(IBMQBackend):
    @classmethod
    def _default_options(cls) -> Options:
        options = super()._default_options()
        options.update_options(noise_model=None, seed_simulator=None)
        return options

    def __init__(
        self,
        configuration,
        provider,
        name,
        client,
        remote,
        account_details={},
        simulator=None,
        **fields,
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
        self.simulator = simulator

    def properties(self) -> None:
        if self.is_remote():
            return super().properties()
        return None

    def status(self):
        if self.is_remote():
            return super().status()
        return self.simulator.status()

    @deprecate_arguments({"qobj": "circuits"})
    def run(  # type: ignore[override]
        self,
        circuits: Union[
            QasmQobj,
            PulseQobj,
            QuantumCircuit,
            Schedule,
            List[Union[QuantumCircuit, Schedule]],
        ],
        job_name: Optional[str] = None,
        job_share_level: Optional[str] = None,
        job_tags: Optional[List[str]] = None,
        experiment_id: Optional[str] = None,
        backend_options: Optional[Dict] = None,
        noise_model: Any = None,
        **kwargs: Dict,
    ):
        if job_share_level:
            warnings.warn(
                "The `job_share_level` keyword is no longer supported "
                "and will be removed in a future release.",
                Warning,
                stacklevel=3,
            )
        if backend_options is not None:
            warnings.warn(
                "Use of `backend_options` is deprecated and will "
                "be removed in a future release."
                "You can now pass backend options as key-value pairs to the "
                "run() method. For example: backend.run(circs, shots=2048).",
                DeprecationWarning,
                stacklevel=2,
            )
        backend_options = backend_options or {}
        run_config = copy.deepcopy(backend_options)
        if noise_model:
            try:
                noise_model = noise_model.to_dict()
            except AttributeError:
                pass
        run_config.update(kwargs)
        return super().run(
            circuits,
            job_name=job_name,
            job_tags=job_tags,
            experiment_id=experiment_id,
            noise_model=noise_model,
            **run_config,
        )
