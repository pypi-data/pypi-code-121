import importlib

BaseExporter = importlib.import_module("uranium_quantum.circuit_exporter.base-exporter")


class Exporter(BaseExporter.BaseExporter):
    def _define_import_code_section(self):
        return f"\
import numpy as np\n\
from pyquil import Program, get_qc\n\
from pyquil.gates import CNOT, CCNOT, CZ, I, H, CPHASE, PHASE, RX, RY, RZ, S, CSWAP, ISWAP, MEASURE, PSWAP, SWAP, T, X, Y, Z\n\
from pyquil.quilatom import Parameter, quil_sin, quil_cos, quil_sqrt, quil_exp\n\
from pyquil.quilbase import DefGate\n\
p = Program()\n\
ro = p.declare('ro', memory_type='BIT', memory_size={self._bits})\n\
"

    def _define_sqrt_not_gate_code_section(self):
        return "\
# define the sqrt-not gate\n\
srn_sqrt_not_array = np.array([[0.5 + 0.5j, 0.5 - 0.5j], [0.5 - 0.5j, 0.5 + 0.5j]])\n\
srn_sqrt_not_defgate = DefGate('srn', srn_sqrt_not_array)\n\
sqrt_not = srn_sqrt_not_defgate.get_constructor()\n\
p.inst(srn_sqrt_not_defgate)\n\
"

    def _define_u3_gates_code_section(self):
        return "\
# define the u3 gate\n\
theta_radians = Parameter('theta')\n\
phi_radians = Parameter('phi')\n\
lambda_radians = Parameter('lambda')\n\
u3_array = np.array([[quil_cos(theta_radians/2), -quil_exp(1j * lambda_radians) * quil_sin(theta_radians/2)], [quil_exp(1j * phi_radians) * quil_sin(theta_radians/2), quil_exp(1j * lambda_radians+1j * phi_radians) * quil_cos(theta_radians/2)]])\n\
u3_defgate = DefGate('u3', u3_array, [theta_radians, phi_radians, lambda_radians])\n\
u3 = u3_defgate.get_constructor()\n\
p.inst(u3_defgate)\n"

    def _define_u2_gates_code_section(self):
        return "\
# define the u2 gate\n\
phi_radians = Parameter('phi')\n\
lambda_radians = Parameter('lambda')\n\
u2_array = np.array([[1/quil_sqrt(2), -quil_exp(1j * lambda_radians) * 1/quil_sqrt(2)], [quil_exp(1j * phi_radians) * 1/quil_sqrt(2), quil_exp(1j * lambda_radians+1j * phi_radians) * 1/quil_sqrt(2)]])\n\
u2_defgate = DefGate('u2', u2_array, [phi_radians, lambda_radians])\n\
u2 = u2_defgate.get_constructor()\n\
p.inst(u2_defgate)\n"

    def _define_sqrt_swap_code_section(self):
        return "\
# define the sqrt-swap gate\n\
sqrt_swap_array = np.array([[1, 0, 0, 0], [0, 0.5 * (1 + 1j), 0.5 * (1 - 1j), 0], [0, 0.5 * (1 - 1j), 0.5 * (1 + 1j), 0], [0, 0, 0, 1]])\n\
sqrt_swap_defgate = DefGate('sqrt_swap', sqrt_swap_array)\n\
sqrt_swap = sqrt_swap_defgate.get_constructor()\n\
p.inst(sqrt_swap_defgate)\n"

    def _define_crtl_hadamard(self):
        return "\
# define the ctrl-hadamard gate\n\
ch_array = np.array([[1, 0, 0, 0], [0, 1, 0, 0],  [0, 0, 1/np.sqrt(2), 1/np.sqrt(2)], [0, 0, 1/np.sqrt(2), -1/np.sqrt(2)]])\n\
ch_defgate = DefGate('ch', ch_array)\n\
ch = ch_defgate.get_constructor()\n"

    def _define_crtl_y(self):
        return "\
# define ctrl-y gate\n\
cy_array = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, -1j], [0, 0, 1j, 0]])\n\
cy_defgate = DefGate('cy', cy_array)\n\
cy = cy_defgate.get_constructor()\n"

    def _define_crtl_sqrt_not(self):
        return "\
# define ctrl-sqrt-not gate\n\
csqrt_not_array = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0.5+0.5j, 0.5-0.5j], [0, 0, 0.5-0.5j, 0.5+0.5j]])\n\
csqrt_not_defgate = DefGate('csqrt_not', csqrt_not_array)\n\
csqrt_not = csqrt_not_defgate.get_constructor()\n"

    def _define_crtl_rx(self):
        return "\
# define ctrl-rx-theta gate\n\
crx_array = np.array([[ 1, 0, 0, 0 ], [ 0, 1, 0, 0 ], [ 0, 0, quil_cos(theta_radians / 2), -1j * quil_sin(theta_radians / 2) ], [ 0, 0, -1j * quil_sin(theta_radians / 2), quil_cos(theta_radians / 2) ]])\n\
crx_defgate = DefGate('crx', crx_array, [theta_radians])\n\
crx = crx_defgate.get_constructor()\n\
p.inst(crx_defgate)\n"

    def _define_crtl_ry(self):
        return "\
# define ctrl-ry-theta gate\n\
cry_array = np.array([[ 1, 0, 0, 0 ],[ 0, 1, 0, 0 ],[ 0, 0, quil_cos(theta_radians / 2), -1 * quil_sin(theta_radians / 2) ], [ 0, 0, quil_sin(theta_radians / 2), quil_cos(theta_radians / 2) ]])\n\
cry_defgate = DefGate('cry', cry_array, [theta_radians])\n\
cry = cry_defgate.get_constructor()\n"

    def _define_crtl_rz(self):
        return "\
# define ctrl-rz-theta gate\n\
crz_array = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, quil_cos(phi_radians / 2) - 1j * quil_sin(phi_radians / 2), 0], [0, 0, 0, quil_cos(phi_radians / 2) + 1j * quil_sin(phi_radians / 2)]])\n\
crz_defgate = DefGate('crz', crz_array, [phi_radians])\n\
crz = crz_defgate.get_constructor()\n\
p.inst(crz_defgate)\n"

    def _define_crtl_u2(self):
        return "\
# define ctrl-u2 gate\n\
phi_radians = Parameter('phi')\n\
lambda_radians = Parameter('lambda')\n\
cu2_array = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0,  0, 1/quil_sqrt(2), -quil_exp(1j * lambda_radians) * 1/quil_sqrt(2)], [0, 0, quil_exp(1j * phi_radians) * 1/quil_sqrt(2), quil_exp(1j * lambda_radians+1j * phi_radians) * 1/quil_sqrt(2)]])\n\
cu2_defgate = DefGate('cu2', cu2_array, [phi_radians, lambda_radians])\n\
cu2 = cu2_defgate.get_constructor()\n\
p.inst(cu2_defgate)\n"

    def _define_crtl_u3(self):
        return "\
# define ctrl-u3 gate\n\
theta_radians = Parameter('theta')\n\
phi_radians = Parameter('phi')\n\
lambda_radians = Parameter('lambda')\n\
cu3_array = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0,  0, quil_cos(theta_radians/2), -quil_exp(1j * lambda_radians) * quil_sin(theta_radians/2)], [0, 0, quil_exp(1j * phi_radians) * quil_sin(theta_radians/2),quil_exp(1j * lambda_radians+1j * phi_radians) * quil_cos(theta_radians/2)]])\n\
cu3_defgate = DefGate('cu3', cu3_array, [theta_radians, phi_radians, lambda_radians])\n\
cu3 = cu3_defgate.get_constructor()\n\
p.inst(cu3_defgate)\n"

    def start_circuit_code(self, circuit_name):
        return (
            self._define_import_code_section()
            + "\n"
            + self._define_sqrt_not_gate_code_section()
            + "\n"
            + self._define_u3_gates_code_section()
            + "\n"
            + self._define_u2_gates_code_section()
            + "\n"
            + self._define_sqrt_swap_code_section()
            + "\n"
            + self._define_crtl_hadamard()
            + "\n"
            + self._define_crtl_y()
            + "\n"
            + self._define_crtl_sqrt_not()
            + "\n"
            + self._define_crtl_rx()
            + "\n"
            + self._define_crtl_ry()
            + "\n"
            + self._define_crtl_rz()
            + "\n"
            + self._define_crtl_u2()
            + "\n"
            + self._define_crtl_u3()
            + "\n"
        )

    def end_circuit_code(self):
        return f'\
qc = get_qc("8q-qvm")\n\
p.wrap_in_numshots_loop(1000)\n\
print(qc.run(p))\n\
'

    @staticmethod
    def _gate_u3(
        target, theta_radians, phi_radians, lambda_radians, add_comments=True
    ):
        out = "# u3 gate\n" if add_comments else ""
        out += (
            f"p.inst(u3({theta_radians}, {phi_radians}, {lambda_radians})({target}))\n"
        )
        return out

    @staticmethod
    def _gate_u2(target, phi_radians, lambda_radians, add_comments=True):
        out = "# u2 gate\n" if add_comments else ""
        out += f"p.inst(u2({phi_radians}, {lambda_radians})({target}))\n"
        return out

    @staticmethod
    def _gate_u1(target, lambda_radians, add_comments=True):
        out = "# u1 gate\n" if add_comments else ""
        out += f"p.inst(PHASE({lambda_radians}, {target}))\n"
        return out

    @staticmethod
    def _gate_identity(target, add_comments=True):
        out = "# identity gate\n" if add_comments else ""
        out += f"p.inst(I({target}))\n"
        return out

    @staticmethod
    def _gate_hadamard(target, add_comments=True):
        out = "# hadamard gate\n" if add_comments else ""
        out += f"p.inst(H({target}))\n"
        return out

    @staticmethod
    def _gate_pauli_x(target, add_comments=True):
        out = "# pauli-x gate\n" if add_comments else ""
        out += f"p.inst(X({target}))\n"
        return out

    @staticmethod
    def _gate_pauli_y(target, add_comments=True):
        out = "# pauli-y gate\n" if add_comments else ""
        out += f"p.inst(Y({target}))\n"
        return out

    @staticmethod
    def _gate_pauli_z(target, add_comments=True):
        out = "# pauli-z gate\n" if add_comments else ""
        out += f"p.inst(Z({target}))\n"
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
        out = "# sqrt-not gate\n" if add_comments else ""
        out += f"p.inst(sqrt_not({target}))\n"
        return out

    @staticmethod
    def _gate_t(target, add_comments=True):
        out = "# t gate\n" if add_comments else ""
        out += f"p.inst(T({target}))\n"
        return out

    @staticmethod
    def _gate_t_dagger(target, add_comments=True):
        out = "# t-dagger gate\n" if add_comments else ""
        out = f"p.inst(PHASE(-np.pi/4, {target}))\n"
        return out

    @staticmethod
    def _gate_rx_theta(target, theta, add_comments=True):
        out = "# rx-theta gate\n" if add_comments else ""
        out += f"p.inst(RX({theta}, {target}))\n"
        return out

    @staticmethod
    def _gate_ry_theta(target, theta, add_comments=True):
        out = "# ry-theta gate\n" if add_comments else ""
        out += f"p.inst(RY({theta}, {target}))\n"
        return out

    @staticmethod
    def _gate_rz_theta(target, theta, add_comments=True):
        out = "# rz-theta gate\n" if add_comments else ""
        out += f"p.inst(RZ({theta}, {target}))\n"
        return out

    @staticmethod
    def _gate_s(target, add_comments=True):
        out = "# s gate\n" if add_comments else ""
        out += f"p.inst(S({target}))\n"
        return out

    @staticmethod
    def _gate_s_dagger(target, add_comments=True):
        out = "# s-dagger gate\n" if add_comments else ""
        out += f"p.inst(PHASE(-np.pi/2, {target}))\n"
        return out

    @staticmethod
    def _gate_swap(target, target2, add_comments=True):
        out = "# swap gate\n" if add_comments else ""
        out += f"p.inst(SWAP({target}, {target2}))\n"
        return out

    @staticmethod
    def _gate_iswap(target, target2, add_comments=True):
        out = "# iswap gate\n" if add_comments else ""
        out += f"p.inst(ISWAP({target}, {target2}))\n"
        return out

    @staticmethod
    def _gate_swap_theta(target, target2, phi, add_comments=True):
        out = "# swap-theta gate\n" if add_comments else ""
        out += f"p.inst(PSWAP({phi}, {target}, {target2}))\n"
        return out

    @staticmethod
    def _gate_sqrt_swap(target, target2, add_comments=True):
        out = "# sqrt-swap gate\n" if add_comments else ""
        out += f"p.inst(sqrt_swap({target}, {target2}))\n"
        return out

    @staticmethod
    def _gate_xx(target, target2, theta, add_comments=True):
        # TODO
        out = "# xx gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_yy(target, target2, theta, add_comments=True):
        # TODO
        out = "# yy gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_zz(target, target2, theta, add_comments=True):
        # TODO
        out = "# zz gate\n" if add_comments else ""
        return out

    @staticmethod
    def _gate_ctrl_hadamard(control, target, controlstate, add_comments=True):
        out = "# ctrl-hadamard gate\n" if add_comments else ""
        out += f"p.inst(ch({control}, {target}))\n"
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
        out = "# ctrl-u3 gate\n" if add_comments else ""
        out += f"p.inst(cu3({theta_radians}, {phi_radians}, {lambda_radians})({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_u2(
        control, target, controlstate, phi_radians, lambda_radians, add_comments=True
    ):
        out = "# ctrl-u2 gate\n" if add_comments else ""
        out += f"p.inst(cu2({phi_radians}, {lambda_radians})({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_u1(
        control, target, controlstate, lambda_radians, add_comments=True
    ):
        out = "# ctrl-u1 gate\n" if add_comments else ""
        out += f"p.inst(CPHASE({lambda_radians}, {control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_t(control, target, controlstate, add_comments=True):
        out = "# ctrl-t gate\n" if add_comments else ""
        out += f"p.inst(CPHASE(np.pi / 4, {control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_t_dagger(control, target, controlstate, add_comments=True):
        out = "# ctrl-t-dagger gate\n" if add_comments else ""
        out += f"p.inst(CPHASE(-np.pi / 4, {control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_pauli_x(control, target, controlstate, add_comments=True):
        out = "# ctrl-pauli-x gate\n" if add_comments else ""
        out += f"p.inst(CNOT({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_pauli_y(control, target, controlstate, add_comments=True):
        out = "# ctrl-pauli-y gate\n" if add_comments else ""
        out += f"p.inst(cy({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_pauli_z(control, target, controlstate, add_comments=True):
        out = "# ctrl-pauli-z gate\n" if add_comments else ""
        out += f"p.inst(CZ({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_pauli_x_root(
        control, target, controlstate, root, add_comments=True
    ):
        # TODO
        root = f"(2**{root[4:]})" if '^' in root else root[2:]
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
        out = "# ctrl-sqrt-not gate\n" if add_comments else ""
        out += f"p.inst(csqrt_not({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_rx_theta(
        control, target, controlstate, theta_radians, add_comments=True
    ):
        out = "# ctrl-rx-theta gate\n" if add_comments else ""
        out += f"p.inst(crx({theta_radians})({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_ry_theta(
        control, target, controlstate, theta_radians, add_comments=True
    ):
        out = "# ctrl-ry-theta gate\n" if add_comments else ""
        out += f"p.inst(cry({theta_radians})({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_rz_theta(
        control, target, controlstate, theta_radians, add_comments=True
    ):
        out = "# ctrl-rz-theta gate\n" if add_comments else ""
        out += f"p.inst(crz({theta_radians})({control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_s(control, target, controlstate, add_comments=True):
        out = "# ctrl-s gate\n" if add_comments else ""
        out += f"p.inst(CPHASE(np.pi / 2, {control}, {target}))\n"
        return out

    @staticmethod
    def _gate_ctrl_s_dagger(control, target, controlstate, add_comments=True):
        out = "# ctrl-s-dagger gate\n" if add_comments else ""
        out += f"p.inst(CPHASE(-np.pi / 2, {control}, {target}))\n"
        return out

    @staticmethod
    def _gate_toffoli(
        control, control2, target, controlstate, controlstate2, add_comments=True
    ):
        out = "# toffoli gate\n" if add_comments else ""
        out += f"p.inst(CCNOT({control}, {control2}, {target}))\n"
        return out

    @staticmethod
    def _gate_fredkin(control, target, target2, controlstate, add_comments=True):
        out = "# fredkin gate\n" if add_comments else ""
        out += f"p.inst(CSWAP({control}, {target}, {target2}))\n"
        return out

    @staticmethod
    def _gate_measure_x(target, classic_bit, add_comments=True):
        raise BaseExporter.ExportException("The measure-x gate is not implemented.")

    @staticmethod
    def _gate_measure_y(target, classic_bit, add_comments=True):
        raise BaseExporter.ExportException("The measure-y gate is not implemented.")

    @staticmethod
    def _gate_measure_z(target, classic_bit, add_comments=True):
        out = "# measure-z gate\n" if add_comments else ""
        out += f"p.inst(MEASURE({target}, ro[{classic_bit}]))\n"
        return out
