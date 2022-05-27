# Load dependencies.
import ovito.extensions.pyscript
import ovito.extensions.particles

# Load the C extension module.
import ovito.plugins.NetCDFPluginPython

# Register import formats.
ovito.io.import_file._formatTable["netcdf/amber"] = ovito.nonpublic.AMBERNetCDFImporter

# Register export formats.
ovito.io.export_file._formatTable["netcdf/amber"] = ovito.nonpublic.AMBERNetCDFExporter
