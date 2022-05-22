import click
import importlib
import yaml

QiskitExporter = importlib.import_module("uranium_quantum.circuit_exporter.qiskit-exporter")
PyquilExporter = importlib.import_module("uranium_quantum.circuit_exporter.pyquil-exporter")
QuilExporter = importlib.import_module("uranium_quantum.circuit_exporter.quil-exporter")
CirqExporter = importlib.import_module("uranium_quantum.circuit_exporter.cirq-exporter")


def get_number_qubits(yaml):
    """Extract the number of qubits in yaml circuit."""
    qubits = 0
    if "steps" in yaml.keys():
        for step in yaml["steps"]:
            if "gates" in step:
                for gate in step["gates"]:
                    if "controls" in gate:
                        for ctrl_info in gate["controls"]:
                            qubits = max(qubits, ctrl_info["target"] + 1)
                    if "targets" in gate:
                        for target in gate["targets"]:
                            qubits = max(qubits, target + 1)
                    if "gates" in gate:
                        for gate in gate["gates"]:
                            for target in gate["targets"]:
                                qubits = max(qubits, target + 1)
    return qubits


def get_number_bits(yaml):
    """Extract the numebr of bits in yaml circuit."""
    bits = 0
    if "steps" in yaml.keys():
        for step in yaml["steps"]:
            if "gates" in step:
                for gate in step["gates"]:
                    if "bit" in gate:
                        bits = max(bits, gate["bit"] + 1)
    return bits

def get_circuit_descendants(circuits, circuit_id, descendants):
  circuit = circuits[circuit_id]
  for step in circuit["steps"]:
      gates = step["gates"]
      for gate in gates:
          if gate["name"] == "circuit":
              gate_circuit_id = gate["circuit_id"]
              if not gate_circuit_id in descendants: 
                  descendants.append(gate_circuit_id)
              get_circuit_descendants(circuits, gate_circuit_id, descendants)

  return descendants

def get_imports_and_or_headers_section(exporter):
    """ get export circuit header section"""
    return exporter.imports_and_or_headers_section()

def process_circuit_yaml(yaml_data, circuit_name, circuit_names, exporter, export_format, add_comments, skip_non_unitary_gates):
    """Export quantium circuit from YAML format to target language."""
    code = exporter.start_circuit_code(circuit_name)
    if "steps" in yaml_data.keys():
        for step in yaml_data["steps"]:
            step_index = step["index"]
            if export_format == "qiskit":
                if add_comments:
                    code += f"\n############ New circuit step no: {step_index} ############\n\n"
            elif export_format == "openqasm":
                if add_comments:
                    code += f"\n//////////// New circuit step no: {step_index} ////////////\n\n"
            elif export_format == "pyquil":
                if add_comments:
                    code += f"\n############ New circuit step no: {step_index} ############\n\n"
            elif export_format == "quil":
                if add_comments:
                    code += f"\n############ New circuit step no: {step_index} ############\n\n"
            elif export_format == "cirq":
                if add_comments:
                    code += f"\n############ New circuit step no: {step_index} ############\n\n"
            code += exporter.process_step(step, circuit_name, circuit_names, add_comments, skip_non_unitary_gates)
    code += exporter.end_circuit_code()
    return code


def get_exported_code(files, main_circuit_id, export_format, comments):
    """Get circuit code in exported format"""
    add_comments = True if comments else False

    exporter = None
    if export_format.lower() == "qiskit":
        exporter = QiskitExporter.Exporter()
    elif export_format.lower() == "openqasm":
        exporter = QiskitExporter.Exporter()
    elif export_format.lower() == "pyquil":
        exporter = PyquilExporter.Exporter()
    elif export_format.lower() == "quil":
        exporter = QuilExporter.Exporter()
    elif export_format.lower() == "cirq":
        exporter = CirqExporter.Exporter()
    else:
        raise Exception(f"Export format {export_format} is not supported.")

    quantum_code = get_imports_and_or_headers_section(exporter)

    circuit_codes = {}
    circuit_objects = {}
    circuit_names = {}

    # collect circuit_names
    for file in files:
        with open(file, "r") as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                circuit_id = yaml_data["circuit_id"]
                circuit_names[circuit_id] = yaml_data["circuit_name"].lower().replace(" ", "_")
            except yaml.YAMLError as ex:
                quantum_code = str(ex)
                return quantum_code

    # creating a custom gate for each circuit
    for file in files:
        with open(file, "r") as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                circuit_id = yaml_data["circuit_id"]
                circuit_objects[circuit_id] = yaml_data
                no_qubits = get_number_qubits(yaml_data)
                exporter.set_number_qubits(no_qubits)
                # a circuit with classical bits cannot be converted to a gate
                exporter.set_number_bits(0)
                circuit_name = yaml_data["circuit_name"].lower().replace(" ", "_")
                circuit_code = process_circuit_yaml(yaml_data, circuit_name, circuit_names, exporter, export_format, add_comments, True)
                circuit_codes[circuit_id] = circuit_code
            except yaml.YAMLError as ex:
                quantum_code = str(ex)
                return quantum_code

    main_circuit_descendants = []
    get_circuit_descendants(circuit_objects, main_circuit_id, main_circuit_descendants)
    # most elementary circuits should be placed first, circuits
    # that depend on elementary circuits should be added later:
    main_circuit_descendants.reverse()

    for circuit_id in main_circuit_descendants:
        quantum_code += circuit_codes[circuit_id]
        quantum_code += "\n"

    # process main circuit
    main_circuit_yaml_data = circuit_objects[main_circuit_id]
    no_qubits = get_number_qubits(main_circuit_yaml_data)
    exporter.set_number_qubits(no_qubits)
    no_bits = get_number_bits(main_circuit_yaml_data)
    exporter.set_number_bits(no_bits)
    quantum_code += process_circuit_yaml(main_circuit_yaml_data, "main", circuit_names, exporter, export_format, add_comments, False)

    # openqasm uses QiskitExporter
    if export_format.lower() == "openqasm":
        exec(quantum_code)
        try:
            quantum_code = eval('qc.qasm()')
        except Exception as ex:
            quantum_code = "QASM translation exception: \n"
            quantum_code += str(ex)
            quantum_code += "\n"

    return quantum_code


@click.command()
@click.option(
    "--files",
    "-f",
    required=True,
    multiple=True,
    help="One or more files with quantum circuits in yaml format."
)
@click.option(
    "--export_format",
    "-e",
    required=True,
    help="Specific format for exporting the circuit into: 'qiskit', 'openqasm', 'pyquil', 'quil' or 'cirq'.",
)
@click.option(
    "--circuit_id",
    "-i",
    required=True,
    help="The id of the circuit to export.",
)
@click.option(
    "-comments",
    "-c",
    required=False,
    help="Add comments with step index gate names in exported code."
)
def main(files, export_format, circuit_id, comments = False):

    output_file = f"exported_circuit_{export_format}.py"

    for file in files:
      if not file.endswith(".yaml"):
          print("One or more yaml file is required as input for this script.")
          return

    if export_format.lower() == "qiskit":
        pass
    elif export_format.lower() == "openqasm":
        output_file = "exported_circuit.qasm"
    elif export_format.lower() == "pyquil":
        raise Exception("The pyquil exporter is not yet implemented.")
    elif export_format.lower() == "quil":
        raise Exception("The quil exporter is not yet implemented.")
    elif export_format.lower() == "cirq":
        raise Exception("The cirq exporter is not yet implemented.")

    quantum_code = get_exported_code(files, int(circuit_id), export_format, comments and comments.lower() in ['true', '1', 't', 'y', 'yes'])

    if export_format.lower() == "openqasm":
        exec(quantum_code)
        try:
            quantum_code = eval('qc.qasm()')
        except Exception as ex:
            quantum_code = "QASM translation exception: \n"
            quantum_code += str(ex)
            quantum_code += "\n"

    with open(output_file, "w") as outfile:
        outfile.write(quantum_code)


if __name__ == "__main__":
    main()
