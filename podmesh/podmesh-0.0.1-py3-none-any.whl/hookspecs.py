from __future__ import annotations
import pluggy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from podmesh import PodMesh, Container

hookspec = pluggy.HookspecMarker("podmesh")


@hookspec
def on_podmesh_created(pm: PodMesh):
    """Called when a PodMesh instance is created"""


@hookspec
def on_podmesh_ready(pm: PodMesh):
    """Called when a PodMesh instance is ready to use"""


@hookspec
def on_podmesh_exiting(pm: PodMesh):
    """Called when a PodMesh instance is exiting"""


@hookspec
def on_container_created(pm: PodMesh, container: Container):
    """Triggered when a container is created"""


@hookspec
def on_container_removed(pm: PodMesh, container: Container):
    """Triggered when a container is remove"""
