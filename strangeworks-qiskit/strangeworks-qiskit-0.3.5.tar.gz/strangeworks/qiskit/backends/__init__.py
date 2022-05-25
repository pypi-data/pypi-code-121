from strangeworks.qiskit.backends.aws import AwsSimulator, GeneralAWSBackend
from strangeworks.qiskit.backends.honeywell import HoneywellBackend
from strangeworks.qiskit.backends.ibm import IBMQBackend, IBMQSimulator
from strangeworks.qiskit.backends.ionq import IonqBackend
from strangeworks.qiskit.backends.rigetti import RigettiBackend
from strangeworks.qiskit.backends.strangeworks import StrangeworksBackend
from strangeworks.qiskit.backends._utils import get_provider_and_account


def backend_resolution(
    sw_backend_name: str, backend_config: dict
) -> "StrangeworksBackend":
    provider, _ = get_provider_and_account(sw_backend_name)
    if not provider:
        return None

    simulator = False
    if "simulator" in backend_config:
        simulator = backend_config["simulator"]

    if provider == "ibm":
        if simulator:
            return IBMQSimulator
        return IBMQBackend

    if provider == "azure":
        if "honeywell" in sw_backend_name:
            return HoneywellBackend

        if "ionq" in sw_backend_name:
            return IonqBackend

    if provider == "aws":
        if "ionq" in sw_backend_name.lower():
            return IonqBackend
        if "aspen" in sw_backend_name.lower():
            return RigettiBackend
        if (
            "sv1" in sw_backend_name.lower()
            or "tn1" in sw_backend_name.lower()
            or "dm1" in sw_backend_name.lower()
        ):
            return AwsSimulator

        return GeneralAWSBackend

    if provider == "rigetti":
        return RigettiBackend

    return None
