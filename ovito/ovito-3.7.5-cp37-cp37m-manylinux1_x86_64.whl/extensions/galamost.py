# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.particles

# Load the C extension module.
import ovito.plugins.GalamostPython

# Register import formats.
ovito.io.import_file._formatTable["galamost"] = ovito.nonpublic.GALAMOSTImporter
