import numpy as np
from qiskit import QuantumRegister
from qiskit.circuit import ClassicalRegister
from qiskit import QuantumCircuit

from qiskit.circuit.library.standard_gates import XGate, YGate, ZGate, HGate
from qiskit.circuit.library import RXGate, RYGate, RZGate
from qiskit.circuit.library import RXXGate, RYYGate, RZZGate
from qiskit.circuit.library import RZXGate
from qiskit.circuit.library import SXGate, SXdgGate
from qiskit.circuit.library import SGate, SdgGate, TGate, TdgGate
from qiskit.circuit.library import UGate, U1Gate
from qiskit.circuit.library import SwapGate, iSwapGate
from qiskit.circuit.library import QFT
from uranium_quantum.circuit_exporter.qiskit_custom_gates import *


qr_third_circuit = QuantumRegister(3)
qc_third_circuit = QuantumCircuit(qr_third_circuit)


qc_third_circuit.h(qr_third_circuit[0])

qc_third_circuit.h(qr_third_circuit[1])

qc_third_circuit.h(qr_third_circuit[2])


qr_secondary_circuit = QuantumRegister(4)
qc_secondary_circuit = QuantumCircuit(qr_secondary_circuit)


qc_secondary_circuit.x(qr_secondary_circuit[0])

qc_secondary_circuit.append(qc_third_circuit.to_gate(label='third_circuit').inverse(), [qr_secondary_circuit[1], qr_secondary_circuit[2], qr_secondary_circuit[3]])
qc_secondary_circuit.append(qc_third_circuit.to_gate(label='third_circuit').inverse(), [qr_secondary_circuit[1], qr_secondary_circuit[2], qr_secondary_circuit[3]])


qr_main = QuantumRegister(7)
qc_main = QuantumCircuit(qr_main)


qc_main.x(qr_main[0])

qc_main.unitary(gate_rotation_to_y_basis(), [5])
qc_main.append(qc_secondary_circuit.to_gate().control(num_ctrl_qubits=2, ctrl_state='10', label='secondary_circuit'), [qr_main[5], qr_main[6], qr_main[1], qr_main[2], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [5])

qc_main.y(qr_main[0])

qc_main.append(qc_third_circuit.to_gate(label='third_circuit').inverse(), [qr_main[1], qr_main[2], qr_main[3]])

qc_main.z(qr_main[0])

qc_main.append(QFT(4).control(num_ctrl_qubits=1, ctrl_state='1'), [qr_main[5], qr_main[1], qr_main[2], qr_main[3], qr_main[4]])

qc_main.append(QFT(6).inverse(), [qr_main[0], qr_main[1], qr_main[2], qr_main[3], qr_main[4], qr_main[5]])


