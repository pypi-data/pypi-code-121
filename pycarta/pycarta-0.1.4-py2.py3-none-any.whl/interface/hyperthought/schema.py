import hyperthought as ht
import json
import re

from abc import ABC, abstractmethod
from collections.abc import Mapping
from copy import deepcopy
from io import IOBase
from pprint import pformat
from typing import Optional, Union, Any, List, Dict
from .base import HyperThoughtKeyFinder


__all__ = ["build"]


JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class ElementFactory(ABC):
    def __init__(
            self,
            name: str,
            **kwds
    ):
        """
        Basic element builder. This controls the API for all other
        specific builders.

        Parameters
        ----------
        name : str
            Name of element created by this builder.
        """
        self.name = name
        self.keyFinder = lambda x: x

    @abstractmethod
    def _element_factory(self, parent, **kwds) -> Optional[ht.api.workflow.Element]:
        """
        Derived classes must define how the element is to be created.
        """
        return None

    @abstractmethod
    def _child_factory(self, element, **kwds):
        """
        Derived classes must define how the children (metadata or
        Workflow/Process) are to be created.
        """
        return None

    @abstractmethod
    def _push(self, auth, element):
        """
        Derived class must define how to upload (push) the objects to
        HyperThought.
        """
        return None

    @staticmethod
    def is_guid(x):
        """
        Checks if the passed parameter is a UUID.
        """
        strx = str(x)
        if re.match(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', strx):
            return x
        else:
            return None

    def build(
            self,
            auth: Optional[ht.auth.Authorization] = None,
            *,
            workspace: str = None,
            parent: str = "00000000-0000-0000-0000-000000000000"
    ) -> None:
        """
        Builds the Element defined by this Builder. This is generally called on Factory
        that connects its element to one already in HyperThought.

        Parameters
        ----------
        auth : hyperthought.auth.Authorization
            Authorization agent used to manage communication to/from the HyperThought server.
            The default (None) is for debugging--to create the structure locally without
            pushing the result to the HyperThought server.
        workspace : str
            Workspace in which to build the Elements.
        parent : str
            Path or UID of a record that will serve as the parent, which already exists in
            HyperThought, to the constructed object. The default
            (00000000-0000-0000-0000-000000000000) is used for debugging.

        Returns
        -------
        ht.api.workflow.Element
            Top-level element created by this code.

        Example
        -------
        class MyFactory(ElementFactory):
            ...

        factory = MyFactory("foo")
        factory.build(auth, "workspace/template/path/to/parent")
        """
        # create a key finder using this authorization agent
        if auth:
            self.keyFinder = HyperThoughtKeyFinder(auth)
        # manage the location
        space_id = self.keyFinder(workspace)
        parent_id = self.keyFinder(parent)
        if not ElementFactory.is_guid(parent_id):
            raise ValueError(f"'{parent}' is not a recognized HyperThought path or record ID.")
        # generate the element and the children
        element = self._element_factory(parent_id, workspace=space_id)
        if auth is not None:
            # execute the construction
            self._push(auth, element)
            # Update the parent already in HyperThought
            # construct a workflow API object
            api = ht.api.workflow.WorkflowAPI(auth)
            api.redraw_canvas(workflow_id=parent_id)
        return element


class WorkflowFactory(ElementFactory):
    _builders = []  # used to store the children (Workflow/Process) of this Element

    def __init__(
            self,
            name: str,
            **kwds
    ):
        """
        This builds a Workflow entry in HyperThought

        Parameters
        ----------
        name : str
            Name of element created by this builder.
        """
        super().__init__(name)

    def _element_factory(
            self,
            parent: Union[str, ht.api.workflow.Workflow],
            *,
            workspace: Optional[str] = None
    ) -> ht.api.workflow.Workflow:
        """
        Build a Workflow.
        """
        space_id = self.keyFinder(workspace)
        obj = ht.api.workflow.Workflow(
            name=self.name,
            assignee=None,
            notes=None,
            due_date=None,
            parent=parent if isinstance(parent, ht.api.workflow.Workflow) else None,
            parent_id=self.keyFinder(parent),
            space_id=space_id
        )
        self._child_factory(obj)
        return obj

    def _child_factory(self, element: ht.api.workflow.Workflow, **kwds) -> None:
        cls = type(self)
        # add elements from this class
        for builder in getattr(cls, "_builders", []):
            element.add_child(builder._element_factory(element))

    def _push(self, auth, element):
        api = ht.api.workflow.WorkflowAPI(auth)
        api.create_workflow(element)


class ProcessFactory(ElementFactory):
    _builders = []  # used to construct the children (metadata or Workflow/Process) of this Element

    def __init__(
            self,
            name: str,
            **kwds
    ):
        """
        Basic element builder. This controls the API for all other
        specific builders.

        Parameters
        ----------
        name : str
            Name of element created by this builder.
        """
        super().__init__(name)

    def _element_factory(
            self,
            parent: Union[str, ht.api.workflow.Workflow],
            *,
            workspace: Optional[str] = None
    ) -> ht.api.workflow.Process:
        obj = ht.api.workflow.Process(
            name=self.name,
            assignee=None,
            notes=None,
            due_date=None,
            parent=parent if isinstance(parent, ht.api.workflow.Workflow) else None,
            parent_id=self.keyFinder(parent) if isinstance(parent, str) else None
        )
        self._child_factory(obj)
        return obj

    def _child_factory(self, element: ht.api.workflow.Process, **kwds) -> None:
        cls = type(self)
        # add metadata from this class
        for builder in getattr(cls, "_builders", []):
            element.add_metadata_item(builder._element_factory(element))

    def _push(self, auth, element):
        api = ht.api.workflow.WorkflowAPI(auth)
        api.create_process(element)


class MetadataFactory(ElementFactory):
    def __init__(
            self,
            key,
            *,
            value: Optional[Any] = None,
            units: Optional[str] = None,
            annotation: Optional[str] = None
    ):
        """
        Basic element builder. This controls the API for all other
        specific builders.

        Parameters
        ----------
        key : str
            Name of the metadata object.
        value : Optional[Any]
            Default value to be stored in this entry
        units : Optional[str]
            Units for this entry
        annotation : Optional[str]
            Default free form note for this entry.
        """
        super().__init__(key)
        self.key = key
        self.value = value
        self.units = units
        self.annotation = annotation

    def _element_factory(
            self,
            parent: Union[str, ht.api.workflow.Process],
            **kwds
    ) -> ht.api.workflow.MetadataItem:
        return ht.api.workflow.MetadataItem(
            key=self.key,
            value=self.value,
            units=self.units,
            annotation=self.annotation,
            type_=None
        )

    def _child_factory(self, element: ht.api.workflow.MetadataItem, **kwds) -> None:
        # Nothing to do because metadata items are not hierarchical.
        pass

    def _push(self, auth, element):
        # Nothing to do because metadata items cannot be pushed outside a Process object.
        pass


class Schema(Mapping):
    def __init__(self, src: Optional[Union[str, IOBase, JSONType]] = None):
        self.__knownClasses = {
            'WorkflowBuilder': WorkflowFactory,
            'ProcessBuilder': ProcessFactory
        }
        if src:
            self.generate(src)

    def __getitem__(self, key):
        return self.__knownClasses[key]

    def __iter__(self):
        return iter(self.__knownClasses)

    def __len__(self):
        return len(self.__knownClasses)

    def _is_workflow(self, key_class_instance):
        obj = self.__knownClasses[key_class_instance] if isinstance(key_class_instance, str) else key_class_instance
        return isinstance(obj, WorkflowFactory) or issubclass(obj, WorkflowFactory)

    def _is_process(self, key_class_instance):
        obj = self.__knownClasses[key_class_instance] if isinstance(key_class_instance, str) else key_class_instance
        return isinstance(obj, ProcessFactory) or issubclass(obj, ProcessFactory)

    def generate(self, schema, reset: bool = True):
        """
        Generate the elements defined in a JSON-formatted schema where each
        entry has the following structure:

            {
                "id": (class name, str),
                "type": (name of the base class, str),
                "contains": (contents of the class, type-dependent list)
            }

        Type must be one of WorkflowBuilder, ProcessBuilder, or a class that
        derives from these. The type-dependent list for the "contains" field
        depends on whether the entry is of type WorkflowBuilder or
        ProcessBuilder. For WorkflowBuilder, each entry should be of the
        following form:

            {
                "type": (type name of the entry, str),
                "name": (name of this entry, str)
            }

        For ProcessBuilder, each entry in the "contains" field should be of the
        following form:

            {
                "key": (key name in the hyperthought Key/Value pair, str, required),
                "value": (default value, str or scalar, optional),
                "units": (units for this key, str, optional)
                "annotation": (str, optional)
            }

        Parameters
        ----------
        schema : str, list, or file object
            Filename or file object containing the JSON schema or a
            JSON-formatted object of the schema.

        reset : bool
            Whether to reset the existing schema. Default is True, that is, each
            call will generate a new Schema. If False, then the classes created
            will build upon one another from one file to the next.

        Returns
        -------
        instance : Schema
            Instance of the Schema type.
        """
        if reset:
            self.__knownClasses = {
                'WorkflowBuilder': WorkflowFactory,
                'ProcessBuilder': ProcessFactory
            }
        # open the JSON file that contains the schema
        if isinstance(schema, str):
            with open(schema, 'rb') as ifs:
                schema = json.load(ifs)
        elif issubclass(type(schema), IOBase):
            schema = json.load(schema)
        if not isinstance(schema, list):
            raise ValueError("The schema must be a list of types.")
        else:
            schema = deepcopy(schema)
        # counter to check for a missing definition
        maxlength = len(schema)
        missing = set()
        while True:
            # get the first entry
            try:
                entry = schema.pop(0)
            except IndexError:
                # all entries have been processed
                break
            # get the key/value pairs from the schema
            try:
                classname = entry["id"]
                basename = entry["type"]
                contents = entry.get("contains", [])
            except KeyError:
                raise IOError("Entry {} does not have the proper "
                              "format.".format(pformat(entry)))
            # create the class
            try:
                base = self[basename]

                if self._is_process(base):
                    oldkeys = {
                        factory.key for factory
                        in getattr(base, "_builders", [])
                    }
                    newkeys = {
                        entry["key"] for entry in contents
                    }
                    methods = {
                        '_builders': (
                            [ # unmodified existing builders
                                factory
                                for factory in getattr(base, "_builders", [])
                                if factory.key in (oldkeys - newkeys)
                            ] +
                            [ # updated existing builders
                                MetadataFactory(
                                    key=factory.key,
                                    value=entry.get("value", factory.value),
                                    units=entry.get("units", factory.units),
                                    annotation=entry.get("annotation", factory.annotation)
                                )
                                for factory in getattr(base, "_builders", [])
                                for entry in contents
                                if (
                                    factory.key in oldkeys.intersection(newkeys) and
                                    entry["key"] == factory.key
                                )
                            ] +
                            [ # new builders
                                MetadataFactory(**entry)
                                for entry in contents
                                if entry["key"] in (newkeys - oldkeys)
                            ]
                        ),
                        '__init__': Schema._init_factory(base)
                    }
                elif self._is_workflow(base):
                    oldnames = {
                        factory.name for factory
                        in getattr(base, "_builders", [])
                    }
                    newnames = {
                        entry["name"] for entry in contents
                    }
                    methods = {
                        '_builders': (
                            [ # unmodified existing builders
                                factory
                                for factory in getattr(base, "_builders", [])
                                if factory.name in (oldnames - newnames)
                            ] +
                            [ # new builders
                                self[entry["type"]](entry["name"])
                                for entry in contents
                                if entry["name"] in newnames
                            ]
                        ),
                        '__init__': Schema._init_factory(base)
                    }
                else:
                    raise ValueError("{} is not a recognized type.".format(base))

                self.__knownClasses[classname] = type(
                    classname,
                    (base,),
                    methods
                )

                # successfully generated a class
                # reset the counter that checks for missing definitions
                maxlength = len(schema)
                missing = missing - {classname}
            except (KeyError, TypeError):
                # A key error means we haven't reached the definition
                # of an entry yet.
                schema.append(entry)
                maxlength = maxlength - 1
                missing.add(classname)
                if maxlength < 1:
                    # we've gone through every entry in the schema at least once
                    # without defining a type that was used.
                    raise IOError("The following objects have not been defined "
                                  "in the schema: {}.".format(list(missing)))
        return self

    @staticmethod
    def _init_factory(base):
        def init(self, name):
            base.__init__(self, name)

        return init


def build(
        auth: ht.auth.Authorization,
        *,
        typename: Union[str, List[str]],
        name: Union[str, List[str]],
        parent: Union[str, List[str]],
        workspace: Union[str, List[str]],
        schema: Union[str, IOBase, JSONType, Schema],
        force: bool = False
) -> None:
    """
    Basic interface for building one or more Workflow or Process objects from
    a schema.

    Parameters
    ----------
    auth : hyperthought.auth.Authorization
        Agent that handles authentication with the HyperThought server.

    typename : str or list[str]
        The element type to be constructed. If more than one Element is to be
        built, then either a typename should be specified for each or, if only
        one typename is given, all Elements will be of the same type.

    name : str or list[str]
        The name of the element to be constructed. If more than one Element is
        to be built, then either a name must be specified for each or, if only
        one name is given, all Elements will be given the same name.

    parent : str or list[str]
        The parent of the element to be constructed. If more than one Element
        is to be built, then either a parent must be given for each or, if only
        one parent is given, all Elements will be built off that same parent.

    workspace : str or list[str]
        The workspace into which the element(s) are to be built. If more than
        one Element is to be built, then either a workspace must be give for
        each or, if only one workspace is given, all Elements are created in
        that one workspace.

    schema : str, io.IOBase, JSON-formatted list, or Schema
        The schema that defines the structure of each Element to be built.

    force : bool (optional)
        If an Element of the same name already exists, a new one will not be
        created by default (force = False, default). If force is True, then
        a new object with the same name will be created.

    Returns
    -------
    None
    """
    def is_iter(x):
        return hasattr(x, "__iter__") and not isinstance(x, str)

    def match_len(a, b):
        a = list(a) if is_iter(a) else [a]
        b = list(b) if is_iter(b) else [b]
        if len(a) != len(b):
            if len(a) == 1:
                a = len(b)*a
            elif len(b) == 1:
                b = len(a)*b
            else:
                raise ValueError(
                    "Lengths of typenames, names, parents, and workspace "
                    "parameters are not compatible."
                )
        return a, b

    # ##### normalize function parameters ##### #
    # make sure schema is a Schema object.
    if not isinstance(schema, Schema):
        schema = Schema(schema)
    # Make sure typenames, names, parents, and workspaces are compatible.
    typename, name = match_len(typename, name)
    parent, name = match_len(parent, name)
    workspace, name = match_len(workspace, name)
    # Parent path must begin with the workspace name.
    for i, (p, w) in enumerate(zip(parent, workspace)):
        if (
            HyperThoughtKeyFinder.is_guid(p) or
            HyperThoughtKeyFinder.is_guid(w)
        ):
            # if the parent or workspace is a UUID, then it cannot be used to
            # construct an object path
            continue
        if not p.startswith(w):
            parent[i] = w.strip("/") + "/" + p.strip("/")
    # ##### Now build everything requested. ##### #
    key_finder = HyperThoughtKeyFinder(auth)
    for t, n, p, w in zip(typename, name, parent, workspace):
        path = p + "/" + n
        if (key_finder(path) is None) or force:
            # This object doesn't exist or the user has asked to force the
            # build.
            builder = schema[t](n)
            _ = builder.build(
                auth=auth,
                workspace=w,
                parent=p
            )
    return
