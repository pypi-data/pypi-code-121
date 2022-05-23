from typing import List
from typing import Optional

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram.tuples.model.ImportLiveDbDispLinkTuple import (
    ImportLiveDbDispLinkTuple,
)
from peek_plugin_diagram.tuples.shapes.ImportDispPolylineTuple import (
    ImportDispPolylineTuple,
)
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType


@addTupleType
class ImportDispPolygonTuple(Tuple):
    """Imported Display Polygon

    This tuple is used by other plugins to load polygons into the diagram.

    """

    __tupleType__ = diagramTuplePrefix + "ImportDispPolygonTuple"

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

    #: Parent DispGroup Hash, If this disp is part of a disp group then set this field to
    # the ImportDispGroupTuple.importHash fields value
    # NOTE: If this disp is part of a display group, then the GEOM coordinates need to
    # be relative to 0x0.
    # NOTE: Disps that are apart of a group must all be imported with the same
    # importGroupHash, during the same import call.
    parentDispGroupHash: str = TupleField()

    ### BEGIN FIELDS FOR THIS DISP ###

    lineWidth: int = TupleField()
    lineStyleHash: str = TupleField()
    lineColorHash: Optional[str] = TupleField()
    fillColorHash: Optional[str] = TupleField()

    FILL_TOP_TO_BOTTOM = 0
    FILL_BOTTOM_TO_TOP = 1
    FILL_RIGHT_TO_LEFT = 2
    FILL_LEFT_TO_RIGHT = 3
    fillDirection: int = TupleField()
    fillPercent: int = TupleField()

    geom: List[List[float]] = TupleField()

    #: Is this a retangle, with perpendicular equal sides.
    # This will effect how the polygon is edited
    isRectangle: Optional[bool] = TupleField()
