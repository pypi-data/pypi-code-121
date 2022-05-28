from __future__ import annotations
from typing import Union, Callable, List

from pymxs import runtime as rt

global CALLBACKS
CALLBACKS: List[When]
if not isinstance(CALLBACKS, list):
    CALLBACKS = []


class Manager:
    callbacks: List[When] = []


class Attribute:
    """These specify the attribute of the given object(s) to be tracked for change."""

    Topology: str = "topology"
    """Signaled when the topology of an object changes in
    the Modify panel such as, using a mesh smooth, optimize, or vertex delete."""
    Geometry: str = "geometry"
    """Signaled when the geometry of an object changes such as, by moving a vertex
    or using an animated modifier."""
    Names: str = "names"
    """Signaled when the name of an object is changed if this occurs because a user
    edits the name in one of the 3ds Max command panels. The handler is called
    repeatedly with each character that is changed."""
    Transform: str = "transform"
    """Signaled when the transform of an object is changed such as, by a move, rotate,
    or scale."""
    Select: str = "select"
    """Signaled when a scene node moves into or out of the current selection set. You
    should interrogate the <node>.isSelected property to determine the new state."""
    Parameters: str = "parameters"
    """Signaled when any parameters are changed in the object. This is something of a
    catch all because the core signals this event in many situations."""
    SubAnimStructure: str = "subAnimStructure"
    """Signaled when the dynamic subAnim structure changes such as, when a new vertex
    becomes animated in an editable mesh, or when a new controller is added to a list
    controller. Also called when subAnims are reassigned, for example, when a material
    is changed in an object."""
    Controller: str = "controller"
    """Signaled when a new controller is assigned to one of the object's tracks."""
    Children: str = "children"
    """Signaled when an object has immediate children added or removed."""


class Trigger:
    Changes: str = "changes"
    """Execute on the change of an Attribute."""
    Deleted: str = "deleted"
    """Execute on the deletion of the node."""


class HandleMode:
    RedrawViews: rt.Name = rt.Name("redrawViews")
    """Execute when the viewport redraws views."""
    TimeChange: rt.Name = rt.Name("timeChange")
    """Execute when the animation time is changed."""


class When:
    """Wrapper for the when construct in MAXScript.

    The when construct defines a change handler function for a certain type of event on
    one or more objects. The system then automatically calls this function whenever
    the event occurs.
    """

    def __init__(
        self,
        objs: Union[rt.Node, List[rt.Node]],
        trigger: Trigger,
        method: Callable,
        attr: Attribute = None,
        handleAt: HandleMode = HandleMode.RedrawViews,
    ) -> None:
        objs = [objs] if not isinstance(objs, list) else objs
        for obj in objs:
            if rt.isValidNode(obj):
                continue
            raise ValueError(f"{obj} is invalid.")
        self._objs = objs
        self._trigger = trigger
        if not callable(method):
            raise ValueError(f"{method} method is not callable.")
        self._method = method
        self._attr = attr
        self._handleAt = handleAt
        self._exec()

    def _exec(self) -> None:
        if self._trigger == Trigger.Changes and self._attr is None:
            raise ValueError(
                "The change trigger requires an Attribute to be set."
                "Use the attr= parameter"
            )
        rt._tempMethod = self._method
        mxsArray = "#(" + ",".join(["$" + obj.name for obj in self._objs]) + ")"
        mxs = (
            f"when {self._attr} {mxsArray} {self._trigger} "
            f"handleAt:#{self._handleAt} node do ("
            "_tempMethod node"
            ")"
        )
        handler = rt.Execute(mxs)
        CALLBACKS.append(handler)


def printer(obj):
    print(obj.radius)


def testWhen():
    sphere = rt.Sphere()
    When(sphere, Trigger.Changes, printer, attr=Attribute.Parameters)
    print(CALLBACKS)


testWhen()
