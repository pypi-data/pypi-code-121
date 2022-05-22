import importlib

BaseExporter = importlib.import_module("uranium_quantum.circuit_exporter.base-exporter")


class Exporter(BaseExporter.BaseExporter):
    def _define_import_code_section(self):
        return f"\
import cirq\n\
import numpy as np\n\
\n\
q = [cirq.NamedQubit('q' + str(i)) for i in range({self._qubits})]\n\
\n"

    def _define_u3_gates_code_section(self):
        return "\
# define the u3 gate\n\
def u3(theta_radians, phi_radians, lambda_radians):\n\
    return cirq.MatrixGate(np.array([[np.cos(theta_radians/2), -np.exp(1j * lambda_radians) * np.sin(theta_radians/2)], [np.exp(1j * phi_radians) * np.sin(theta_radians/2), np.exp(1j * lambda_radians+1j * phi_radians) * np.cos(theta_radians/2)]]))\n\
\n"

    def _define_u2_gates_code_section(self):
        return "\
# define the u2 gate\n\
def u2(phi_radians, lambda_radians):\n\
    return cirq.MatrixGate(np.array([[1/np.sqrt(2), -np.exp(1j * lambda_radians) * 1/np.sqrt(2)], [np.exp(1j * phi_radians) * 1/np.sqrt(2), np.exp(1j * lambda_radians + 1j * phi_radians) * 1/np.sqrt(2)]]))\n\
\n"

    def _define_u1_gates_code_section(self):
        return "\
def u1(lambda_radians):\n\
    return cirq.MatrixGate(np.array([[1, 0], [0, np.exp(1j * lambda_radians)]]))\n\
\n"

    def _define_crtl_u1(self):
        return "\
# define ctrl-u1 gate\n\
def cu1(lambda_radians):\n\
    return cirq.MatrixGate(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, np.exp(1j * lambda_radians)]]))\n\
\n"

    def _define_crtl_u2(self):
        return "\
# define ctrl-u2 gate\n\
def cu2(phi_radians, lambda_radians):\n\
    return cirq.MatrixGate(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1/np.sqrt(2), -np.exp(1j * lambda_radians) * 1/np.sqrt(2)], [0, 0, np.exp(1j * phi_radians) * 1/np.sqrt(2), np.exp(1j * lambda_radians + 1j * phi_radians) * 1/np.sqrt(2)]]))\n\
\n"

    def _define_crtl_u3(self):
        return "\
# define ctrl-u3 gate\n\
def cu3(theta_radians, phi_radians, lambda_radians):\n\
    return cirq.MatrixGate(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, np.cos(theta_radians/2), -np.exp(1j * lambda_radians) * np.sin(theta_radians/2)], [0, 0, np.exp(1j * phi_radians) * np.sin(theta_radians/2), np.exp(1j * lambda_radians+1j * phi_radians) * np.cos(theta_radians/2)]]))\n\
\n"

    def start_circuit_code(self, circuit_name):
        return (
            self._define_import_code_section()
            + "\n"
            + self._define_u3_gates_code_section()
            + "\n"
            + self._define_u2_gates_code_section()
            + "\n"
            + self._define_u1_gates_code_section()
            + "\n"
            + self._define_crtl_u1()
            + "\n"
            + self._define_crtl_u2()
            + "\n"
            + self._define_crtl_u3()
            + "\n"
            + "circuit = cirq.Circuit(\n\n"
        )

    def end_circuit_code(self):
        return f"\
)\n\
\n\
simulator = cirq.Simulator()\n\
simulator.run(circuit, repetitions=1000)\n"

    @staticmethod
    def _gate_u3(
        target, theta_radians, phi_radians, lambda_radians, add_comments=True
    ):
        out = "    # u3 gate\n" if add_comments else ""
        out += (
            f"    u3({theta_radians}, {phi_radians}, {lambda_radians})(q[{target}]),\n"
        )
        return out

    @staticmethod
    def _gate_u2(target, phi_radians, lambda_radians, add_comments=True):
        out = "    # u2 gate\n" if add_comments else ""
        out += f"    u2({phi_radians}, {lambda_radians})(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_u1(target, lambda_radians, add_comments=True):
        out = "    # u1 gate\n" if add_comments else ""
        out += f"    u1({lambda_radians})(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_identity(target, add_comments=True):
        out = "    # identity gate\n" if add_comments else ""
        out += f"    cirq.I(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_hadamard(target, add_comments=True):
        out = "    # hadamard gate\n" if add_comments else ""
        out += f"    cirq.H(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_pauli_x(target, add_comments=True):
        out = "    # pauli-x gate\n" if add_comments else ""
        out += f"    cirq.X(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_pauli_y(target, add_comments=True):
        out = "    # pauli-y gate\n" if add_comments else ""
        out += f"    cirq.Y(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_pauli_z(target, add_comments=True):
        out = "    # pauli-z gate\n" if add_comments else ""
        out += f"    cirq.Z(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_pauli_x_root(target, root, add_comments=True):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# pauli-x-root gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_pauli_y_root(target, root, add_comments=True):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# pauli-y-root gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_pauli_z_root(target, root, add_comments=True):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# pauli-z-root gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_pauli_x_root_dagger(target, root, add_comments=True):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# pauli-x-root-dagger gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_pauli_y_root_dagger(target, root, add_comments=True):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# pauli-y-root-dagger gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_pauli_z_root_dagger(target, root, add_comments=True):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# pauli-z-root-dagger gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_sqrt_not(target, add_comments=True):
        out = "    # sqrt-not gate\n" if add_comments else ""
        out += f"    (cirq.X**(1/2))(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_t(target, add_comments=True):
        out = "    # t gate\n" if add_comments else ""
        out += f"    cirq.T(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_t_dagger(target, add_comments=True):
        out = "    # t-dagger gate\n" if add_comments else ""
        out += f"    u1(-np.pi / 4)(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_rx_theta(target, theta, add_comments=True):
        out = "    # rx-theta gate\n" if add_comments else ""
        out += f"    cirq.rx(0)(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ry_theta(target, theta, add_comments=True):
        out = "    # ry-theta gate\n" if add_comments else ""
        out += f"    cirq.ry(0)(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_rz_theta(target, theta, add_comments=True):
        out = "    # rz-theta gate\n" if add_comments else ""
        out += f"    cirq.rz(0)(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_s(target, add_comments=True):
        out = "    # s gate\n" if add_comments else ""
        out += f"    cirq.S(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_s_dagger(target, add_comments=True):
        out = "    # s-dagger gate\n" if add_comments else ""
        out += f"    u1(-np.pi / 2)(q[{target}]),\n"
        return out

    @staticmethod
    def _gate_swap(target, target2, add_comments=True):  ##
        out = "    # swap gate\n" if add_comments else ""
        out += f"    cirq.SWAP(q[{target}], q[{target2}]),\n"
        return out

    @staticmethod
    def _gate_iswap(target, target2, add_comments=True):
        out = "    # iswap gate\n" if add_comments else ""
        out += f"    cirq.ISWAP(q[{target}], q[{target2}]),\n"
        return out

    @staticmethod
    def _gate_swap_theta(target, target2, phi, add_comments=True):
        raise BaseExporter.ExportException("The swap-theta gate is not implemented.")

    @staticmethod
    def _gate_sqrt_swap(target, target2, add_comments=True):
        out = "    # sqrt-swap gate\n" if add_comments else ""
        out += f"    (cirq.SWAP**(1/2))(q[{target}], q[{target2}]),\n"
        return out

    @staticmethod
    def _gate_xx(target, target2, theta, add_comments=True):
        out = "# xx gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_yy(target, target2, theta, add_comments=True):
        out = "# yy gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_zz(target, target2, theta, add_comments=True):
        out = "# zz gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_ctrl_hadamard(control, target, controlstate, add_comments=True):
        out = "    # ctrl-hadamard gate\n" if add_comments else ""
        out += f"    cirq.H.controlled().on(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_u3(
        control,
        target,
        controlstate,
        theta_radians,
        phi_radians,
        lambda_radians,
        add_comments=True,
    ):
        out = "    # ctrl-u3 gate\n" if add_comments else ""
        out += f"    cu3({theta_radians}, {phi_radians}, {lambda_radians})(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_u2(
        control, target, controlstate, phi_radians, lambda_radians, add_comments=True
    ):
        out = "    # ctrl-u2 gate\n" if add_comments else ""
        out += f"    cu2({phi_radians}, {lambda_radians})(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_u1(
        control, target, controlstate, lambda_radians, add_comments=True
    ):
        out = "    # ctrl-u1 gate\n" if add_comments else ""
        out += f"    cu1({lambda_radians})(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_t(control, target, controlstate, add_comments=True):
        out = "    # ctrl-t gate\n" if add_comments else ""
        out += f"    cu1(np.pi / 4)(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_t_dagger(control, target, controlstate, add_comments=True):
        out = "    # ctrl-t-dagger gate\n" if add_comments else ""
        out += f"    cu1(-np.pi / 4)(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_pauli_x(control, target, controlstate, add_comments=True):
        out = "    # ctrl-pauli-x gate\n" if add_comments else ""
        out += f"    cirq.CNOT(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_pauli_y(control, target, controlstate, add_comments=True):
        out = "    # ctrl-pauli-y gate\n" if add_comments else ""
        out += f"    cirq.Y.controlled().on(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_pauli_z(control, target, controlstate, add_comments=True):
        out = "    # ctrl-pauli-z gate\n" if add_comments else ""
        out += f"    cirq.CZ(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_pauli_x_root(
        control, target, controlstate, root, add_comments=True
    ):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# ctrl-pauli-x-root gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_ctrl_pauli_y_root(
        control, target, controlstate, root, add_comments=True
    ):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# ctrl-pauli-y-root gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_ctrl_pauli_z_root(
        control, target, controlstate, root, add_comments=True
    ):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# ctrl-pauli-z-root gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_ctrl_pauli_x_root_dagger(
        control, target, controlstate, root, add_comments=True
    ):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# ctrl-pauli-x-root-dagger gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_ctrl_pauli_y_root_dagger(
        control, target, controlstate, root, add_comments=True
    ):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# ctrl-pauli-y-root-dagger gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_ctrl_pauli_z_root_dagger(
        control, target, controlstate, root, add_comments=True
    ):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
        out = "# ctrl-pauli-z-root-dagger gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_ctrl_sqrt_not(control, target, controlstate, add_comments=True):
        out = "    # ctrl-sqrt-not gate\n" if add_comments else ""
        out += f"    (cirq.X**(1/2)).controlled().on(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_rx_theta(
        control, target, controlstate, theta_radians, add_comments=True
    ):
        out = "    # ctrl-rx-theta gate\n" if add_comments else ""
        out += f"    cirq.rx({theta_radians}).controlled().on(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_ry_theta(
        control, target, controlstate, theta_radians, add_comments=True
    ):
        out = "    # ctrl-ry-theta gate\n" if add_comments else ""
        out += f"    cirq.ry({theta_radians}).controlled().on(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_rz_theta(
        control, target, controlstate, theta_radians, add_comments=True
    ):
        out = "    # ctrl-rz-theta gate\n" if add_comments else ""
        out += f"    cirq.rz({theta_radians}).controlled().on(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_s(control, target, controlstate, add_comments=True):
        out = "    # ctrl-s gate\n" if add_comments else ""
        out += f"    cu1(np.pi / 2)(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_ctrl_s_dagger(control, target, controlstate, add_comments=True):
        out = "    # ctrl-s-dagger gate\n" if add_comments else ""
        out += f"    cu1(-np.pi / 2)(q[{control}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_toffoli(
        control, control2, target, controlstate, controlstate2, add_comments=True
    ):
        out = "    # toffoli gate\n" if add_comments else ""
        out += f"    cirq.CSWAP(q[{control}], q[{control2}], q[{target}]),\n"
        return out

    @staticmethod
    def _gate_fredkin(control, target, target2, controlstate, add_comments=True):
        out = "    # fredkin gate\n" if add_comments else ""
        out += f"    cirq.CCX(q[{control}], q[{target}], q[{target2}]),\n"
        return out

    @staticmethod
    def _gate_measure_x(target, classic_bit, add_comments=True):
        raise BaseExporter.ExportException("The measure-x gate is not implemented.")

    @staticmethod
    def _gate_measure_y(target, classic_bit, add_comments=True):
        raise BaseExporter.ExportException("The measure-y gate is not implemented.")

    @staticmethod
    def _gate_measure_z(target, classic_bit, add_comments=True):
        out = "    # measure-z gate\n" if add_comments else ""
        out += f"    cirq.measure(q[{target}], key='c{classic_bit}'),\n"
        return out
