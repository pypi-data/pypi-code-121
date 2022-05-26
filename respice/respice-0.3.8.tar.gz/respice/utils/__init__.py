from respice.analysis import Circuit
from respice.components import Component


def create_series_connected_circuit(*components: Component) -> Circuit:
    """
    Utility to connect a closed circuit with all given elements connected in series.

    :param components:
        The elements to construct the circuit from.
    :return:
        A circuit.
    """
    if len(components) < 2:
        raise ValueError('Not enough elements to connect in series. At least 2 required.')

    circuit = Circuit()

    for i, elem in enumerate(components[:-1]):
        circuit.add(elem, i, i + 1)

    # Add closing element.
    circuit.add(components[-1], len(components) - 1, 0)

    return circuit
