from typing import Union
import strangeworks
from strangeworks.jobs.jobs import Job
from typing import List, Optional
from .qc import QuantumComputer
from qcs_api_client.client import QCSClientConfiguration
import pyquil
from pyquil.api._qam import QAMExecutionResult
import base64
import pickle


def list_quantum_computers() -> List[str]:
    res = []
    backends = strangeworks.client.circuit_runner.get_backends(pprint=False)
    for b in backends:
        if "rigetti" in b.selector_id():
            res.append(b.selector_id().replace("rigetti.", ""))
    return res


def get_qc(
    name: str,
    as_qvm: Optional[bool] = None,
    noisy: Optional[bool] = None,
    compiler_timeout: float = 10.0,
    execution_timeout: float = 10.0,
    client_configuration: Optional[QCSClientConfiguration] = None,
) -> QuantumComputer:
    backend = strangeworks.client.backends_service.select_backend(f"rigetti.{name}")
    ogc = pyquil.get_qc(
        name=name,
        as_qvm=as_qvm,
        noisy=noisy,
        compiler_timeout=compiler_timeout,
        execution_timeout=execution_timeout,
        client_configuration=client_configuration,
    )
    return QuantumComputer(ogc, backend=backend, as_qvm=as_qvm)


def fetch_job(
    job_id: str,
) -> Union[Job, QAMExecutionResult]:
    job = strangeworks.client.fetch_job(job_id)
    if job.is_complete():
        results = job.results()
        return execution_from_result(results)
    return job


def execution_from_result(response: dict) -> QAMExecutionResult:
    pickled_res = response["pickled_result"]
    pickle_bytes = base64.b64decode(pickled_res)
    return pickle.loads(pickle_bytes)
