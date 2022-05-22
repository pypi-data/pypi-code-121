"""A simple API for creating quantum circuits in yaml format using python."""

from typing import Dict, List

class Control:
    def __init__(self, target, state):
        self.target = target
        self.state = state

class QbitAleadyTaken(Exception):
    """Will be thrown when a gate exist at indicated step and qubit."""

    def __init__(self, qbit, step):
        """Raise exception."""
        super().__init__()
        self.message = (
            f"The position defined by step {step} and qbit {qbit} is already taken."
        )


class QbitIndexLargerThanCircuitSize(Exception):
    """Will throw when the index of the qbit where a gate should be applied is\
 larger than the maximum size limit allowed by the quantum circuit."""

    def __init__(self, qbit, step):
        """Raise exception."""
        super().__init__()
        self.message = f"Requested qbit index {qbit} during step {step} is \
larger then the maximum size allowed by quantum circuit."


class QuantumCircuit:
    """A quantum circuit is basically a collection of qubits where quantum gates
    can be allocated at positions defined by a qbit index and step index."""

    def __init__(self, no_qbits):
        """Intialize a quantum register having a predefined fixed number of qbits."""
        self._no_qbits: int
        self._current_step: int
        self._gates: Dict[int, Dict]
        self._qbits_taken: Dict[int, List]

        self._no_qbits = no_qbits
        self._current_step = 0
        self._gates = {}
        self._qbits_taken = {}

        self._gates[0] = []
        self._qbits_taken[0] = set()

    def increment_step(self):
        """Increment current step index. A step used a to group a collection of \
gates that can be applied in parallel on a quantum circuit. Steps is a facility added \
mainly for easier visualisation of the collection of gates applied on a circuit \
in a web browser. Grouping gates in a layout indexed by steps also facilitates \
delivering some of the logic intended by the creator of the circuit."""
        self._current_step += 1
        self._gates[self._current_step] = []
        self._qbits_taken[self._current_step] = set()
        return self

    def _gates_in_current_step(self):
        return self._gates[self._current_step]

    def _check_circuit_size(self, target):
        if target >= self._no_qbits:
            raise QbitIndexLargerThanCircuitSize(target, self._current_step)

    def _check_qbit_alocated(self, qbit):
        if qbit in self._qbits_taken[self._current_step]:
            raise QbitAleadyTaken(qbit, self._current_step)

    def _get_controls_targets(self, controls):
        targets = []
        for control in controls:
            targets.append(control.target)
        return targets

    def _get_aggregated_targets(self, gates):
        targets = []
        for gate in gates:
            targets.append(gate["targets"][0])
        return targets

    def _qbits_taken_in_current_step(self):
        return self._qbits_taken[self._current_step]

    def _format_controls(self, controls):
        formatted_controls = []
        for control in controls:
            formatted_controls.append({'target': control.target, 'state': control.state})
        return formatted_controls

    def current_step(self):
        """Get number of steps"""
        return self._current_step

    def list_of_qubits_contains_no_duplicates(self, list):
        return len(list) == len(set(list))

    def export(self, name):
        """Export the quantum circuit to a file in YAML format."""
        if not name.endswith(".yaml") and not name.endswith(".yml"):
            name = name + ".yaml"
        with open(name, "w") as yaml_file:
            yaml_file.write("version: '1.1'\n")
            yaml_file.write("circuit-type: simple\n")
            yaml_file.write("steps:\n")
            for step in range(self._current_step + 1):
                yaml_file.write("  - index: " + str(step) + "\n")
                yaml_file.write("    gates:\n")
                for gate in self._gates[step]:
                    yaml_file.write("      - name: " + gate["name"] + "\n")
                    if "targets" in gate and gate["targets"]:
                        yaml_file.write("        targets:\n")
                        for target in gate["targets"]:
                            yaml_file.write(
                                "          - " + str(target) + "\n"
                            )
                    if "controls" in gate and gate["controls"]:
                        yaml_file.write("        controls:\n")
                        for control in gate["controls"]:
                            yaml_file.write(
                                "          - target: " + str(control["target"]) + "\n"
                            )
                            yaml_file.write(
                                "            state: '" + str(control["state"]) + "'\n"
                            )
                    if "gates" in gate and gate["gates"]:
                        yaml_file.write("        gates:\n")
                        for aggregated_gate in gate["gates"]:
                            yaml_file.write("          - name: " + aggregated_gate["name"] + "\n")
                            yaml_file.write("            targets:\n")
                            for target in aggregated_gate["targets"]:
                                yaml_file.write("              - " + str(target) + "\n")
                            if "theta" in aggregated_gate:
                                yaml_file.write("            theta: " + str(aggregated_gate["theta"]) + "\n")
                            if "phi" in aggregated_gate:
                                yaml_file.write("            phi: " + str(aggregated_gate["phi"]) + "\n")
                            if "lambda" in aggregated_gate:
                                yaml_file.write("            lambda: " + str(aggregated_gate["lambda"]) + "\n")
                            if "root-k" in aggregated_gate:
                                yaml_file.write(
                                    "            root: " + f'1/2^{aggregated_gate["root-k"]}' + "\n"
                                )
                            if "root-t" in aggregated_gate:
                                yaml_file.write(
                                    "            root: " + f'1/{str(aggregated_gate["root-t"])}' + "\n"
                                )
                    if "theta" in gate:
                        yaml_file.write("        theta: " + str(gate["theta"]) + "\n")
                    if "phi" in gate:
                        yaml_file.write("        phi: " + str(gate["phi"]) + "\n")
                    if "lambda" in gate:
                        yaml_file.write("        lambda: " + str(gate["lambda"]) + "\n")
                    if "root-k" in gate:
                        yaml_file.write(
                            "        root: " + f'1/2^{gate["root-k"]}' + "\n"
                        )
                    if "root-t" in gate:
                        yaml_file.write(
                            "        root: " + f'1/{str(gate["root-t"])}' + "\n"
                        )
                    if "bit" in gate:
                        yaml_file.write("        bit: " + str(gate["bit"]) + "\n")

    def setup_new_gate(self, gate, qbits):
        for qbit in qbits:
            self._check_circuit_size(qbit)
            self._check_qbit_alocated(qbit)
        for qbit in range(min(qbits), max(qbits) + 1):
            self._qbits_taken_in_current_step().add(qbit)
        self._gates_in_current_step().append(gate)

    def gate_aggregate(self, controls, gates):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + self._get_aggregated_targets(gates)), "Target and control qubit list must contain no duplicates."
        gate = {}
        gate["name"] = "aggregate"
        gate["controls"] = self._format_controls(controls)
        gate["gates"] = gates
        self.setup_new_gate(gate, self._get_controls_targets(controls) + self._get_aggregated_targets(gates))
        return self

    def gate_u1(self, controls, targets, lambda_radians):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert lambda_radians is not None, "Value of lambda must be specified for this gate."
        gate = {}
        gate["name"] = "u1"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["lambda"] = lambda_radians
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_u2(self, controls, targets, phi_radians, lambda_radians):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert lambda_radians is not None, "Value of lambda must be specified for this gate."
        assert phi_radians is not None, "Value of phi must be specified for this gate."
        gate = {}
        gate["name"] = "u2"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["phi"] = phi_radians
        gate["lambda"] = lambda_radians
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_u3(self, controls, targets, theta_radians, phi_radians, lambda_radians):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert lambda_radians is not None, "Value of lambda must be specified for this gate."
        assert phi_radians is not None, "Value of phi must be specified for this gate."
        assert theta_radians is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "u3"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta_radians
        gate["phi"] = phi_radians
        gate["lambda"] = lambda_radians
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_identity(self, targets):
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "identity"
        gate["targets"] = targets
        self.setup_new_gate(gate, targets)
        return self

    def gate_hadamard(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "hadamard"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_hadamard_xy(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "hadamard-xy"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_hadamard_yz(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "hadamard-yz"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_hadamard_zx(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "hadamard-zx"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_x(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "pauli-x"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_y(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "pauli-y"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_z(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "pauli-z"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_x_root(self, controls, targets, t=None, k=None):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert t != None or k != None
        gate = {}
        gate["name"] = "pauli-x-root"
        if k:
            gate["root-k"] = k
        elif t:
            gate["root-t"] = t
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_y_root(self, controls, targets, t=None, k=None):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert t != None or k != None
        gate = {}
        gate["name"] = "pauli-y-root"
        if k:
            gate["root-k"] = k
        elif t:
            gate["root-t"] = t
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_z_root(self, controls, targets, t=None, k=None):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert t != None or k != None
        gate = {}
        gate["name"] = "pauli-z-root"
        if k:
            gate["root-k"] = k
        elif t:
            gate["root-t"] = t
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_x_root_dagger(self, controls, targets, t=None, k=None):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert t != None or k != None
        gate = {}
        gate["name"] = "pauli-x-root-dagger"
        if k:
            gate["root-k"] = k
        elif t:
            gate["root-t"] = t
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_y_root_dagger(self, controls, targets, t=None, k=None):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert t != None or k != None
        gate = {}
        gate["name"] = "pauli-y-root-dagger"
        if k:
            gate["root-k"] = k
        elif t:
            gate["root-t"] = t
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_pauli_z_root_dagger(self, controls, targets, t=None, k=None):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert t != None or k != None
        gate = {}
        gate["name"] = "pauli-z-root-dagger"
        if k:
            gate["root-k"] = k
        elif t:
            gate["root-t"] = t
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_rx_theta(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "rx-theta"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_ry_theta(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "ry-theta"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_rz_theta(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "rz-theta"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_s(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "s"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_s_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "s-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_p(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "p"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_t(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "t"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_t_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "t-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_v(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "v"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_v_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "v-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_h(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "h"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_h_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "h-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_c(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "c"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_c_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "c-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_xx(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "xx"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_yy(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "yy"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_zz(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "zz"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_xy(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "xy"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_swap(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "swap"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_iswap(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "iswap"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_fswap(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "fswap"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_swap_theta(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "swap-theta"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_sqrt_swap(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "sqrt-swap"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_sqrt_swap_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "sqrt-swap-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_swap_root(self, controls, targets, t):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "swap-root"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["root-t"] = t
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_swap_root_dagger(self, controls, targets, t):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "swap-root-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["root-t"] = t
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_molmer_sorensen(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "molmer-sorensen"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_molmer_sorensen_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "molmer-sorensen-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_w(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "w"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_berkeley(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "berkeley"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_berkeley_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "berkeley-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_ecp(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "ecp"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_ecp_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "ecp-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_magic(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "magic"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_magic_dagger(self, controls, targets):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        gate = {}
        gate["name"] = "magic-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_cross_resonance(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "cross-resonance"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_cross_resonance_dagger(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "cross-resonance-dagger"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_a(self, controls, targets, theta, phi):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "a"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        gate["phi"] = phi
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_givens(self, controls, targets, theta):
        assert self.list_of_qubits_contains_no_duplicates(self._get_controls_targets(controls) + targets),  "Target and control qubit list must contain no duplicates."
        assert len(targets) == 2, "For a two qubit gate you need to specify two target qubits."
        assert theta is not None, "Value of theta must be specified for this gate."
        gate = {}
        gate["name"] = "givens"
        gate["controls"] = self._format_controls(controls)
        gate["targets"] = targets
        gate["theta"] = theta
        self.setup_new_gate(gate, self._get_controls_targets(controls) + targets)
        return self

    def gate_measure_x(self, targets, classic_bit):
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "measure-x"
        gate["targets"] = targets
        gate["bit"] = classic_bit
        self.setup_new_gate(gate, targets)
        return self

    def gate_measure_y(self, targets, classic_bit):
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "measure-y"
        gate["targets"] = targets
        gate["bit"] = classic_bit
        self.setup_new_gate(gate, targets)
        return self

    def gate_measure_z(self, targets, classic_bit):
        assert len(targets) == 1, "This is a one qubit gate, please specify as argument a list containing one target qubit."
        gate = {}
        gate["name"] = "measure-z"
        gate["targets"] = targets
        gate["bit"] = classic_bit
        self.setup_new_gate(gate, targets)
        return self

