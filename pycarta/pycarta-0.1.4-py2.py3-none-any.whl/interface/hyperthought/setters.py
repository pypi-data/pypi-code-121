import warnings

import hyperthought as ht
from .base import HyperThoughtKeyFinder
from typing import Dict, Union, Any, Optional
from warnings import warn


__all__ = ["update_process"]


class _HyperthoughtUpdateAgent:
    def __init__(self, auth: ht.auth.Authorization):
        self.auth = auth
        self.api = ht.api.workflow.WorkflowAPI(auth)
        self.document = dict()
        self.metadata = None

    def is_process(self):
        return self.document.get("processType") == "process"

    def retrieve_node(self, node: Union[str, ht.api.workflow.Workflow]) -> None:
        nodeId = HyperThoughtKeyFinder(self.auth)(node)
        self.document = self.api.get_document(nodeId)
        self.retrieve_metadata()

    def retrieve_metadata(self):
        metadata = self.document.get("metadata", [])
        self.metadata = [
            ht.api.workflow.MetadataItem(
                # Default in case key is missing.
                key=m.get("keyName", "[unnamed]"),
                value=m["value"]["link"],
                units=m["unit"],
                annotation=m["annotation"],
                type_=m["value"]["type"] or None
            ) for m in metadata
            # delete empty Process Node entries
            if (
                m["value"]["link"] or
                m["unit"] or
                m["annotation"] or
                m["value"]["type"]
            )
        ]

    def update_values(self, add: bool = False, **kwargs) -> None:
        # update metadata fields
        metadata = self.metadata
        # metadata is stored as a list, but we want to access it as a map.
        keyIndexMap = {m.key: i for i, m in enumerate(metadata)}
        for key, value in kwargs.items():
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                type_ = None
                if str(value).startswith("/files/"):
                    type_="link"
                if key in keyIndexMap:
                    # update existing metadata values
                    m = metadata[keyIndexMap[key]]
                    metadata[keyIndexMap[key]] = ht.api.workflow.MetadataItem(
                        key=m.key,
                        value=value,
                        units=m.units,
                        annotation=m.annotation,
                        type_=type_
                    )
                elif add:
                    # add new entry (if requested by the user)
                    metadata.append(
                        ht.api.workflow.MetadataItem(
                            key=key,
                            value=value,
                            type_=type_
                        )
                    )
                else:
                    warn(f"{key} not found. No value set.")

    def update_units(self, add: bool = False, **kwargs) -> None:
        # update metadata fields
        metadata = self.metadata
        # metadata is stored as a list, but we want to access it as a map.
        keyIndexMap = {m.key: i for i, m in enumerate(metadata)}
        for key, value in kwargs.items():
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                if key in keyIndexMap:
                    # update existing metadata values
                    metadata[keyIndexMap[key]].units = value
                elif add:
                    # add new entry (if requested by the user)
                    metadata.append(
                        ht.api.workflow.MetadataItem(
                            key=key,
                            value=None,
                            units=value
                        )
                    )
                else:
                    warn(f"{key} not found. No unit set.")

    def update_annotation(self, add: bool = False, **kwargs) -> None:
        # update metadata fields
        metadata = self.metadata
        # metadata is stored as a list, but we want to access it as a map.
        keyIndexMap = {m.key: i for i, m in enumerate(metadata)}
        for key, value in kwargs.items():
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                if key in keyIndexMap:
                    # update existing metadata values
                    metadata[keyIndexMap[key]].annotation = value
                elif add:
                    # add new entry (if requested by the user)
                    metadata.append(
                        ht.api.workflow.MetadataItem(
                            key=key,
                            value=None,
                            annotation=value
                        )
                    )
                else:
                    warn(f"{key} not found. No annotation set.")

    def update(self):
        if self.metadata:
            self.document["metadata"] = [m.to_api_format() for m in self.metadata]
        self.api.update_document(self.document)


def update_process(
        auth: ht.auth.Authorization,
        node: Union[str, ht.api.workflow.Process],
        *,
        values: Optional[Dict[str, Any]] = None,
        units: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        add: bool = False
):
    """
    Update an existing Process Node in HyperThought.

    Parameters
    ----------
    auth : hyperthought.auth.Authorization
        Authorization agent that handles communication with the HyperThought
        server.
    node : str or hyperthought.api.workflow.Process
        Path, UUID, or Process object to be updated.
    values : dict[str, Any]
        Key-value pairs where the key represents an existing metadata entry in
        the Process Node and the value populates the value field in the Process
        Node.
    units : dict[str, str]
        Key-value pairs where the key represents an existing metadata entry in
        the Process Node and the value is the units for that entry.
    annotations: dict[str, str]
        Key-value pairs where the key represents an existing metadata entry in
        the Process Node and the value populates the annotation field in that
        entry.
    add : bool (optional)
        By default (`add = False`), keys from `values`, `units`, and
        `annotation` not already present in the Process Node will be skipped
        and a warning message issued. If `add = True` then missing keys will be
        added to the Process Node.

    Returns
    -------
    None
    """
    agent = _HyperthoughtUpdateAgent(auth)
    agent.retrieve_node(node)
    if agent.is_process():
        if values:
            agent.update_values(add=add, **values)
        if units:
            agent.update_units(add=add, **units)
        if annotations:
            agent.update_annotation(add=add, **annotations)
        agent.update()
