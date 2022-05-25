import hyperthought as ht
import os
import re
from collections.abc import MutableMapping
from typing import Callable, Optional, Union
from uuid import uuid4


__all__ = ["HyperThoughtKeyFinder"]


class Workspace(MutableMapping):
    def __init__(self, *args, **kwds):
        """
        While HyperThought 2.0 provides Workflow, Decision, and Process
        objects derived from `Element` that expose the `Element.id`
        interface, no such class exists for Workspaces. This object
        is a thin wrapper around a python dict that exposes this
        same `Workspace.id` interface for Workspaces.

        Generally there will be little-or-no need for PyCarta users
        to create an instance of a Workspace object.
        """
        self._entries = dict(*args, **kwds)
        self._entries["id"] = self._entries.get("id", str(uuid4()))

    # abstract methods for MutableMapping
    def __getitem__(self, key): return self._entries[key]

    def __setitem__(self, key, value): self._entries[key] = value

    def __delitem__(self, key): del self._entries[key]

    def __iter__(self): return iter(self._entries)

    def __len__(self): return len(self._entries)

    @property
    def id(self) -> str: return self["id"]


class Template(MutableMapping):
    def __init__(self, *args, **kwds):
        """
        While HyperThought 2.0 provides Workflow, Decision, and Process
        objects derived from `Element` that expose the `Element.id`
        interface, no such class exists for Templates. This object
        is a thin wrapper around a python dict that exposes this
        same `Template.id` interface for Templates.

        Generally there will be little-or-no need for PyCarta users
        to create an instance of a Template object.
        """
        self._entries = dict(*args, **kwds)
        self._entries["key"] = self._entries.get("key", str(uuid4()))

    # abstract methods for MutableMapping
    def __getitem__(self, key): return self._entries[key]

    def __setitem__(self, key, value): self._entries[key] = value

    def __delitem__(self, key): del self._entries[key]

    def __iter__(self): return iter(self._entries)

    def __len__(self): return len(self._entries)

    @property
    def id(self) -> str: return self["key"]


class KeyFinder:
    def __init__(self):
        """
        Unique identifiers are pervasive throughout the HyperThought API, but
        these are presented in multiple forms, e.g. JSON packages with
        different formats, objects that expose the `cls.id` interface, or
        to provide a more user-friendly way of getting a UUID than to copy-
        paste from the URL of the corresponding HyperThought page.
        """
        self._finderFunctions = []
        self.register(KeyFinder.is_guid)

    def register(self, func: Callable) -> Optional[str]:
        """
        Registers a function to be used to find keys.
        This function should take one positional parameter,
        the object in which the key may be found.

        Parameters
        ----------
        func : unary function
            Function/functor used to return a key from an object.

        Returns
        -------
        str or None
            The key or None if not found/present
        """
        self._finderFunctions.append(func)

    def __call__(self, obj) -> Optional[str]:
        for func in self._finderFunctions:
            try:
                if key := func(obj):
                    return key
            except:  # noqa: E722
                pass
        return None

    @staticmethod
    def is_guid(x) -> Optional[str]:
        """Returns whether the object is a UUID. None if not."""
        try:
            if re.match(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', x):
                return x
        except TypeError:
            pass
        return None

    @staticmethod
    def attr_factory(attr):
        """
        Returns a function that attempts to look up an object
        attribute by name.
        """
        def func(obj):
            return getattr(obj, attr, None)
        return func

    @staticmethod
    def getitem_factory(*keys):
        """
        Returns a function that looks up a (potentially nested)
        entries in a container (or nested containers).

        Parameters
        ----------
        *keys : indexers
            Index to the container(s). These can be dict keys,
            tuple or list indices, or a combination.

        Examples
        --------
            c = ['a', 'b', 'c']
            f = getitem_factory(1)
            f(c) # returns 'b'

            c = [[1, 2], [3, 4]]
            f = getitem_factory(1, 0)
            f(c) # returns 3
        """
        def func(obj):
            try:
                for k in keys[:-1]:
                    obj = obj[k]
                return obj[keys[-1]]
            except (KeyError, IndexError):
                return None
        return func


class HyperThoughtKeyFinder(KeyFinder):
    def __init__(self, auth: Optional[Union[str, ht.auth.Authorization]]=None):
        """
        Unique identifiers are pervasive throughout the HyperThought API, but
        these are presented in multiple forms, e.g. JSON packages with
        different formats, objects that expose the `cls.id` interface, or
        to provide a more user-friendly way of getting a UUID than to copy-
        paste from the URL of the corresponding HyperThought page.

        This class registers functions able to return the key from known
        HyperThought objects.

        Parameters
        ----------
        auth : hyperthought.auth.Authorization
            Agent to handle communication with the HyperThought server.
        """
        # Register basic HyperThought objects
        super().__init__()
        self._auth = None
        self.auth = auth
        # workspace, document: [id]
        self.register(KeyFinder.getitem_factory("id"))
        # templates: [key]
        self.register(KeyFinder.getitem_factory("key"))
        # workflow, process: [content][pk] <- as returned from function call
        self.register(KeyFinder.getitem_factory("content", "pk"))
        # Element (and derived), Workspace, Template: obj.id
        self.register(KeyFinder.attr_factory("id"))
        # Search using HyperThought path
        self.register(self.key_from_path)

    @property
    def auth(self) -> ht.auth.Authorization:
        return self._auth

    @auth.setter
    def auth(self, auth:Union[str, ht.auth.Authorization]) -> None:
        """
        Sets the HyperThought Authorization agent that will be used to
        access/query the HyperThought server.

        Parameters
        ----------
        auth : str or hyperthought.auth.Authorization
            The HyperThought API token or hyperthought.auth.Authorization
            agent that manages communication with the HyperTHought server.
        """
        if isinstance(auth, ht.auth.Authorization):
            self._auth = auth
        else:
            self._auth = ht.auth.Authorization(auth_payload=auth)

    def key_from_path(self, path: str) -> str:
        """
        Accepts a string in the form,

            workspace/template/path/to/element

        will return the UUID of the object at that location.

        Parameters
        ----------
        path : str
            Path from the workspace to the object of interest.
        """
        auth = self.auth
        split = path.split("/")
        # get workspace
        workspaceApi = ht.api.workspaces.WorkspacesAPI(auth)
        spaceId = [
            self(ws)
            for ws in workspaceApi.get_workspaces()
            if ws["name"] == split[0]][0]
        if len(split) == 1:
            return spaceId
        # templates
        workflowApi = ht.api.workflow.WorkflowAPI(auth)
        objId = [
            self(t)
            for t in workflowApi.get_templates(spaceId)
            if t["name"] == split[1]][0]
        # workflows/process
        for p in split[2:]:
            objId = [
                self(child)
                for child in workflowApi.get_children(objId)
                if child["content"]["name"] == p][0]
        return objId
