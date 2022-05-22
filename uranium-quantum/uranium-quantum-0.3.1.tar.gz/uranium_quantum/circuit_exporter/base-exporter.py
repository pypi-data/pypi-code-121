class ExportException(Exception):
    pass


class BaseExporter:

    """Base class for exporting circuits from YAML format.
    to Qiskit, OpenQasm, Pyquil, Quil and Cirq."""

    def __init__(self):
        self._qubits = None

    def set_number_qubits(self, qubits):
        """Set the number of qubits in this circuit."""
        self._qubits = qubits

    def set_number_bits(self, bits):
        """Set the number of classical bits in this circuit."""
        self._bits = bits

    def process_step(self, step, circuit_name, circuit_names, add_comments, skip_non_unitary_gates):
        """Export gates present in one step from the input YAML file."""
        output = ""
        if "gates" in step:
            for gate in step["gates"]:

                controls, targets, gates, root, theta_radians, phi_radians, lambda_radians, bit, circuit_id, circuit_gate_name, circuit_power = (
                    [],
                    [],
                    [],
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None
                )
                if "controls" in gate:
                    controls = gate["controls"]
                if "targets" in gate:
                    targets = gate["targets"]
                if "gates" in gate:
                    gates = gate["gates"]
                if "root" in gate:
                    root = gate["root"]
                if "theta" in gate:
                    theta_radians = gate["theta"]
                if "phi" in gate:
                    phi_radians = gate["phi"]
                if "lambda" in gate:
                    lambda_radians = gate["lambda"]
                if "bit" in gate:
                    bit = gate["bit"]
                if "circuit_id" in gate:
                    circuit_id = gate["circuit_id"]
                    circuit_gate_name = circuit_names[circuit_id]
                if "circuit_power" in gate:
                    circuit_power = gate["circuit_power"]

                name = gate["name"]
                output += self.process_gate(
                    name,
                    circuit_name,
                    controls,
                    targets,
                    gates,
                    root,
                    theta_radians,
                    phi_radians,
                    lambda_radians,
                    bit,
                    circuit_id,
                    circuit_gate_name,
                    circuit_power,
                    add_comments,
                    skip_non_unitary_gates,
                )
                output += "\n"
        return output

    def process_gate(
        self,
        name,
        circuit_name,
        controls,
        targets,
        gates,
        root,
        theta_radians,
        phi_radians,
        lambda_radians,
        bit,
        circuit_id,
        circuit_gate_name,
        circuit_power,
        add_comments,
        skip_non_unitary_gates,
    ):
        """Create export code corresponding to a gate in yaml circuit."""

        if skip_non_unitary_gates and \
           (name == "measure-x" or name == "measure-y" or name == "measure-z" or name == "barrier"):
            return ""

        if name == "circuit":
            return self._gate_circuit(
                circuit_name, controls, targets, circuit_id, circuit_gate_name, circuit_power, add_comments,
            )
        elif name == "u3":
            return self._gate_u3(
                circuit_name, controls, targets, theta_radians, phi_radians, lambda_radians, add_comments,
            )
        elif name == "u2":
            return self._gate_u2(
                circuit_name, controls, targets, phi_radians, lambda_radians, add_comments
            )
        elif name == "u1":
            return self._gate_u1(
                circuit_name, controls, targets, lambda_radians, add_comments
            )
        elif name == "identity":
            return self._gate_identity(
                circuit_name, targets, add_comments)
        elif name == "hadamard":
            return self._gate_hadamard(
                circuit_name, controls, targets, add_comments
            )
        elif name == "hadamard-xy":
            return self._gate_hadamard_xy(
                circuit_name, controls, targets, add_comments
            )
        elif name == "hadamard-yz":
            return self._gate_hadamard_yz(
                circuit_name, controls, targets, add_comments
            )
        elif name == "hadamard-zx":
            return self._gate_hadamard_zx(
                circuit_name, controls, targets, add_comments
            )
        elif name == "pauli-x":
            return self._gate_pauli_x(
                circuit_name, controls, targets, add_comments
            )
        elif name == "pauli-y":
            return self._gate_pauli_y(
                circuit_name, controls, targets, add_comments
            )
        elif name == "pauli-z":
            return self._gate_pauli_z(
                circuit_name, controls, targets, add_comments
            )
        elif name == "pauli-x-root":
            return self._gate_pauli_x_root(
                circuit_name, controls, targets, root, add_comments
            )
        elif name == "pauli-y-root":
            return self._gate_pauli_y_root(
                circuit_name, controls, targets, root, add_comments
            )
        elif name == "pauli-z-root":
            return self._gate_pauli_z_root(
                circuit_name, controls, targets, root, add_comments
            )
        elif name == "pauli-x-root-dagger":
            return self._gate_pauli_x_root_dagger(
                circuit_name, controls, targets, root, add_comments
            )
        elif name == "pauli-y-root-dagger":
            return self._gate_pauli_y_root_dagger(
                circuit_name, controls, targets, root, add_comments
            )
        elif name == "pauli-z-root-dagger":
            return self._gate_pauli_z_root_dagger(
                circuit_name, controls, targets, root, add_comments
            )
        elif name == "t":
            return self._gate_t(
                circuit_name, controls, targets, add_comments
            )
        elif name == "t-dagger":
            return self._gate_t_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "s":
            return self._gate_s(
                circuit_name, controls, targets, add_comments
            )
        elif name == "s-dagger":
            return self._gate_s_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "rx-theta":
            return self._gate_rx_theta(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "ry-theta":
            return self._gate_ry_theta(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "rz-theta":
            return self._gate_rz_theta(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "v":
            return self._gate_v(
                circuit_name, controls, targets, add_comments
            )
        elif name == "v-dagger":
            return self._gate_v_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "h":
            return self._gate_h(
                circuit_name, controls, targets, add_comments
            )
        elif name == "h-dagger":
            return self._gate_h_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "c":
            return self._gate_c(
                circuit_name, controls, targets, add_comments
            )
        elif name == "c-dagger":
            return self._gate_c_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "p":
            return self._gate_p(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "swap":
            return self._gate_swap(
                circuit_name, controls, targets, add_comments
            )
        elif name == "swap-root":
            return self._gate_swap_root(
                circuit_name, controls, targets, root, add_comments
            )
        elif name == "swap-root-dagger":
            return self._gate_swap_root_dagger(
                circuit_name, controls, targets, root, add_comments
            )
        elif name == "iswap":
            return self._gate_iswap(
                circuit_name, controls, targets, add_comments
            )
        elif name == "fswap":
            return self._gate_fswap(
                circuit_name, controls, targets, add_comments
            )
        elif name == "sqrt-swap":
            return self._gate_sqrt_swap(
                circuit_name, controls, targets, add_comments
            )
        elif name == "sqrt-swap-dagger":
            return self._gate_sqrt_swap_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "swap-theta":
            return self._gate_swap_theta(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "xx":
            return self._gate_xx(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "yy":
            return self._gate_yy(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "zz":
            return self._gate_zz(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "xy":
            return self._gate_xy(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "molmer-sorensen":
            return self._gate_molmer_sorensen(
                circuit_name, controls, targets, add_comments
            )
        elif name == "molmer-sorensen-dagger":
            return self._gate_molmer_sorensen_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "berkeley":
            return self._gate_berkeley(
                circuit_name, controls, targets, add_comments
            )
        elif name == "berkeley-dagger":
            return self._gate_berkeley_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "ecp":
            return self._gate_ecp(
                circuit_name, controls, targets, add_comments
            )
        elif name == "ecp-dagger":
            return self._gate_ecp_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "w":
            return self._gate_w(
                circuit_name, controls, targets, add_comments
            )
        elif name == "a":
            return self._gate_a(
                circuit_name, controls, targets, theta_radians, phi_radians, add_comments
            )
        elif name == "magic":
            return self._gate_magic(
                circuit_name, controls, targets, add_comments
            )
        elif name == "magic-dagger":
            return self._gate_magic_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "givens":
            return self._gate_givens(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "cross-resonance":
            return self._gate_cross_resonance(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "cross-resonance-dagger":
            return self._gate_cross_resonance_dagger(
                circuit_name, controls, targets, theta_radians, add_comments
            )
        elif name == "qft":
            return self._gate_qft(
                circuit_name, controls, targets, add_comments
            )
        elif name == "qft-dagger":
            return self._gate_qft_dagger(
                circuit_name, controls, targets, add_comments
            )
        elif name == "barrier":
            return self._gate_barrier(
                circuit_name, add_comments
            )
        elif name == "measure-x":
            return self._gate_measure_x(
                circuit_name, targets, bit, add_comments
            )
        elif name == "measure-y":
            return self._gate_measure_y(
                circuit_name, targets, bit, add_comments
            )
        elif name == "measure-z":
            return self._gate_measure_z(
                circuit_name, targets, bit, add_comments
            )
        elif name == "aggregate":
            code = ""
            for gate in gates:
                if gate["name"] == "u3":
                    if len(code): code += "\n"
                    code += self._gate_u3(
                        circuit_name, controls, gate["targets"], gate["theta"], gate["phi"], gate["lambda"], add_comments,
                    )
                elif gate["name"] == "u2":
                    if len(code): code += "\n"
                    code += self._gate_u2(
                        circuit_name, controls, gate["targets"], gate["phi"], gate["lambda"], add_comments
                    )
                elif gate["name"] == "u1":
                    if len(code): code += "\n"
                    code += self._gate_u1(
                        circuit_name, controls, gate["targets"], gate["lambda"], add_comments
                    )
                elif gate["name"] == "identity":
                    if len(code): code += "\n"
                    code += self._gate_identity(
                        circuit_name, gate["targets"], add_comments)
                elif gate["name"] == "hadamard":
                    if len(code): code += "\n"
                    code += self._gate_hadamard(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "hadamard-xy":
                    if len(code): code += "\n"
                    code += self._gate_hadamard_xy(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "hadamard-yz":
                    if len(code): code += "\n"
                    code += self._gate_hadamard_yz(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "hadamard-zx":
                    if len(code): code += "\n"
                    code += self._gate_hadamard_zx(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "pauli-x":
                    if len(code): code += "\n"
                    code += self._gate_pauli_x(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "pauli-y":
                    if len(code): code += "\n"
                    code += self._gate_pauli_y(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "pauli-z":
                    if len(code): code += "\n"
                    code += self._gate_pauli_z(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "pauli-x-root":
                    if len(code): code += "\n"
                    code += self._gate_pauli_x_root(
                        circuit_name, controls, gate["targets"], gate["root"], add_comments
                    )
                elif gate["name"] == "pauli-y-root":
                    if len(code): code += "\n"
                    code += self._gate_pauli_y_root(
                        circuit_name, controls, gate["targets"], gate["root"], add_comments
                    )
                elif gate["name"] == "pauli-z-root":
                    if len(code): code += "\n"
                    code += self._gate_pauli_z_root(
                        circuit_name, controls, gate["targets"], gate["root"], add_comments
                    )
                elif gate["name"] == "pauli-x-root-dagger":
                    if len(code): code += "\n"
                    code += self._gate_pauli_x_root_dagger(
                        circuit_name, controls, gate["targets"], gate["root"], add_comments
                    )
                elif gate["name"] == "pauli-y-root-dagger":
                    if len(code): code += "\n"
                    code += self._gate_pauli_y_root_dagger(
                        circuit_name, controls, gate["targets"], gate["root"], add_comments
                    )
                elif gate["name"] == "pauli-z-root-dagger":
                    if len(code): code += "\n"
                    code += self._gate_pauli_z_root_dagger(
                        circuit_name, controls, gate["targets"], gate["root"], add_comments
                    )
                elif gate["name"] == "t":
                    if len(code): code += "\n"
                    code += self._gate_t(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "t-dagger":
                    if len(code): code += "\n"
                    code += self._gate_t_dagger(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "s":
                    if len(code): code += "\n"
                    code += self._gate_s(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "s-dagger":
                    if len(code): code += "\n"
                    code += self._gate_s_dagger(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "rx-theta":
                    if len(code): code += "\n"
                    code += self._gate_rx_theta(
                        circuit_name, controls, gate["targets"], gate["theta"], add_comments
                    )
                elif gate["name"] == "ry-theta":
                    if len(code): code += "\n"
                    code += self._gate_ry_theta(
                        circuit_name, controls, gate["targets"], gate["theta"], add_comments
                    )
                elif gate["name"] == "rz-theta":
                    if len(code): code += "\n"
                    code += self._gate_rz_theta(
                        circuit_name, controls, gate["targets"], gate["theta"], add_comments
                    )
                elif gate["name"] == "v":
                    if len(code): code += "\n"
                    code += self._gate_v(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "v-dagger":
                    if len(code): code += "\n"
                    code += self._gate_v_dagger(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "h":
                    if len(code): code += "\n"
                    code += self._gate_h(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "h-dagger":
                    if len(code): code += "\n"
                    code += self._gate_h_dagger(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "c":
                    if len(code): code += "\n"
                    code += self._gate_c(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "c-dagger":
                    if len(code): code += "\n"
                    code += self._gate_c_dagger(
                        circuit_name, controls, gate["targets"], add_comments
                    )
                elif gate["name"] == "p":
                    if len(code): code += "\n"
                    code += self._gate_p(
                        circuit_name, controls, gate["targets"], gate["theta"], add_comments
                    )
            return code
        raise ExportException(f"The gate {name} is not implemented in exporter code.")

    @staticmethod
    def _gate_circuit(
        circuit_name, controls, targets, circuit_id, circuit_gate_name, circuit_power, add_comments
    ):
        return ""

    @staticmethod
    def _gate_u3(
        circuit_name, controls, targets, theta_radians, phi_radians, lambda_radians, add_comments
    ):
        return ""

    @staticmethod
    def _gate_u2(circuit_name, controls, targets, phi_radians, lambda_radians, add_comments):
        return ""

    @staticmethod
    def _gate_u1(circuit_name, controls, targets, lambda_radians, add_comments):
        return ""

    @staticmethod
    def _gate_identity(circuit_name, targets, add_comments):
        return ""

    @staticmethod
    def _gate_hadamard(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_hadamard_xy(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_hadamard_yz(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_hadamard_zx(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_x(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_y(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_z(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_x_root(circuit_name, controls, targets, root, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_y_root(circuit_name, controls, targets, root, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_z_root(circuit_name, controls, targets, root, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_x_root_dagger(circuit_name, controls, targets, root, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_y_root_dagger(circuit_name, controls, targets, root, add_comments):
        return ""

    @staticmethod
    def _gate_pauli_z_root_dagger(circuit_name, controls, targets, root, add_comments):
        return ""

    @staticmethod
    def _gate_t(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_t_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_rx_theta(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_ry_theta(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_rz_theta(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_s(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_s_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_v(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_v_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_h(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_h_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_c(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_c_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_p(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_swap(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_swap_root(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_swap_root_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_iswap(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_fswap(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_swap_theta(circuit_name, controls, targets, phi, add_comments):
        return ""

    @staticmethod
    def _gate_sqrt_swap(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_sqrt_swap_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_xx(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_yy(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_zz(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_xy(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_molmer_sorensen(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_molmer_sorensen_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_berkeley(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_berkeley_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_ecp(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_ecp_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_w(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_a(circuit_name, controls, targets, theta, phi, add_comments):
        return ""

    @staticmethod
    def _gate_magic(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_magic_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_givens(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_measure_x(circuit_name, target, classic_bit, add_comments):
        return ""

    @staticmethod
    def _gate_cross_resonance(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_cross_resonance_dagger(circuit_name, controls, targets, theta, add_comments):
        return ""

    @staticmethod
    def _gate_measure_y(circuit_name, target, classic_bit, add_comments):
        return ""

    @staticmethod
    def _gate_measure_z(circuit_name, target, classic_bit, add_comments):
        return ""

    @staticmethod
    def _gate_aggregate(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_qft(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_qft_dagger(circuit_name, controls, targets, add_comments):
        return ""

    @staticmethod
    def _gate_barrier(circuit_name, add_comments):
        return ""