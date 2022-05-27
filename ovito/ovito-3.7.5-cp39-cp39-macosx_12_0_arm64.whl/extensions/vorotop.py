# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.particles

# Load the C extension module.
import ovito.plugins.VoroTopPython

# Publish classes.
ovito.modifiers.__all__ += ['VoroTopModifier']
