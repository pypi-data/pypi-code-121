import enum


class QuantumInstructionSet(str, enum.Enum):
    QASM = "qasm"
    QSHARP = "qs"
    IONQ = "ionq"
