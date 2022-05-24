import numpy as np
from quantumsymmetry.core import apply_encoding, get_character_table, HartreeFock_ket, find_ground_state_irrep, get_molecule_name, make_clifford_tableau, find_symmetry_generators
from openfermion import QubitOperator, FermionOperator, jordan_wigner, utils, linalg
from qiskit import opflow, quantum_info
from qiskit_nature.operators.second_quantization import FermionicOp
from qiskit_nature.converters.second_quantization import QubitConverter
from pyscf import gto, scf, symm, ao2mo

def apply_encoding_mapper(operator, suppress_none=True):
    print('!')
    apply_encoding(operator = operator, encoding = SymmetryAdaptedEncoding_encoding, output_format = 'qiskit')

def convert_encoding(operators, suppress_none=True, check_commutes=False, num_particles=None, sector_locator=None):
    if type(operators) == FermionicOp:
        print('Type: FermionicOp')
        operator = operators
        output = 0
        print('The original operator is:')
        print(operator)
        operator = fix_qubit_order_convention(operator)
        print('The operator to encode is:')
        print(operator)
        encoded_operator = apply_encoding(operator = operator, encoding = SymmetryAdaptedEncoding_encoding, output_format = 'qiskit')
        print('The encoded operator is:')
        print(encoded_operator)
        if type(encoded_operator) != int and type(encoded_operator) != None:
            print('Length of operators is')
            print(encoded_operator.num_qubits)
            output = encoded_operator
    elif type(operators) == list:
        output = list()
        print('Type: list')
        for operator in operators:
            print('The original operator is:')
            print(operator)
            operator = fix_qubit_order_convention(operator)
            print('The operator to encode is:')
            print(operator)
            encoded_operator = apply_encoding(operator = operator, encoding = SymmetryAdaptedEncoding_encoding, output_format = 'qiskit')
            print('The encoded operator is:')
            print(encoded_operator)
            if type(encoded_operator) != int and type(encoded_operator) != None:
                print('Length of operators is')
                print(encoded_operator.num_qubits)
                output.append(encoded_operator)
    return output

def transform(driver, operators):
    output1 = driver
    output2 = list()
    if operators == None:
        return output1, None
    for operator in operators:
        print('The original operator is:')
        print(operator)
        operator = fix_qubit_order_convention(operator)
        print('The operator to encode is:')
        print(operator)
        encoded_operator = apply_encoding(operator = operator, encoding = SymmetryAdaptedEncoding_encoding, output_format = 'qiskit')
        print('The encoded operator is:')
        print(encoded_operator)
        if type(encoded_operator) != int and type(encoded_operator) != None:
            print('Length of operators is')
            print(output1.num_qubits)
            output2.append(encoded_operator)
    return output1, output2

def fix_qubit_order_convention(input):
    output = 0
    input.display_format="dense"
    N = input.register_length
    input_list = input.to_list()
    for x in range(len(input_list)):
        output_label = str()
        input_label = input_list[x][0]
        input_label = input_label[::-1]
        for j in range(N//2):
            output_label += input_label[j]
            output_label += input_label[N//2 + j]
        output += FermionicOp([(output_label[::-1], input_list[x][1])], display_format='dense')
    return output
    
def SymmetryAdaptedEncodingQubitConverter(encoding):
    global SymmetryAdaptedEncoding_encoding
    SymmetryAdaptedEncoding_encoding = encoding
    qubit_transformation = QubitConverter(apply_encoding_mapper)
    qubit_transformation.convert_match = convert_encoding
    qubit_transformation.mapper.map = apply_encoding_mapper
    qubit_transformation.convert = convert_encoding
    return qubit_transformation

def SymmetryAdaptedEncodingHartreeFock(atom, basis, charge = 0, spin = 0, irrep = None):
    mol = gto.Mole()
    mol.atom = atom
    mol.symmetry = True
    mol.basis = basis
    mol.charge = charge
    mol.spin = spin
    mol.verbose = 0
    mol.build()
    if mol.groupname == 'Dooh' or mol.groupname == 'SO3':
        mol.symmetry = 'D2h'
        mol.build()
    if mol.groupname == 'Coov':
        mol.symmetry = 'C2v'
        mol.build()
    mf = scf.RHF(mol)
    mf.kernel()
    
    label_orb_symm = symm.label_orb_symm(mol, mol.irrep_name, mol.symm_orb, mf.mo_coeff)
    character_table, conj_labels, irrep_labels, conj_descriptions = get_character_table(mol.groupname)
    if irrep == None:
        irrep =  find_ground_state_irrep(label_orb_symm, mf.mo_occ, character_table, irrep_labels)
    molecule_name = get_molecule_name(mol)
    symmetry_generator_labels, symmetry_generators_strings, target_qubits, symmetry_generators, signs, descriptions = find_symmetry_generators(mol, mf, irrep)
    tableau, tableau_signs = make_clifford_tableau(symmetry_generators, signs, target_qubits)

    n = len(tableau)//2
    ZZ_block = (-tableau[:n, :n] + 1)//2
    sign_vector = (-tableau_signs[:n]+ 1)//2
    b = HartreeFock_ket(mf.mo_occ)
    string_b = f'{b:0{n}b}'
    b_list = list(string_b)[::-1]
    for i in range(len(b_list)):
        b_list[i] = int(b_list[i])
    c_list = np.matmul(ZZ_block, b_list + sign_vector)[::-1] % 2
    string_c = ''.join(str(x) for x in c_list)
    target_qubits.sort(reverse = True)
    for qubit in target_qubits:
        l = len(string_c)
        string_c = string_c[:l - qubit - 1] + string_c[l - qubit:]

    from qiskit.circuit.quantumcircuit import QuantumCircuit
    output = QuantumCircuit(len(string_c))
    for i, bit in enumerate(string_c[::-1]):
        if bit == '1':
            output.x(i)
    return output