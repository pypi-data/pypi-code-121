"""
This module defines the :py:class:`Scene` class, which serves as a "universe" or context for all actions
performed by a script. The global scene object is accessible as module-level variable :py:data:`ovito.scene`.
The scene manages a list of :py:class:`~ovito.pipeline.Pipeline` objects, which will be visible in images and videos
when rendering the scene through a :py:class:`~ovito.vis.Viewport`. Furthermore, you can save the entire
scene definition including all pipelines to a :file:`.ovito` session state file, which can be opened in the graphical OVITO application.
"""

# Initialize sub-modules.
import ovito.data
import ovito.vis
import ovito.modifiers
import ovito.pipeline
import ovito.io
import ovito.nonpublic

# Load all extension modules.
import ovito.extensions

# The public symbols of this root module:
__all__ = ['version', 'version_string', 'scene', 'Scene', 'enable_logging']