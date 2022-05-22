from enum import Enum

from typing_extensions import Literal


class ProviderVendor(str, Enum):
    IBMQ = "IBMQ"
    AZURE_QUANTUM = "Azure Quantum"
    AWS_BRAKET = "AWS Braket"
    IONQ = "IonQ"
    NVIDIA = "Nvidia"


class ProviderTypeVendor:
    IBMQ = Literal[ProviderVendor.IBMQ]
    AZURE_QUANTUM = Literal[ProviderVendor.AZURE_QUANTUM]
    AWS_BRAKET = Literal[ProviderVendor.AWS_BRAKET]
    IONQ = Literal[ProviderVendor.IONQ]
    NVIDIA = Literal[ProviderVendor.NVIDIA]


class IonqBackendNames(str, Enum):
    SIMULATOR = "simulator"
    QPU = "qpu"


class AzureQuantumBackendNames(str, Enum):
    IONQ_SIMULATOR = "ionq.simulator"
    IONQ_QPU = "ionq.qpu"
    HONEYWELL_API_VALIDATOR1 = "honeywell.hqs-lt-s1-apival"
    HONEYWELL_API_VALIDATOR2 = "honeywell.hqs-lt-s2-apival"
    HONEYWELL_SIMULATOR1 = "honeywell.hqs-lt-s1-sim"
    HONEYWELL_SIMULATOR2 = "honeywell.hqs-lt-s2-sim"
    HONEYWELL_QPU1 = "honeywell.hqs-lt-s1"
    HONEYWELL_QPU2 = "honeywell.hqs-lt-s2"
    QUANTINUUM_API_VALIDATOR1 = "quantinuum.hqs-lt-s1-apival"
    QUANTINUUM_API_VALIDATOR2 = "quantinuum.hqs-lt-s2-apival"
    QUANTINUUM_SIMULATOR1 = "quantinuum.hqs-lt-s1-sim"
    QUANTINUUM_SIMULATOR2 = "quantinuum.hqs-lt-s2-sim"
    QUANTINUUM_QPU1 = "quantinuum.hqs-lt-s1"
    QUANTINUUM_QPU2 = "quantinuum.hqs-lt-s2"
    MICROSOFT_FULLSTATE_SIMULATOR = "microsoft.simulator.fullstate"


class AWSBackendNames(str, Enum):
    AWS_BRAKET_SV1 = "SV1"
    AWS_BRAKET_TN1 = "TN1"
    AWS_BRAKET_DM1 = "dm1"
    AWS_BRAKET_ASPEN_9 = "Aspen-9"
    AWS_BRAKET_ASPEN_10 = "Aspen-10"
    AWS_BRAKET_IONQ = "IonQ Device"


class IBMQBackendNames(str, Enum):
    IBMQ_AER_SIMULATOR = "aer_simulator"
    IBMQ_AER_SIMULATOR_STATEVECTOR = "aer_simulator_statevector"
    IBMQ_AER_SIMULATOR_DENSITY_MATRIX = "aer_simulator_density_matrix"
    IBMQ_AER_SIMULATOR_MATRIX_PRODUCT_STATE = "aer_simulator_matrix_product_state"


class NvidiaBackendNames(str, Enum):
    STATEVECTOR = "statevector"


EXACT_SIMULATORS = {
    IonqBackendNames.SIMULATOR,
    AzureQuantumBackendNames.IONQ_SIMULATOR,
    AzureQuantumBackendNames.MICROSOFT_FULLSTATE_SIMULATOR,
    AWSBackendNames.AWS_BRAKET_SV1,
    AWSBackendNames.AWS_BRAKET_TN1,
    AWSBackendNames.AWS_BRAKET_DM1,
    NvidiaBackendNames.STATEVECTOR,
    *IBMQBackendNames,
}
