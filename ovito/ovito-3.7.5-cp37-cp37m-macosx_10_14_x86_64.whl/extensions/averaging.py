# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.stdobj

# Load the C extension module.
import ovito.plugins.TimeAveragingPython

# Publish classes.
ovito.modifiers.__all__ += ['TimeAveragingModifier', 'TimeSeriesModifier']
