from __future__ import annotations

from datetime import datetime
from typing import List, Mapping, Optional, Type, cast

from sarus_data_spec.base import Referring
from sarus_data_spec.dataset import Dataset
from sarus_data_spec.manager.typing import Manager
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


class Status(Referring[sp.Status]):
    """A python class to describe status"""

    def __init__(self, protobuf: sp.Status) -> None:
        self._referred = {
            protobuf.dataset,
            protobuf.manager,
        }  # This has to be defined before it is initialized
        super().__init__(protobuf)

    def prototype(self) -> Type[sp.Status]:
        """Return the type of the underlying protobuf."""
        return sp.Status

    def datetime(self) -> datetime:
        return datetime.fromisoformat(self.protobuf().datetime)

    def ready(self) -> bool:
        return self.protobuf().stage.HasField("ready")

    def pending(self) -> bool:
        return self.protobuf().stage.HasField("pending")

    def processing(self) -> bool:
        return self.protobuf().stage.HasField("processing")

    def error(self) -> bool:
        return self.protobuf().stage.HasField("error")

    def dataset(self) -> Dataset:
        return cast(Dataset, self.storage().referrable(self._protobuf.dataset))

    def owner(
        self,
    ) -> Manager:  # TODO: Maybe find a better name, but this was shadowing the actual manager of this object.  # noqa: E501
        return cast(Manager, self.storage().referrable(self._protobuf.manager))


# Builders
def status(
    dataset: st.DataSpec,
    manager: Manager,
    stage: sp.Status.Stage,
    task: str,
    properties: Optional[Mapping[str, str]] = None,
) -> Status:
    """A builder to ease the construction of a status"""
    # If none of fields or type is defined, set type to Null
    return Status(
        sp.Status(
            dataset=dataset.uuid(),
            manager=manager.uuid(),
            datetime=datetime.now().isoformat(),
            task=task,
            stage=stage,
            properties=properties,
        )
    )


def last_status(dataspec: st.DataSpec) -> Optional[st.Status]:
    """Return a DataSpec's last status by sorted datetime."""
    statuses = cast(
        List[st.Status], dataspec.referring(sp.type_name(sp.Status))
    )
    sorted_statuses = sorted(
        statuses, key=lambda x: x.datetime(), reverse=True
    )
    return next(iter(sorted_statuses), None)


def pending(
    dataset: st.DataSpec,
    manager: Manager,
    task: str,
    properties: Optional[Mapping[str, str]] = None,
) -> Status:
    return status(
        dataset,
        manager,
        sp.Status.Stage(pending=sp.Status.Stage.Pending()),
        task,
        properties,
    )


def processing(
    dataset: st.DataSpec,
    manager: Manager,
    task: str,
    properties: Optional[Mapping[str, str]] = None,
) -> Status:
    return status(
        dataset,
        manager,
        sp.Status.Stage(processing=sp.Status.Stage.Processing()),
        task,
        properties,
    )


def ready(
    dataset: st.DataSpec,
    manager: Manager,
    task: str,
    properties: Optional[Mapping[str, str]] = None,
) -> Status:
    return status(
        dataset,
        manager,
        sp.Status.Stage(ready=sp.Status.Stage.Ready()),
        task,
        properties,
    )


def error(
    dataset: st.DataSpec,
    manager: Manager,
    task: str,
    properties: Optional[Mapping[str, str]] = None,
) -> Status:
    return status(
        dataset,
        manager,
        sp.Status.Stage(error=sp.Status.Stage.Error()),
        task,
        properties,
    )
