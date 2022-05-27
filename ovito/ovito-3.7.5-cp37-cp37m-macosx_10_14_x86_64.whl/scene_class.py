import ovito
from ovito import Scene

# Implementation of the Scene.pipelines property:
def _Scene_pipelines(self):
    """ The list of :py:class:`~ovito.pipeline.Pipeline` objects that are currently part of the three-dimensional scene.
        Only pipelines in this list will display their output data in the viewports and in rendered images. You can add or remove a pipeline either by calling
        its :py:meth:`~ovito.pipeline.Pipeline.add_to_scene` or :py:meth:`~ovito.pipeline.Pipeline.remove_from_scene` methods or by directly manipulating this
        list using the standard Python ``append()`` and ``del`` statements:

        .. literalinclude:: ../example_snippets/scene_pipelines.py
          :lines: 1-11
    """
    return self.scene_root.children
Scene.pipelines = property(_Scene_pipelines)

# Implementation of the Scene.selected_pipeline property:
def _get_Scene_selected_pipeline(self):
    """ The :py:class:`~ovito.pipeline.Pipeline` currently selected in the OVITO desktop application,
        or ``None`` if no pipeline is selected. Typically, this is the last pipeline that was added to the scene using
        :py:meth:`Pipeline.add_to_scene() <ovito.pipeline.Pipeline.add_to_scene>`.

        This field can be useful for macro scripts running in the context of an interactive OVITO session, 
        which perform some action on the currently selected pipeline such as inserting a modifier.
    """
    return self.selection.nodes[0] if self.selection.nodes else None
def _set_Scene_selected_pipeline(self, pipeline):
    """ Sets the :py:class:`~ovito.pipeline.Pipeline` that is currently selected in the graphical user interface of OVITO. """
    if pipeline: self.selection.nodes = [pipeline]
    else: del self.selection.nodes[:]
Scene.selected_pipeline = property(_get_Scene_selected_pipeline, _set_Scene_selected_pipeline)
