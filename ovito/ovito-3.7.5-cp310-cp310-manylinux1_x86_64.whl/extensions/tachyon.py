# Load dependencies.
import ovito.extensions.pyscript

# Load the C extension module.
import ovito.plugins.TachyonPython

# Publish classes.
ovito.vis.__all__ += ['TachyonRenderer']
