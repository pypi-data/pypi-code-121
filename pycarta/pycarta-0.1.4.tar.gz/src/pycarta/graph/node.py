import json
from collections.abc import Hashable
from pprint import pformat
from typing import Optional, Union, List
from uuid import uuid4

from ..base.logger import MetaLogger
from ..base.typing import JsonType


class Node(Hashable):
    """
    Container class for user-defined graphs uploaded to Carta.

    Attributes
    ----------
    id : str
        Identifier for a Node--this must be unique across all
        nodes. This differs from `label`.
    label : str
        A human-readable label that will be displayed for each node.
    properties : list[Node.Property]
        A list of properties.

    Classes
    -------
        Property
    """
    @staticmethod
    def ensure_list(x):
        if not hasattr(x, "__iter__") or isinstance(x, str):
            return [x]
        else:
            return list(x)

    class Property():
        """
        Container class to store node properties.

        Attributes
        ----------
        id : str
            Name of this property. While all properties in an instance of
            a Node must be unique, these need not be unique across Nodes.
            More specifically, `id` is not a UUID, it is human-readable,
            descriptive name.
        values : list
            List of values for this property.
        """
        def __init__(self, **kwds):
            """
            Crates a new instance of a property.

            Parameters
            ----------
            id/name : str
                Name of this property. `name` is an alias for `id`. If both
                are present, `id` takes precedence.
            values : list
                List of values for this property.
            properties : list
                List of subproperties.
            """
            self._id = kwds.get("id", kwds.get("name"))
            if self._id is None:
                raise TypeError(f"Node.Property missing 1 required "
                                 "positional parameter: 'id'")
            self.values = Node.ensure_list(kwds.get("values", []))
            if "properties" in kwds:
                self.properties = Node.ensure_list(kwds["properties"])
            else:
                self.properties = None

        @property
        def id(self): return self._id

        def json(self):
            """
            Returns a JSON-formatted representation of this property.

            Returns
            -------
            dict
            """
            rval = {
                "id": self.id,
                "values": [v for v in self.values if v is not None]
            }
            if self.properties is not None:
                rval["properties"] = [p.json() for p in self.properties]
            return rval

        @staticmethod
        def from_json(pkg: JsonType):
            """
            Creates a new `Node.Property` object from a JSON-formatted
            package.

            Parameters
            ----------
            pkg : JSON
                Package that contains a JSON-formatted representation of
                a `Node.Property`.

            Returns
            -------
            Node.Property
            """
            try:
                pkg = json.loads(json.dumps(pkg))
            except:
                raise ValueError("%s package is not valid JSON.", pformat(pkg))
            # if "values" in pkg:
            #     pkg["values"] = [v for v in pkg["values"] if v is not None]
            if "properties" in pkg:
                pkg["properties"] = [
                    Node.Property.from_json(p)
                    for p in Node.ensure_list(pkg["properties"])
                ]
            return Node.Property(**pkg)

    def __init__(
        self,
        label: str,
        *,
        id: str=None,
        properties=[]
    ):
        """
        Creates a new Node object.

        Parameters
        ----------
        label : str
            Label to use for the new node.
        id : str
            ID to use for the new node. If not specified, a universally
            unique identifier (UUID) will be created.
        properties : list[Node.Property]
            List of properties contained in this Node.
        """
        self._id = id or str(uuid4())
        self.label = label
        self.properties = properties or []

    def __hash__(self): return hash(self.id)

    @property
    def id(self): return self._id

    def json(self):
        """
        Returns a JSON-formatted representation of this Node.

        Returns
        -------
        dict
        """
        return {
            "id": self.id,
            "label": self.label,
            "properties": [p.json() for p in self.properties]
        }

    @staticmethod
    def from_json(pkg: JsonType):
        """
        Creates a new Node from a JSON-formatted representation of a Node.

        Parameters
        ----------
        pkg : dict
            JSON-formatted representation of the Node.

        Returns
        -------
        Node
        """
        try:
            pkg = json.loads(json.dumps(pkg))
        except:
            raise ValueError("%s package is not valid JSON.", pformat(pkg))
        if "properties" in pkg:
            pkg["properties"] = [
                Node.Property.from_json(p)
                for p in Node.ensure_list(pkg["properties"])
                if p is not None
            ]
        return Node(**pkg)
