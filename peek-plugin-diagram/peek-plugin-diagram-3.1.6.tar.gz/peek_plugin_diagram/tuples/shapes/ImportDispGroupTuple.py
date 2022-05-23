from typing import Optional

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.shapes.ImportDispPolylineTuple import (
    ImportDispPolylineTuple,
)


@addTupleType
class ImportDispGroupTuple(Tuple):
    """Imported Display Group

    This tuple is used by other plugins to load groups of display objects
    into the diagram model.

    Display items are apart of this group if their :code:`parentDispGroupHash` value is
    set to the :code:`importHash` of this group.

    The display items that are apart of this group will never be displayed.

    To create an instance of this display group on the diagram,
    import a ImportDispGroupPtyTuple display object.

    """

    __tupleType__ = diagramTuplePrefix + "ImportDispGroupTuple"

    ### BEGIN DISP COMMON FIELDS ###

    # The actions to perform when this line is clicked
    ACTION_NONE = ImportDispPolylineTuple.ACTION_NONE
    ACTION_POSITION_ON = ImportDispPolylineTuple.ACTION_POSITION_ON
    # For ACTION_POSITION_ON, Add the following to the display data
    # data['actionPos'] = {k='coordSetKey', x=x, y=y, z=zoom}

    #: Selectable, Is is this item selectable?, the layer also needs selectable=true
    selectable: bool = TupleField()

    #: Overlay, Is is this shape an overlay?, Overlays are sometimes used to add dynamic
    # data to the diagram, such as a Job, Operation, or placing a green box over a red
    # one to change it's state.
    overlay: bool = TupleField()

    #: Action, An action to perform when this display item is clicked.
    # See the ACTION_NONE constants for values.
    action: Optional[int] = TupleField(None)

    #: Data, Generic data, this is passed to the popup context in the UI.
    # peek_plugin_diagram doesn't care as long as it's json compatible or None
    # Json length Length = 400
    data: Optional[dict] = TupleField(None)

    #: The unique hash of this display object
    # This will be referenced by:
    # ImportDispGroupPrtTuple.targetDispGroupHash, and
    # Any disps in the group, disp.parentDispGroupHash
    importHash: str = TupleField()

    #: The unique hash for all the display items imported in a group with this one.
    #: for example, a page or tile reference.
    importGroupHash: str = TupleField()

    #: The key of the ModelSet to import into
    modelSetKey: str = TupleField()

    #: The Key of the Coordinate Set to import into
    coordSetKey: str = TupleField()

    ### BEGIN FIELDS FOR THIS DISP ###

    #: A name for this dispGroup
    name: str = TupleField()

    # If this is set to true, then this group will be available in the user interface
    # for edit support (located in the special '##|dispgroup' grid key)
    compileAsTemplate: bool = TupleField(False)
