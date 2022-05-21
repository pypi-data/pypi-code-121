from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, Set


class Container:
    __slots__ = ("_id", "name", "labels", "remote")

    def __init__(
        self, id_: str, name: str, labels: Dict[str, str] = None, remote: bool = False
    ):
        self._id = id_
        self.name = name
        self.labels: Dict[str, str] = labels.copy() if labels else {}
        self.remote = remote

    @property
    def id(self):
        return self._id

    def __str__(self):
        return f"Container(id={self.id}, name={self.name}, labels={self.labels}, remote={self.remote})"


class PodMesh:
    def __init__(self, hook):
        self.containers: Dict[str, Container] = {}
        self.labels: DefaultDict[str, Set[Container]] = defaultdict(set)
        self.hook = hook
        self.hook.on_podmesh_created(pm=self)

    def ready(self):
        self.hook.on_podmesh_ready(pm=self)

    def exit(self):
        self.hook.on_podmesh_exiting(pm=self)

    def add_container(self, container: Container):
        self.containers[container.id] = container
        for label in container.labels.keys():
            self.labels[label].add(container)
        self.hook.on_container_created(pm=self, container=container)

    def remove_container(self, container: Container):
        del self.containers[container.id]
        for label in container.labels.keys():
            self.labels[label].remove(container)
        self.hook.on_container_removed(pm=self, container=container)
