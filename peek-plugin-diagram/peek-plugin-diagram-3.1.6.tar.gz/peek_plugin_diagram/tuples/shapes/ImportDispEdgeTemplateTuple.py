from typing import Optional, List

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.model.ImportLiveDbDispLinkTuple import (
    ImportLiveDbDispLinkTuple,
)
from peek_plugin_diagram.tuples.shapes.ImportDispPolylineTuple import (
    ImportDispPolylineTuple,
)


@addTupleType
class ImportDispEdgeTemplateTuple(Tuple):
    """Imported Shape Line Template

    This tuple is used by other plugins to load Line Template into the diagram.
    The line template is used by the user to create new lines.

    """

    __tupleType__ = diagramTuplePrefix + "ImportDispEdgeTemplateTuple"

    # The size of the end types are relative to the line width
    END_TYPE_NONE = ImportDispPolylineTuple.END_TYPE_NONE
    END_TYPE_ARROW = ImportDispPolylineTuple.END_TYPE_ARROW
    END_TYPE_DOT = ImportDispPolylineTuple.END_TYPE_DOT

    ### BEGIN DISP COMMON FIELDS ###

    # The actions to perform when this line is clicked
    ACTION_NONE = ImportDispPolylineTuple.ACTION_NONE
    ACTION_POSITION_ON = ImportDispPolylineTuple.ACTION_POSITION_ON
    # For ACTION_POSITION_ON, Add the following to the display data
    # data['actionPos'] = {k='coordSetKey', x=x, y=y, z=zoom}

    #: Key, This value is a unique ID of the object that this graphic represents
    # It's used to link this graphical object to objects in other plugins, like vertices
    # in the peek-plugin-graphdb plugin.
    # Length = 50
    key: str = TupleField()

    #: Selectable, Is is this item selectable?, the layer also needs selectable=true
    selectable: bool = TupleField()

    #: Action, An action to perform when this display item is clicked.
    # See the ACTION_NONE constants for values.
    action: Optional[int] = TupleField(None)

    #: Data, Generic data, this is passed to the popup context in the UI.
    # peek_plugin_diagram doesn't care as long as it's json compatible or None
    # Json length Length = 400
    data: Optional[dict] = TupleField(None)

    #: The hash of the level to link to (Matches ImportDispLevel.importHash)
    levelHash: str = TupleField()

    #: The hash of the layer to link to (Matches ImportDispLayer.importHash)
    layerHash: str = TupleField()

    #: The Z Order of this display object when compared against other objects on
    # same layer and level.
    zOrder: int = TupleField()

    #: The unique hash of this display object
    importHash: str = TupleField()

    #: The unique hash for all the display items imported in a group with this one.
    #: for example, a page or tile reference.
    importGroupHash: str = TupleField()

    #: The key of the ModelSet to import into
    modelSetKey: str = TupleField()

    #: The Key of the Coordinate Set to import into
    coordSetKey: str = TupleField()

    #: Related links to LiveDB values for this display item
    liveDbDispLinks: List[ImportLiveDbDispLinkTuple] = TupleField()

    ### BEGIN FIELDS FOR THIS DISP ###

    #: A name for this dispGroup
    name: str = TupleField()

    lineWidth: int = TupleField()
    lineStyleHash: str = TupleField()
    lineColorHash: Optional[str] = TupleField()

    geom: List[float] = TupleField()

    #: Start end type, is this an arrow, etc?
    startEndType: Optional[int] = TupleField()

    #: End End Type, See Start end type
    endEndType: Optional[int] = TupleField()
