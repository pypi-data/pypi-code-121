# Load dependencies.
import ovito.extensions.pyscript

# Load the C extension module.
import ovito.plugins.POVRayPython

# Register export formats.
ovito.io.export_file._formatTable["povray"] = ovito.nonpublic.POVRayExporter
