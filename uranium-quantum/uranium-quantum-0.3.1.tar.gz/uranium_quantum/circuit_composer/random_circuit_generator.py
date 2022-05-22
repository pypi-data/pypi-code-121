import random
import click

from uranium_quantum.circuit_composer.circuit_composer import (
    QuantumCircuit,
)

NO_SINGLE_QBIT_GATES = 21
NO_TWO_QBIT_GATES = 24
NO_THREE_QBIT_GATES = 2


def _add_random_single_qbit_gate(quantum_circuit, qbit):

    gate = random.randint(0, NO_SINGLE_QBIT_GATES - 1)

    if gate == 0:
        quantum_circuit.gate_u3(qbit, 1, 2, 3)
    elif gate == 1:
        quantum_circuit.gate_u2(qbit, 2, 3)
    elif gate == 2:
        quantum_circuit.gate_u1(qbit, 2)
    elif gate == 3:
        quantum_circuit.gate_identity(qbit)
    elif gate == 4:
        quantum_circuit.gate_hadamard(qbit)
    elif gate == 5:
        quantum_circuit.gate_pauli_x(qbit)
    elif gate == 6:
        quantum_circuit.gate_pauli_y(qbit)
    elif gate == 7:
        quantum_circuit.gate_pauli_z(qbit)
    elif gate == 8:
        quantum_circuit.gate_t(qbit)
    elif gate == 9:
        quantum_circuit.gate_t_dagger(qbit)
    elif gate == 10:
        quantum_circuit.gate_rx_theta(qbit, 1.2)
    elif gate == 11:
        quantum_circuit.gate_ry_theta(qbit, 1.3)
    elif gate == 12:
        quantum_circuit.gate_rz_theta(qbit, 1.4)
    elif gate == 13:
        quantum_circuit.gate_s(qbit)
    elif gate == 14:
        quantum_circuit.gate_s_dagger(qbit)
    elif gate == 15:
        quantum_circuit.gate_pauli_x_root(qbit, k=random.randint(3, 10))
    elif gate == 16:
        quantum_circuit.gate_pauli_y_root(qbit, k=random.randint(3, 10))
    elif gate == 17:
        quantum_circuit.gate_pauli_z_root(qbit, k=random.randint(3, 10))
    elif gate == 18:
        quantum_circuit.gate_pauli_x_root_dagger(qbit, k=random.randint(3, 10))
    elif gate == 19:
        quantum_circuit.gate_pauli_y_root_dagger(qbit, k=random.randint(3, 10))
    elif gate == 20:
        quantum_circuit.gate_pauli_z_root_dagger(qbit, k=random.randint(3, 10))


def _add_random_two_qbit_gate(quantum_circuit, qbit, qbit2):

    gate = random.randint(0, NO_TWO_QBIT_GATES - 1)

    # randomly reorder the qbits
    if random.randint(0, 1) == 1:
        qbit2, qbit = qbit, qbit2

    control_state = random.randint(0, 1)

    if gate == 0:
        quantum_circuit.gate_ctrl_u3(qbit, control_state, qbit2, 1.0, 2.0, 3.0)
    elif gate == 1:
        quantum_circuit.gate_ctrl_u2(qbit, control_state, qbit2, 2.0, 3.0)
    elif gate == 2:
        quantum_circuit.gate_ctrl_u1(qbit, control_state, qbit2, 1.0)
    elif gate == 3:
        quantum_circuit.gate_ctrl_hadamard(qbit, control_state, qbit2)
    elif gate == 4:
        quantum_circuit.gate_ctrl_pauli_x(qbit, control_state, qbit2)
    elif gate == 5:
        quantum_circuit.gate_ctrl_pauli_x(qbit, control_state, qbit2)
    elif gate == 6:
        quantum_circuit.gate_ctrl_pauli_z(qbit, control_state, qbit2)
    elif gate == 7:
        quantum_circuit.gate_ctrl_t(qbit, control_state, qbit2)
    elif gate == 8:
        quantum_circuit.gate_ctrl_t_dagger(qbit, control_state, qbit2)
    elif gate == 9:
        quantum_circuit.gate_ctrl_rx_theta(qbit, control_state, qbit2, 2.0)
    elif gate == 10:
        quantum_circuit.gate_ctrl_ry_theta(qbit, control_state, qbit2, 3.0)
    elif gate == 11:
        quantum_circuit.gate_ctrl_rz_theta(qbit, control_state, qbit2, 4.0)
    elif gate == 12:
        quantum_circuit.gate_ctrl_s(qbit, control_state, qbit2)
    elif gate == 13:
        quantum_circuit.gate_ctrl_s_dagger(qbit, control_state, qbit2)
    elif gate == 14:
        quantum_circuit.gate_ctrl_pauli_x_root(
            qbit, control_state, qbit2, k=random.randint(3, 10)
        )
    elif gate == 15:
        quantum_circuit.gate_ctrl_pauli_y_root(
            qbit, control_state, qbit2, k=random.randint(3, 10)
        )
    elif gate == 16:
        quantum_circuit.gate_ctrl_pauli_z_root(
            qbit, control_state, qbit2, k=random.randint(3, 10)
        )
    elif gate == 17:
        quantum_circuit.gate_ctrl_pauli_x_root_dagger(
            qbit, control_state, qbit2, k=random.randint(3, 10)
        )
    elif gate == 18:
        quantum_circuit.gate_ctrl_pauli_y_root_dagger(
            qbit, control_state, qbit2, k=random.randint(3, 10)
        )
    elif gate == 19:
        quantum_circuit.gate_ctrl_pauli_z_root_dagger(
            qbit, control_state, qbit2, k=random.randint(3, 10)
        )
    elif gate == 20:
        quantum_circuit.gate_swap(qbit, qbit2)
    elif gate == 21:
        quantum_circuit.gate_sqrt_swap(qbit, qbit2)
    elif gate == 22:
        quantum_circuit.gate_swap_theta(qbit, qbit2, 2.0)
    elif gate == 23:
        quantum_circuit.gate_iswap(qbit, qbit2)
    # elif gate == 24:
    #     quantum_circuit.gate_xx(qbit, qbit2, 3.0)
    # elif gate == 25:
    #     quantum_circuit.gate_yy(qbit, qbit2, 3.0)
    # elif gate == 26:
    #     quantum_circuit.gate_zz(qbit, qbit2, 3.0)


def _add_random_three_qbit_gate(quantum_circuit, qbit, qbit2, qbit3):

    gate = random.randint(0, NO_THREE_QBIT_GATES - 1)

    # randomly reorder the qbits
    qbit_order = random.randint(0, 5)
    if qbit_order == 1:
        qbit2, qbit, qbit3 = qbit, qbit2, qbit3
    elif qbit_order == 2:
        qbit2, qbit3, qbit = qbit, qbit2, qbit3
    elif qbit_order == 3:
        qbit3, qbit, qbit2 = qbit, qbit2, qbit3
    elif qbit_order == 4:
        qbit3, qbit2, qbit = qbit, qbit2, qbit3
    elif qbit_order == 5:
        qbit, qbit3, qbit2 = qbit, qbit2, qbit3

    control_state = random.randint(0, 1)
    control_state2 = random.randint(0, 1)

    if gate == 0:
        quantum_circuit.gate_toffoli(qbit, control_state, qbit2, control_state2, qbit3)
    else:
        quantum_circuit.gate_fredkin(qbit, control_state, qbit2, qbit3)


def _add_single_qubit_gate(quantum_circuit, qubits, latest_qbit, fillqubits=False):
    if fillqubits:
        delta = 1
    else:
        delta = random.randint(1, 2)
    if latest_qbit + delta >= qubits:
        latest_qbit = -1
        quantum_circuit.increment_step()
    _add_random_single_qbit_gate(quantum_circuit, latest_qbit + delta)
    latest_qbit += delta
    return latest_qbit


def _add_two_qubit_gate(quantum_circuit, qubits, latest_qbit, fillqubits=False):
    if fillqubits:
        fst = random.randint(2, 4)
        snd = 1
    else:
        fst = random.randint(2, 4)
        snd = random.randint(1, fst - 1)
    if latest_qbit + fst >= qubits:
        latest_qbit = -1
        quantum_circuit.increment_step()
    _add_random_two_qbit_gate(quantum_circuit, latest_qbit + snd, latest_qbit + fst)
    latest_qbit += fst
    return latest_qbit


def _add_three_qubit_gate(quantum_circuit, qubits, latest_qbit, fillqubits=False):
    if fillqubits:
        fst = random.randint(3, 5)
        snd = random.randint(2, fst - 1)
        third = 1
    else:
        fst = random.randint(3, 5)
        snd = random.randint(2, fst - 1)
        third = random.randint(1, snd - 1)
    if latest_qbit + fst >= qubits:
        latest_qbit = -1
        quantum_circuit.increment_step()
    _add_random_three_qbit_gate(
        quantum_circuit, latest_qbit + third, latest_qbit + snd, latest_qbit + fst
    )
    latest_qbit += fst
    return latest_qbit


@click.command()
@click.option(
    "--qubits", "-q", type=int, required=True, help="Number of qubits in the circuit."
)
@click.option(
    "--gates", "-g", type=int, required=True, help="Number of gates in the circuit."
)
@click.option(
    "--output",
    "-o",
    required=False,
    help="Name of the output file, no extension needed.",
)
@click.option(
    "--seed",
    "-s",
    type=int,
    required=False,
    help="Random number generator seed, if missing a fixed predefined seed will be used.",
)
@click.option(
    "--measuregates",
    "-m",
    type=bool,
    default=False,
    required=False,
    help="Add measure gates at the end of circuit.",
)
@click.option(
    "--fill",
    "-f",
    type=bool,
    default=False,
    required=False,
    help="Assign gates to each and every qubit.",
)
def main(qubits, gates, output, seed, measuregates, fill):

    qubits = int(qubits)
    gates = int(gates)

    if seed:
        seed = int(seed)
        random.seed(seed)
    else:
        random.seed(1024)

    quantum_circuit = QuantumCircuit(qubits)
    # I want three qubit gates to show up more often
    no_all_gates = NO_SINGLE_QBIT_GATES + NO_TWO_QBIT_GATES + 2 * NO_THREE_QBIT_GATES

    latest_qbit = -1
    for _ in range(gates):

        gate_choice = random.randint(0, no_all_gates)
        if gate_choice < NO_SINGLE_QBIT_GATES:
            latest_qbit = _add_single_qubit_gate(
                quantum_circuit, qubits, latest_qbit, fill
            )
        elif gate_choice < NO_SINGLE_QBIT_GATES + NO_TWO_QBIT_GATES:
            latest_qbit = _add_two_qubit_gate(
                quantum_circuit, qubits, latest_qbit, fill
            )
        else:
            latest_qbit = _add_three_qubit_gate(
                quantum_circuit, qubits, latest_qbit, fill
            )

    if measuregates:
        quantum_circuit.increment_step()
        for qubit in range(qubits):
            quantum_circuit.gate_measure_z(qubit, qubit)

    output_file = output or "generated_circuit"
    output_file = output_file.rstrip(".yaml")
    output_file += f"_{qubits}_qubits_{gates}_gates.yaml"
    with open(output_file, "w") as outfile:
        quantum_circuit.export(output_file)


if __name__ == "__main__":
    main()
