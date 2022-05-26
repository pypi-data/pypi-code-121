from typing import List, Dict, Tuple

from qiskit.providers.ibmq import IBMQBackend
from qiskit.providers.models.backendproperties import Gate


def get_gate_time(gate: Gate, qubit_data: List[dict], gf_data: Dict[str, int]) -> int:
    if gate.gate == 'u1':
        return 0
    if gate.gate == 'u2':
        buffer = qubit_data[gate.qubits[0]].get('buffer', {}).get('value', None)
        gd_gatetime = qubit_data[gate.qubits[0]].get('gateTime', {}).get('value', None)
        return buffer + gd_gatetime
    if gate.gate == 'u3':
        buffer = qubit_data[gate.qubits[0]].get('buffer', {}).get('value', None)
        gd_gatetime = qubit_data[gate.qubits[0]].get('gateTime', {}).get('value', None)
        return 2*(buffer + gd_gatetime)
    if gate.gate == 'cx':
        gf_gatetime = gf_data[gate.name.upper()]
        buffer_0 = qubit_data[gate.qubits[0]].get('buffer', {}).get('value', None)
        buffer_1 = qubit_data[gate.qubits[1]].get('buffer', {}).get('value', None)
        gd_gatetime_0 = qubit_data[gate.qubits[0]].get('gateTime', {}).get('value', None)
        gd_gatetime_1 = qubit_data[gate.qubits[1]].get('gateTime', {}).get('value', None)
        return max(buffer_0 + gd_gatetime_0, buffer_1 + gd_gatetime_1) \
               + 2*(gf_gatetime + max(buffer_0, buffer_1)) \
               + buffer_0 + gd_gatetime_0
    return 0


def get_gate_times(backend: IBMQBackend) -> List[Tuple[str, List[int], int]]:
    device_properties = backend.properties()
    gates = device_properties.gates #  type: List[Gate]
    gate_times = [(g.gate, g.qubits, [p.value for p in g.parameters if p.name == 'gate_length'][0]) for g in gates]

    return gate_times
