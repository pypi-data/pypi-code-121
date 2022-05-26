# Load the C extension module.
import ovito.plugins.PyScript

# Load class add-ons.
import ovito.scene_class
import ovito.nonpublic.frame_buffer
import ovito.nonpublic.render_settings
import ovito.nonpublic.viewport_configuration
import ovito.data.data_collection
import ovito.pipeline.file_source
import ovito.pipeline.modifier_interface
import ovito.pipeline.pipeline_class # Depends on 'ovito.pipeline.modifier_interface'
import ovito.vis.data_vis
import ovito.vis.viewport
import ovito.io.import_file_func
import ovito.io.export_file_func
import ovito.io.file_reader_interface
