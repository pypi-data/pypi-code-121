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
from uranium_quantum.circuit_exporter.qiskit_custom_gates import *


cr_main = ClassicalRegister(33)
qr_main = QuantumRegister(30)
qc_main = QuantumCircuit(qr_main, cr_main)


qc_main.u(1.57, 1.57, 1.57, qr_main[1])

qc_main.u(np.pi/2, 1.57, 1.57, qr_main[2])

qc_main.p(1.57, qr_main[3])

qc_main.id(qr_main[4])

qc_main.h(qr_main[5])

qc_main.unitary(hadamard_xy(), [6], label='hadamard-xy')

qc_main.unitary(hadamard_yz(), [7], label='hadamard-yz')

qc_main.h(qr_main[8])

qc_main.x(qr_main[9])

qc_main.y(qr_main[10])

qc_main.z(qr_main[11])

qc_main.unitary(pauli_x_root(2.0), [12], label='pauli-x-root')

qc_main.unitary(pauli_y_root((2**7.0)), [13], label='pauli-y-root')

qc_main.unitary(pauli_z_root((2**22.0)), [14], label='pauli-z-root')

qc_main.unitary(pauli_x_root_dagger((2**29.0)), [15], label='pauli-x-root-dagger')

qc_main.unitary(pauli_y_root_dagger((2**8.0)), [16], label='pauli-y-root-dagger')

qc_main.unitary(pauli_z_root_dagger(1.1), [17], label='pauli-z-root-dagger')

qc_main.rx(1.57, qr_main[18])

qc_main.ry(1.57, qr_main[19])

qc_main.rz(1.57, qr_main[20])

qc_main.t(qr_main[21])

qc_main.tdg(qr_main[22])

qc_main.s(qr_main[23])

qc_main.sdg(qr_main[24])

qc_main.append(SXGate(), [qr_main[25]])

qc_main.append(SXdgGate(), [qr_main[26]])

qc_main.unitary(h(), [27], label='h')

qc_main.unitary(h_dagger(), [28], label='h-dagger')

qc_main.unitary(c(), [29], label='c')

qc_main.unitary(c_dagger(), [0], label='c-dagger')

qc_main.p(0.5, qr_main[1])

qc_main.measure(2, 32)

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(UGate(1.57, 1.57, 1.57).control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[2]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(UGate(1.5707963267948966, 1.57, 1.57).control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[3]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(U1Gate(1.57).control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(HGate().control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[5]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(hadamard_xy().control(num_ctrl_qubits=2, ctrl_state='01', label='hadamard-xy'), [qr_main[0], qr_main[1], qr_main[6]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(hadamard_yz().control(num_ctrl_qubits=2, ctrl_state='01', label='hadamard-yz'), [qr_main[0], qr_main[1], qr_main[7]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(HGate().control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[8]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(XGate().control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[9]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(YGate().control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[10]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(ZGate().control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[11]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(pauli_x_root(2.0).control(num_ctrl_qubits=2, ctrl_state='01', label='pauli-x-root'), [qr_main[0], qr_main[1], qr_main[12]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(pauli_y_root((2**7.0)).control(num_ctrl_qubits=2, ctrl_state='01', label='pauli-y-root'), [qr_main[0], qr_main[1], qr_main[13]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(pauli_z_root((2**22.0)).control(num_ctrl_qubits=2, ctrl_state='01', label='pauli-z-root'), [qr_main[0], qr_main[1], qr_main[14]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(pauli_x_root_dagger((2**29.0)).control(num_ctrl_qubits=2, ctrl_state='01', label='pauli-x-root-dagger'), [qr_main[0], qr_main[1], qr_main[15]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(pauli_y_root_dagger((2**8.0)).control(num_ctrl_qubits=2, ctrl_state='01', label='pauli-y-root-dagger'), [qr_main[0], qr_main[1], qr_main[16]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(pauli_z_root_dagger(1.1).control(num_ctrl_qubits=2, ctrl_state='01', label='pauli-z-root-dagger'), [qr_main[0], qr_main[1], qr_main[17]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(RXGate(1.57).control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[18]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(RYGate(1.57).control(num_ctrl_qubits=2, ctrl_state='01'), [qr_main[0], qr_main[1], qr_main[19]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.h(qr_main[1])
qc_main.append(RZGate(1.57).control(num_ctrl_qubits=2, ctrl_state='11'), [qr_main[0], qr_main[1], qr_main[20]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(TGate().control(num_ctrl_qubits=2, ctrl_state='11'), [qr_main[0], qr_main[1], qr_main[21]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(TdgGate().control(num_ctrl_qubits=2, ctrl_state='11'), [qr_main[0], qr_main[1], qr_main[22]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(SGate().control(num_ctrl_qubits=2, ctrl_state='11'), [qr_main[0], qr_main[1], qr_main[23]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(SdgGate().control(num_ctrl_qubits=2, ctrl_state='11'), [qr_main[0], qr_main[1], qr_main[24]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(SXGate().control(num_ctrl_qubits=2, ctrl_state='11'), [qr_main[0], qr_main[1], qr_main[25]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(SXdgGate().control(num_ctrl_qubits=2, ctrl_state='11'), [qr_main[0], qr_main[1], qr_main[26]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(h().control(num_ctrl_qubits=2, ctrl_state='11', label='h'), [qr_main[0], qr_main[1], qr_main[27]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(h_dagger().control(num_ctrl_qubits=2, ctrl_state='11', label='h-dagger'), [qr_main[0], qr_main[1], qr_main[28]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(c().control(num_ctrl_qubits=2, ctrl_state='11', label='c'), [qr_main[0], qr_main[1], qr_main[29]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(c_dagger().control(num_ctrl_qubits=2, ctrl_state='11', label='c-dagger'), [qr_main[0], qr_main[1], qr_main[2]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(U1Gate(0.2).control(num_ctrl_qubits=2, ctrl_state='11'), [qr_main[0], qr_main[1], qr_main[3]])
qc_main.h(qr_main[1])

qc_main.swap(qr_main[0], qr_main[1])

qc_main.append(sqrt_swap(label='sqrt-swap'), [qr_main[2], qr_main[3]])

qc_main.append(sqrt_swap_dagger(label='sqrt-swap-dagger'), [qr_main[4], qr_main[5]])

qc_main.append(swap_theta(1.1, label='swap-theta'), [qr_main[6], qr_main[7]])

qc_main.iswap(qr_main[8], qr_main[9])

qc_main.append(fswap(label='fswap'), [qr_main[10], qr_main[11]])

qc_main.append(swap_root(2.1, label='swap-root'), [qr_main[12], qr_main[13]])

qc_main.append(swap_root_dagger(2.1, label='swap-root-dagger'), [qr_main[14], qr_main[15]])

qc_main.append(RXXGate(0.22), [qr_main[16], qr_main[17]])

qc_main.append(RYYGate(0.22), [qr_main[18], qr_main[19]])

qc_main.append(RZZGate(0.22), [qr_main[20], qr_main[21]])

qc_main.append(xy(0.22, label='xy'), [qr_main[22], qr_main[23]])

qc_main.append(molmer_sorensen(label='molmer-sorensen'), [qr_main[24], qr_main[25]])

qc_main.append(molmer_sorensen_dagger(label='molmer-sorensen-dagger'), [qr_main[0], qr_main[1]])

qc_main.append(berkeley(label='berkeley'), [qr_main[2], qr_main[3]])

qc_main.append(berkeley_dagger(label='berkeley-dagger'), [qr_main[4], qr_main[5]])

qc_main.append(ecp(label='ecp'), [qr_main[6], qr_main[7]])

qc_main.append(ecp_dagger(label='ecp-dagger'), [qr_main[8], qr_main[9]])

qc_main.append(w(label='w'), [qr_main[10], qr_main[11]])

qc_main.append(a(1.22, 1.44, label='a'), [qr_main[12], qr_main[13]])

qc_main.append(magic(label='magic'), [qr_main[14], qr_main[15]])

qc_main.append(magic_dagger(label='magic-dagger'), [qr_main[16], qr_main[17]])

qc_main.append(RZXGate(0.1), [qr_main[18], qr_main[19]])

qc_main.append(RZXGate(-0.2), [qr_main[20], qr_main[21]])

qc_main.append(givens(2.1, label='givens'), [qr_main[22], qr_main[23]])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(SwapGate().control(num_ctrl_qubits=2, ctrl_state='10'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(sqrt_swap().control(num_ctrl_qubits=2, ctrl_state='10', label='sqrt-swap'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(sqrt_swap_dagger().control(num_ctrl_qubits=2, ctrl_state='10', label='sqrt-swap-dagger'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(swap_theta(1.2).control(num_ctrl_qubits=2, ctrl_state='10', label='swap-theta'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(iSwapGate().control(num_ctrl_qubits=2, ctrl_state='10'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(fswap().control(num_ctrl_qubits=2, ctrl_state='10', label='fswap'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(swap_root(2).control(num_ctrl_qubits=2, ctrl_state='10', label='swap-root'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(swap_root_dagger(3).control(num_ctrl_qubits=2, ctrl_state='10', label='swap-root-dagger'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(RXXGate(0.1).control(num_ctrl_qubits=2, ctrl_state='10'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(RYYGate(0.1).control(num_ctrl_qubits=2, ctrl_state='10'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(RZZGate(0.1).control(num_ctrl_qubits=2, ctrl_state='10'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(xy(0.1).control(num_ctrl_qubits=2, ctrl_state='10', label='xy'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.h(qr_main[1])
qc_main.append(molmer_sorensen().control(num_ctrl_qubits=2, ctrl_state='10', label='molmer-sorensen'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(molmer_sorensen_dagger().control(num_ctrl_qubits=2, ctrl_state='10', label='molmer-sorensen-dagger'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(berkeley().control(num_ctrl_qubits=2, ctrl_state='10', label='berkeley'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[0])
qc_main.h(qr_main[1])
qc_main.append(berkeley_dagger().control(num_ctrl_qubits=2, ctrl_state='11', label='berkeley-dagger'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[0])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(ecp().control(num_ctrl_qubits=2, ctrl_state='10', label='ecp'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[0])
qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(ecp_dagger().control(num_ctrl_qubits=2, ctrl_state='10', label='ecp-dagger'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[0])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.h(qr_main[1])
qc_main.append(w().control(num_ctrl_qubits=2, ctrl_state='10', label='w'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[1])
qc_main.append(a(0.1, 0.2).control(num_ctrl_qubits=2, ctrl_state='10', label='a'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[1])

qc_main.h(qr_main[0])
qc_main.h(qr_main[1])
qc_main.append(magic().control(num_ctrl_qubits=2, ctrl_state='00', label='magic'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[0])
qc_main.h(qr_main[1])

qc_main.h(qr_main[0])
qc_main.h(qr_main[1])
qc_main.append(magic_dagger().control(num_ctrl_qubits=2, ctrl_state='10', label='magic-dagger'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[0])
qc_main.h(qr_main[1])

qc_main.h(qr_main[0])
qc_main.h(qr_main[1])
qc_main.append(RZXGate(0.1).control(num_ctrl_qubits=2, ctrl_state='10', label='cross-resonance'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[0])
qc_main.h(qr_main[1])

qc_main.h(qr_main[0])
qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(RZXGate(-0.1).control(num_ctrl_qubits=2, ctrl_state='01', label='cross-resonance-dg'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[0])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

qc_main.h(qr_main[0])
qc_main.unitary(gate_rotation_to_y_basis(), [1])
qc_main.append(givens(0.1).control(num_ctrl_qubits=2, ctrl_state='01', label='givens'), [qr_main[0], qr_main[1], qr_main[3], qr_main[4]])
qc_main.h(qr_main[0])
qc_main.unitary(gate_undo_rotation_to_y_basis(), [1])

