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
Top-level package for the Q-CTRL Visualizer.

The public API of this package consists only of the objects exposed through this top-level package.
Direct access to sub-modules is not officially supported, so may be affected by
backwards-incompatible changes without notice.
"""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from .bloch import (
    display_bloch_sphere,
    display_bloch_sphere_from_bloch_vectors,
    display_bloch_sphere_from_density_matrices,
    display_bloch_spheres_and_correlations,
)
from .confidence_ellipses import plot_confidence_ellipses
from .controls import (
    plot_controls,
    plot_sequences,
    plot_smooth_controls,
)
from .cost_history import plot_cost_history
from .discriminators import (
    plot_discriminator,
    plot_xdata,
)
from .filter_functions import plot_filter_functions
from .populations import plot_populations
from .style import (
    QCTRL_STYLE_COLORS,
    get_qctrl_style,
)

__all__ = [
    "QCTRL_STYLE_COLORS",
    "display_bloch_sphere",
    "display_bloch_sphere_from_bloch_vectors",
    "display_bloch_sphere_from_density_matrices",
    "display_bloch_spheres_and_correlations",
    "get_qctrl_style",
    "plot_confidence_ellipses",
    "plot_controls",
    "plot_cost_history",
    "plot_discriminator",
    "plot_filter_functions",
    "plot_populations",
    "plot_sequences",
    "plot_smooth_controls",
    "plot_xdata",
]

__version__ = "3.2.1"
