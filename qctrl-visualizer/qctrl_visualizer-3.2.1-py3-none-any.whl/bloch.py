# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""
Bloch sphere visualization module
"""

import json
import uuid
from typing import Optional

import numpy as np

PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
PAULI_Z = np.array([[1, 0], [0, -1]], dtype=complex)

PAULIS = [PAULI_X, PAULI_Y, PAULI_Z]


def display_bloch_spheres_and_correlations(
    states: np.ndarray,
    color: Optional[str] = None,
    width: int = 900,
    visualizer_js: Optional[str] = None,
):
    r"""
    Visualizes a trajectory of two-qubit states.

    This function requires IPython, and you must run it from a Jupyter
    notebook. By default, it requires an Internet connection to fetch the
    JavaScript library for the two-qubit visualizer, but you can also use
    it offline by making a backup copy of the JavaScript file in your local
    filesystem.

    Parameters
    ----------
    states : np.ndarray
        A trajectory of two-qubit states represented by state vectors. This
        array must have shape ``[T,4]``, where ``T`` is the number of state
        vectors in the trajectory.
    color : str, optional
        A string identifying the color of the trajectory. The string must
        be a color value accepted by CSS, such as a hexadecimal code like
        ``"#00FF00"`` or a color name like ``"green"``. The exact types of
        values accepted might depend on your browser, but you can find an
        official list of color values as part of the `CSS standard
        <https://www.w3.org/TR/css-color-3/#colorunits>`_. If you don't
        pass a string, the default behavior is to use the color value
        ``"#EB6467"``.
    width : int, optional
        The width of the visualization, in pixels. Its height is half of
        the value of the width. Defaults to 900 pixels.
    visualizer_js : str, optional
        A string with the location of the JavaScript library for the
        two-qubit visualizer. It can be a URL or a path to a local file. If
        you don't pass a string, the function uses the default online
        version of the Q-CTRL Visualizer JavaScript package.

    Notes
    -----
    While the pure state of a single qubit can be represented as a point on
    one Bloch sphere, the pure state of two qubits isn't fully represented
    by simply duplicating the number of Bloch spheres. This is due to the
    fact that the state of two qubits can present correlations that can't
    be visualized simply from the individual states of each qubit.

    This function displays the state of the two qubits using two Bloch
    spheres and three additional tetrahedra, which represent the
    information about the entanglement between the qubits. The points on
    (or in) the Bloch spheres are analogous to those in the single-qubit
    visualization. The Cartesian coordinates
    :math:`(b_{1,x}, b_{1,y}, b_{1,z})` for the first Bloch sphere are the
    following expectation values:

    .. math::
        b_{1,x} = \langle \sigma_x \otimes I \rangle, \\
        b_{1,y} = \langle \sigma_y \otimes I \rangle, \\
        b_{1,z} = \langle \sigma_z \otimes I \rangle,

    whereas the Cartesian coordinates :math:`(b_{2,x}, b_{2,y}, b_{2,z})`
    for the second Bloch sphere are:

    .. math::
        b_{2,x} = \langle I \otimes \sigma_x \rangle, \\
        b_{2,y} = \langle I \otimes \sigma_y \rangle, \\
        b_{2,z} = \langle I \otimes \sigma_z \rangle,

    where :math:`I` is the :math:`2 \times 2` identity matrix.

    The points in the three extra tetrahedra represent the correlations
    between observables in the two qubits. Each tetrahedron has three non
    orthogonal axes, each representing the covariance of a specific
    two-qubit observable. The upper left tetrahedron represents the
    covariances :math:`V(XY)`, :math:`V(YZ)`, and :math:`V(ZX)`:

    .. math::
        V(XY) = \langle \sigma_x \otimes \sigma_y \rangle - b_{1,x} b_{2,y}, \\
        V(YZ) = \langle \sigma_y \otimes \sigma_z \rangle - b_{1,y} b_{2,z}, \\
        V(ZX) = \langle \sigma_z \otimes \sigma_x \rangle - b_{1,z} b_{2,x}.

    The tetrahedron on the upper right part of the display represents the
    covariances :math:`V(XZ)`, :math:`V(YX)`, and :math:`V(ZY)`:

    .. math::
        V(XZ) = \langle \sigma_x \otimes \sigma_z \rangle - b_{1,x} b_{2,z}, \\
        V(YX) = \langle \sigma_y \otimes \sigma_x \rangle - b_{1,y} b_{2,x}, \\
        V(ZY) = \langle \sigma_z \otimes \sigma_y \rangle - b_{1,z} b_{2,y}.

    The tetrahedron in the lower part of the visualization has the
    covariances :math:`V(XX)`, :math:`V(YY)`, and :math:`V(ZZ)`:

    .. math::
        V(XX) = \langle \sigma_x \otimes \sigma_x \rangle - b_{1,x} b_{2,x}, \\
        V(YY) = \langle \sigma_y \otimes \sigma_y \rangle - b_{1,y} b_{2,y}, \\
        V(ZZ) = \langle \sigma_z \otimes \sigma_z \rangle - b_{1,z} b_{2,z}.

    The two-qubit visualization also displays a measure of the entanglement
    between the two qubits in the form of a bar that shows the concurrence
    :math:`C` associated with a given state vector :math:`| \psi \rangle`:

    .. math::
        C(| \psi \rangle) = 2 \left| \langle 00 | \psi \rangle
        \langle 11 | \psi \rangle - \langle 01 | \psi \rangle
        \langle 10 | \psi \rangle \right|.

    .. rubric:: Styling

    This function displays HTML and JavaScript in your Jupyter notebook. It
    creates four HTML elements that you can style by defining the following
    CSS classes:

    qctrlvisualizer
        CSS class for the outer ``<div>`` that contains the Bloch spheres
        visualization, progress bar, and button. The div has inline styles
        ``display:flex``, ``flex-direction:column``, and
        ``align-items:center``, so if you want to use different values for
        these properties you must either strip them out or use the
        ``!important`` rule when defining your ``qctrlvisualizer`` class.

    qctrlvisualizer-wrapper
        CSS class for the ``<div>`` that contains the Bloch spheres
        visualization. The div has inline styles ``margin:0.5rem 0``,
        ``width``, and ``height`` (based on the `width` you pass).

    qctrlvisualizer-progress-bar
        CSS class for the range ``<input>`` representing the progress bar.
        The input has inline style ``margin:0.5rem 0``.

    qctrlvisualizer-button
        CSS class for the ``<button>`` representing the play/pause/replay
        button. The button has inline style ``margin:0.5rem 0``.

    qctrlvisualizer-button-play
        CSS class for the ``<button>`` when the button text is "Play".

    qctrlvisualizer-button-pause
        CSS class for the ``<button>`` when the button text is "Pause".

    qctrlvisualizer-button-replay
        CSS class for the ``<button>`` when the button text is "Replay".
    """

    identifier = uuid.uuid4().hex

    color = color or "#EB6467"

    density_matrices = (
        np.asarray(states)[..., None] @ np.asarray(states).conj()[..., None, :]
    )

    # Calculate points on (or in) the Bloch spheres.
    paulis_1 = [np.kron(pauli, np.eye(2)) for pauli in PAULIS]
    paulis_2 = [np.kron(np.eye(2), pauli) for pauli in PAULIS]

    bloch_vectors_1 = _expectation_values(density_matrices, np.array(paulis_1))
    bloch_vectors_2 = _expectation_values(density_matrices, np.array(paulis_2))

    # Calculate points in the tetrahedra.
    paulis_a = [np.kron(PAULIS[i], PAULIS[(i + 1) % 3]) for i in range(3)]
    paulis_b = [np.kron(PAULIS[i], PAULIS[(i + 2) % 3]) for i in range(3)]
    paulis_c = [np.kron(pauli, pauli) for pauli in PAULIS]

    tetrahedron_a = (
        _expectation_values(density_matrices, np.array(paulis_a))
        - bloch_vectors_1 * bloch_vectors_2[:, [1, 2, 0]]
    )
    tetrahedron_b = (
        _expectation_values(density_matrices, np.array(paulis_b))
        - bloch_vectors_1 * bloch_vectors_2[:, [2, 0, 1]]
    )
    tetrahedron_c = (
        _expectation_values(density_matrices, np.array(paulis_c))
        - bloch_vectors_1 * bloch_vectors_2
    )

    # Calculate concurrence.
    concurrence = 2.0 * np.abs(
        states[:, 0] * states[:, 3] - states[:, 1] * states[:, 2]
    )
    is_entangled = concurrence > 0.02

    visualization_data = {
        "data": {
            "entanglementBooleans": is_entangled.tolist(),
            "entanglementMeasures": concurrence.tolist(),
            "qubits": [
                {
                    "name": "qubit1",
                    "x": [bloch_vector[0] for bloch_vector in bloch_vectors_1],
                    "y": [bloch_vector[1] for bloch_vector in bloch_vectors_1],
                    "z": [bloch_vector[2] for bloch_vector in bloch_vectors_1],
                },
                {
                    "name": "qubit2",
                    "x": [bloch_vector[0] for bloch_vector in bloch_vectors_2],
                    "y": [bloch_vector[1] for bloch_vector in bloch_vectors_2],
                    "z": [bloch_vector[2] for bloch_vector in bloch_vectors_2],
                },
            ],
            "vectors": [
                {
                    "name": "a",
                    "x": [vector[0] for vector in tetrahedron_a],
                    "y": [vector[1] for vector in tetrahedron_a],
                    "z": [vector[2] for vector in tetrahedron_a],
                },
                {
                    "name": "b",
                    "x": [vector[0] for vector in tetrahedron_b],
                    "y": [vector[1] for vector in tetrahedron_b],
                    "z": [vector[2] for vector in tetrahedron_b],
                },
                {
                    "name": "c",
                    "x": [vector[0] for vector in tetrahedron_c],
                    "y": [vector[1] for vector in tetrahedron_c],
                    "z": [vector[2] for vector in tetrahedron_c],
                },
            ],
        }
    }

    _display_visualization(
        visualization_data=visualization_data,
        identifier=identifier,
        width=width,
        height=width // 2,
        color=color,
        visualizer_js=visualizer_js,
    )


def display_bloch_sphere(
    states: np.ndarray,
    color: Optional[str] = None,
    width: int = 300,
    visualizer_js: Optional[str] = None,
):
    r"""
    Displays a trajectory on the Bloch sphere using state vectors as input.

    This function requires IPython, and you must run it from a Jupyter
    notebook. By default, it requires an Internet connection to fetch the
    JavaScript library for the Bloch sphere visualizer, but you can also
    use it offline by making a backup copy of the JavaScript file in your
    local filesystem.

    This function plots trajectories on the surface of the Bloch sphere if
    you provide normalized state vectors. To display trajectories in the
    interior of the sphere, provide non-normalized state vectors, or use
    `display_bloch_sphere_from_density_matrices
    <display_bloch_sphere_from_density_matrices.html>`_ or
    `display_bloch_sphere_from_bloch_vectors
    <display_bloch_sphere_from_bloch_vectors.html>`_.

    Parameters
    ----------
    states : np.ndarray
        A trajectory of single-qubit states represented by state vectors.
        This array must have shape ``[T,2]``, where ``T`` is the number of
        state vectors in the trajectory.
    color : str, optional
        A string identifying the color of the trajectory. The string must
        be a color value accepted by CSS, such as a hexadecimal code like
        ``"#00FF00"`` or a color name like ``"green"``. The exact types of
        values accepted might depend on your browser, but you can find an
        official list of color values as part of the `CSS standard
        <https://www.w3.org/TR/css-color-3/#colorunits>`_. If you don't
        pass a string, the default behavior is to use the color value
        ``"#EB6467"``.
    width : int, optional
        The width of the Bloch sphere, in pixels. Its height has the same
        value as the width. Defaults to 300 pixels.
    visualizer_js : str, optional
        A string with the location of the JavaScript library for the Bloch
        sphere visualizer. It can be a URL or a path to a local file. If
        you don't pass a string, the function uses the default online
        version of the Q-CTRL Visualizer JavaScript package.

    See Also
    --------
    display_bloch_sphere_from_bloch_vectors,
    display_bloch_sphere_from_density_matrices

    Notes
    -----
    This function represents the trajectory of single-qubit states as
    points on the Bloch sphere. The points on the Bloch sphere have
    spherical coordinates :math:`(r, \theta, \phi)`, which (up to a global
    phase) correspond to each state vector
    :math:`\left| \psi \right\rangle` in the trajectory according to:

    .. math::
        \left| \psi \right\rangle = \sqrt{r} \cos(\theta/2)
        \left| 0 \right\rangle + \sqrt{r} e^{i \phi} \sin(\theta/2)
        \left| 1 \right\rangle.

    The Bloch sphere has unit radius. If the states that you provide are
    not normalized, then :math:`r \ne 1` and you can draw trajectories
    inside the Bloch sphere.

    .. rubric:: Styling

    This function displays HTML and JavaScript in your Jupyter notebook. It
    creates four HTML elements that you can style by defining the following
    CSS classes:

    qctrlvisualizer
        CSS class for the outer ``<div>`` that contains the Bloch sphere
        visualization, progress bar, and button. The div has inline styles
        ``display:flex``, ``flex-direction:column``, and
        ``align-items:center``, so if you want to use different values for
        these properties you must either strip them out or use the
        ``!important`` rule when defining your ``qctrlvisualizer`` class.

    qctrlvisualizer-wrapper
        CSS class for the ``<div>`` that contains the Bloch sphere
        visualization. The div has inline styles ``margin:0.5rem 0``,
        ``width``, and ``height`` (based on the `width` you pass).

    qctrlvisualizer-progress-bar
        CSS class for the range ``<input>`` representing the progress bar.
        The input has inline style ``margin:0.5rem 0``.

    qctrlvisualizer-button
        CSS class for the ``<button>`` representing the play/pause/replay
        button. The button has inline style ``margin:0.5rem 0``.

    qctrlvisualizer-button-play
        CSS class for the ``<button>`` when the button text is "Play".

    qctrlvisualizer-button-pause
        CSS class for the ``<button>`` when the button text is "Pause".

    qctrlvisualizer-button-replay
        CSS class for the ``<button>`` when the button text is "Replay".
    """
    density_matrices = (
        np.asarray(states)[..., None] @ np.asarray(states)[..., None, :].conj()
    )

    display_bloch_sphere_from_density_matrices(
        density_matrices=density_matrices,
        color=color,
        width=width,
        visualizer_js=visualizer_js,
    )


def display_bloch_sphere_from_density_matrices(
    density_matrices: np.ndarray,
    color: Optional[str] = None,
    width: int = 300,
    visualizer_js: Optional[str] = None,
):
    r"""
    Displays a trajectory in the Bloch sphere from input density matrices.

    This function requires IPython, and you must run it from a Jupyter
    notebook. By default, it requires an Internet connection to fetch the
    JavaScript library for the Bloch sphere visualizer, but you can also
    use it offline by making a backup copy of the JavaScript file in your
    local filesystem.

    Parameters
    ----------
    density_matrices : np.ndarray
        A trajectory of single-qubit states represented by density
        matrices. This array must have shape ``[T,2,2]``, where ``T`` is
        the number of density matrices in the trajectory.
    color : str, optional
        A string identifying the color of the trajectory. The string must
        be a color value accepted by CSS, such as a hexadecimal code like
        ``"#00FF00"`` or a color name like ``"green"``. The exact types of
        values accepted might depend on your browser, but you can find an
        official list of color values as part of the `CSS standard
        <https://www.w3.org/TR/css-color-3/#colorunits>`_. If you don't
        pass a string, the default behavior is to use the color value
        ``"#EB6467"``.
    width : int, optional
        The width of the Bloch sphere, in pixels. Its height has the same
        value as the width. Defaults to 300 pixels.
    visualizer_js : str, optional
        A string with the location of the JavaScript library for the Bloch
        sphere visualizer. It can be a URL or a path to a local file. If
        you don't pass a string, the function uses the default online
        version of the Q-CTRL Visualizer JavaScript package.

    See Also
    --------
    display_bloch_sphere,
    display_bloch_sphere_from_bloch_vectors

    Notes
    -----
    This function represents the trajectory of single-qubit states as
    points inside or on the Bloch sphere. These points correspond to each
    input density matrix :math:`\rho`, according to the following equation:

    .. math::
        \rho = \frac{1}{2} I + \frac{1}{2} \left( b_x \sigma_x + b_y
        \sigma_y + b_z \sigma_z \right),

    where :math:`I` is the :math:`2 \times 2` identity matrix, and
    :math:`b_x`, :math:`b_y`, and :math:`b_z` are Cartesian coordinates on
    the Bloch sphere.

    As the Pauli matrices :math:`\sigma_k` have zero trace and their square
    is the identity matrix, the value of each Cartesian coordinate
    :math:`b_k` is:

    .. math::
        b_k = \mathrm{Tr} \left\{ \sigma_k \rho \right\},

    which is just the expectation value of :math:`\sigma_k`.

    .. rubric:: Styling

    This function displays HTML and JavaScript in your Jupyter notebook. It
    creates four HTML elements that you can style by defining the following
    CSS classes:

    qctrlvisualizer
        CSS class for the outer ``<div>`` that contains the Bloch sphere
        visualization, progress bar, and button. The div has inline styles
        ``display:flex``, ``flex-direction:column``, and
        ``align-items:center``, so if you want to use different values for
        these properties you must either strip them out or use the
        ``!important`` rule when defining your ``qctrlvisualizer`` class.

    qctrlvisualizer-wrapper
        CSS class for the ``<div>`` that contains the Bloch sphere
        visualization. The div has inline styles ``margin:0.5rem 0``,
        ``width``, and ``height`` (based on the `width` you pass).

    qctrlvisualizer-progress-bar
        CSS class for the range ``<input>`` representing the progress bar.
        The input has inline style ``margin:0.5rem 0``.

    qctrlvisualizer-button
        CSS class for the ``<button>`` representing the play/pause/replay
        button. The button has inline style ``margin:0.5rem 0``.

    qctrlvisualizer-button-play
        CSS class for the ``<button>`` when the button text is "Play".

    qctrlvisualizer-button-pause
        CSS class for the ``<button>`` when the button text is "Pause".

    qctrlvisualizer-button-replay
        CSS class for the ``<button>`` when the button text is "Replay".
    """
    bloch_vectors = _expectation_values(
        np.asarray(density_matrices), np.asarray(PAULIS)
    )

    display_bloch_sphere_from_bloch_vectors(
        bloch_vectors=bloch_vectors,
        color=color,
        width=width,
        visualizer_js=visualizer_js,
    )


def _expectation_values(
    density_matrices: np.ndarray, observables: np.ndarray
) -> np.ndarray:
    """
    Returns expectation values of `observables` for `density_matrices`.

    Parameters
    ----------
    density_matrices : np.ndarray
        A batch of :math:`M` density matrices of shape :math:`D \times D`,
        with respect to which you want to calculate the expectation values.
    observables : np.ndarray
        A batch of :math:`N` matrices of shape :math:`D \times D`, whose
        expectation values you want to calculate.

    Returns
    -------
    np.ndarray
        An array of shape ``[M,N]`` with the real expectation values.
    """
    return np.real(
        np.trace(
            np.matmul(observables[None, ...], density_matrices[:, None, ...]),
            axis1=-2,
            axis2=-1,
        )
    )


def display_bloch_sphere_from_bloch_vectors(
    bloch_vectors: np.ndarray,
    color: Optional[str] = None,
    width: int = 300,
    visualizer_js: Optional[str] = None,
):
    r"""
    Displays a Bloch sphere with an animation of the Bloch vectors.

    This function requires IPython, and you must run it from a Jupyter
    notebook. By default, it requires an Internet connection to fetch the
    JavaScript library for the Bloch sphere visualizer, but you can also
    use it offline by making a backup copy of the JavaScript file in your
    local filesystem.

    Parameters
    ----------
    bloch_vectors : np.ndarray
        A trajectory of Bloch vectors (that is, points either on or inside
        the Bloch sphere) given in Cartesian coordinates. This array must
        have shape ``[T,3]``, where ``T`` is the number of vectors in the
        trajectory.
    color : str, optional
        A string identifying the color of the trajectory. The string must
        be a color value accepted by CSS, such as a hexadecimal code like
        ``"#00FF00"`` or a color name like ``"green"``. The exact types of
        values accepted might depend on your browser, but you can find an
        official list of color values as part of the `CSS standard
        <https://www.w3.org/TR/css-color-3/#colorunits>`_. If you don't
        pass a string, the default behavior is to use the color value
        ``"#EB6467"``.
    width : int, optional
        The width of the Bloch sphere, in pixels. Its height has the same
        value as the width. Defaults to 300 pixels.
    visualizer_js : str, optional
        A string with the location of the JavaScript library for the Bloch
        sphere visualizer. It can be a URL or a path to a local file. If
        you don't pass a string, the function uses the default online
        version of the Q-CTRL Visualizer JavaScript package.

    Raises
    ------
    ValueError
        If `bloch_vectors` is of complex type.

    See Also
    --------
    display_bloch_sphere,
    display_bloch_sphere_from_density_matrices

    Notes
    -----
    The Bloch vector :math:`\mathbf{b}` is a 3D real vector that represents
    a point either on or inside the Bloch sphere. It is equivalent to a
    single-qubit state represented by a density matrix :math:`\rho`,
    according to the following equation:

    .. math::
        \rho = \frac{1}{2} I + \frac{1}{2} \left( b_x \sigma_x + b_y
        \sigma_y + b_z \sigma_z \right),

    where :math:`I` is the :math:`2 \times 2` identity matrix, and
    :math:`b_x`, :math:`b_y`, and :math:`b_z` are the components of the
    Bloch vector in Cartesian coordinates.

    For points on the surface of the Bloch sphere (that is, when the norm
    of the vector has value 1), the Bloch vector represents a pure state.
    In this case, if you write the Bloch vector in terms of the spherical
    coordinates :math:`(\theta, \phi)`, such that
    :math:`b_x = \sin\theta \cos\phi`, :math:`b_y = \sin\theta \sin\phi`,
    and :math:`b_z = \cos \theta`, then the state vector it represents is:

    .. math::
        \left| \psi \right\rangle = \cos(\theta/2) \left| 0 \right\rangle
        + e^{i \phi} \sin(\theta/2) \left| 1 \right\rangle.

    .. rubric:: Styling

    This function displays HTML and JavaScript in your Jupyter notebook. It
    creates four HTML elements that you can style by defining the following
    CSS classes:

    qctrlvisualizer
        CSS class for the outer ``<div>`` that contains the Bloch sphere
        visualization, progress bar, and button. The div has inline styles
        ``display:flex``, ``flex-direction:column``, and
        ``align-items:center``, so if you want to use different values for
        these properties you must either strip them out or use the
        ``!important`` rule when defining your ``qctrlvisualizer`` class.

    qctrlvisualizer-wrapper
        CSS class for the ``<div>`` that contains the Bloch sphere
        visualization. The div has inline styles ``margin:0.5rem 0``,
        ``width``, and ``height`` (based on the `width` you pass).

    qctrlvisualizer-progress-bar
        CSS class for the range ``<input>`` representing the progress bar.
        The input has inline style ``margin:0.5rem 0``.

    qctrlvisualizer-button
        CSS class for the ``<button>`` representing the play/pause/replay
        button. The button has inline style ``margin:0.5rem 0``.

    qctrlvisualizer-button-play
        CSS class for the ``<button>`` when the button text is "Play".

    qctrlvisualizer-button-pause
        CSS class for the ``<button>`` when the button text is "Pause".

    qctrlvisualizer-button-replay
        CSS class for the ``<button>`` when the button text is "Replay".
    """
    if np.iscomplexobj(bloch_vectors):
        raise ValueError("The Bloch vectors must not have complex type.")

    identifier = uuid.uuid4().hex

    visualization_data = {
        "data": {
            "qubits": [
                {
                    "name": "qubit1",
                    "x": [vector[0] for vector in bloch_vectors],
                    "y": [vector[1] for vector in bloch_vectors],
                    "z": [vector[2] for vector in bloch_vectors],
                }
            ]
        }
    }

    color = color or "#EB6467"

    _display_visualization(
        visualization_data=visualization_data,
        identifier=identifier,
        color=color,
        width=width,
        height=width,
        visualizer_js=visualizer_js,
    )


def _display_visualization(
    visualization_data: dict,
    identifier: str,
    width: int,
    height: int,
    color: str,
    visualizer_js: Optional[str] = None,
):
    """
    Calls the Q-CTRL Visualizer JavaScript to display the Bloch sphere.

    You can find the Q-CTRL Visualizer JavaScript package at
    https://www.npmjs.com/package/@qctrl/visualizer .

    Parameters
    ----------
    visualization_data : dict
        A dictionary containing serialized data that is understood by the
        `Visualizer` class of the ``Visualizer.js`` script.
    identifier : str
        A string appended to the end of the ``id`` of the HTML objects that
        this function creates.
    width : int
        The width of the visualization, in pixels.
    height : int
        The height of the visualization, in pixels.
    color : str
        A string identifying the color of the trajectory on the Bloch
        sphere. The string must be a color value accepted by CSS, such as a
        hexadecimal code like ``"#00FF00"`` or a color name like
        ``"green"``.
    visualizer_js : str, optional
        A string with the location of the JavaScript library for the Bloch
        sphere visualizer. It can be a URL or a path to a local file. If
        you don't pass a string, the function uses the default online
        version of the Q-CTRL Visualizer JavaScript package.
    """
    # pylint: disable=import-error,import-outside-toplevel
    from IPython.display import (
        HTML,
        Javascript,
        display,
    )

    theme_settings = {"highlightColor": color, "pathColor": color}

    labels = {
        "xAxis": True,
        "yAxis": True,
        "zAxis": True,
        "theta": True,
        "phi": True,
        "northPole": True,
        "southPole": True,
        # Prevent "Non Error Trajectory" dot from appearing.
        "nonErrorState": False,
    }

    default_url = (
        "https://cdn.jsdelivr.net/npm/@qctrl/visualizer@3.1.14/umd/visualizer.min.js"
    )

    # If no custom Visualizer.js is provided, use the default one.
    visualizer_js = visualizer_js or default_url

    html_code = f"""
    <div
        class="qctrlvisualizer"
        style="display:flex;flex-direction:column;align-items:center;"
    >
        <div
            class="qctrlvisualizer-wrapper"
            style="width:{width}px;height:{height}px;margin:0.5rem 0"
            id="qctrlvisualizer-wrapper-{identifier}"
        ></div>
        <input
            class="qctrlvisualizer-progress-bar"
            style="margin:0.5rem 0"
            id="qctrlvisualizer-progress-bar-{identifier}"
            type="range"
            min="0"
            max="1"
            step="0.01"
            value="0"
        >
        <button
            class="qctrlvisualizer-button qctrlvisualizer-button-play"
            style="margin:0.5rem 0"
            id="qctrlvisualizer-button-{identifier}"
        >Play</button>
    </div>
    """

    js_code = f"""
    let isPlaying = false;
    let progress = 0;

    const visualizationData = {json.dumps(visualization_data)};
    const themeSettings = {json.dumps(theme_settings)};
    const labels = {json.dumps(labels)};

    const wrapper = document.getElementById("qctrlvisualizer-wrapper-{identifier}");
    const progressBar = document.getElementById("qctrlvisualizer-progress-bar-{identifier}");
    const button = document.getElementById("qctrlvisualizer-button-{identifier}");

    function updateButton () {{
      button.classList.remove(...[
        "qctrlvisualizer-button-play",
        "qctrlvisualizer-button-pause",
        "qctrlvisualizer-button-replay"
      ]);
      if (isPlaying) {{
        button.classList.add("qctrlvisualizer-button-pause");
        button.innerHTML = "Pause";
        return;
      }}
      if (progress>=1) {{
        button.classList.add("qctrlvisualizer-button-replay");
        button.innerHTML = "Replay";
        return;
      }}
      button.classList.add("qctrlvisualizer-button-play");
      button.innerHTML = "Play";
    }}

    button.onclick = () => {{
      isPlaying = !isPlaying;
      if (progress >= 1) progress = 0;
      updateButton();
      visualizer.update({{ isPlaying, progress }});
    }};

    progressBar.oninput = ({{ target }}) => {{
      progress = +target.value;
      visualizer.update({{ progress }});
      updateButton();
    }};

    const onUpdate = ({{ target, data }}) => {{
      progress = data.progress;
      progressBar.value = progress;
      if (progress >= 1) {{
        isPlaying = false;
        target.update({{ isPlaying }});
        updateButton();
      }}
    }};

    const visualizer = new Visualizer({{
      visualizationData,
      wrapper,
      onUpdate,
      labels,
    }}).init();

    visualizer.update({{ themeSettings }});
    """

    custom_js_loader = f"""
    function visualizerLoader() {{
      if ((typeof Visualizer) == "function") {{
        console.log("Using preloaded Q-CTRL Visualizer JavaScript package.");
        displayBlochSphere();
        return;
      }}

      try {{
        console.log("Attempting to load {visualizer_js} with require.js.");
        requirejs(["{visualizer_js}"], displayBlochSphere, displayErrorMessage);
      }} catch(error) {{
        var existing_script = document.getElementById("qctrlvisualizer-script");

        if (existing_script !== null) {{
          console.log(
            "Script tag for the Q-CTRL Visualizer JavaScript package already exists."
            + " Delaying execution of function until script is loaded."
          );
          existing_script.addEventListener("load", displayBlochSphere);
          existing_script.addEventListener("error", displayErrorMessage);
          return;
        }}

        console.log("Attempting to load {visualizer_js} with script tag.");
        script = document.createElement("script");
        script.onload = displayBlochSphere;
        script.onerror = displayErrorMessage;
        script.id = "qctrlvisualizer-script";
        script.src = "{visualizer_js}";
        document.head.appendChild(script);
      }}
    }}

    function displayBlochSphere() {{ {js_code} }}

    function displayErrorMessage() {{
      console.log("Failed to load {visualizer_js}.");
      const wrapper = document.getElementById("qctrlvisualizer-wrapper-{identifier}");
      wrapper.innerHTML = "Could not load JavaScript at {visualizer_js}.";
    }}

    visualizerLoader();
    """

    display(HTML(html_code))
    display(Javascript(custom_js_loader))
