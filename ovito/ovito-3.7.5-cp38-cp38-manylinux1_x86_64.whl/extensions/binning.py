# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.grid
import ovito.extensions.particles

# Load the C extension module.
import ovito.plugins.SpatialBinningPython

# Publish classes.
ovito.modifiers.__all__ += ['SpatialBinningModifier']
