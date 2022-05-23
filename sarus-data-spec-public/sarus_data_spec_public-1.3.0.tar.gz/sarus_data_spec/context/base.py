from types import TracebackType
import typing as t

from sarus_data_spec.bounds import Bounds
from sarus_data_spec.context.state import (
    pop_global_context,
    push_global_context,
)
from sarus_data_spec.context.typing import Context
from sarus_data_spec.factory import Factory
from sarus_data_spec.manager.typing import Manager
from sarus_data_spec.marginals import Marginals
from sarus_data_spec.predicate import Predicate
from sarus_data_spec.protobuf import type_name
from sarus_data_spec.schema import Schema
from sarus_data_spec.size import Size
from sarus_data_spec.storage.typing import Storage
import sarus_data_spec as s
import sarus_data_spec.protobuf as sp


class Base(Context):
    """A factory class with all the config"""

    def __init__(self) -> None:
        self._factory = Factory()
        # Register relevant classes
        self.factory().register(
            type_name(sp.Dataset),
            lambda protobuf: s.Dataset(t.cast(sp.Dataset, protobuf)),
        )
        self.factory().register(
            type_name(sp.Scalar),
            lambda protobuf: s.Scalar(t.cast(sp.Scalar, protobuf)),
        )
        self.factory().register(
            type_name(sp.Status),
            lambda protobuf: s.Status(t.cast(sp.Status, protobuf)),
        )
        self.factory().register(
            type_name(sp.Transform),
            lambda protobuf: s.Transform(t.cast(sp.Transform, protobuf)),
        )
        self.factory().register(
            type_name(sp.Attribute),
            lambda protobuf: s.Attribute(t.cast(sp.Attribute, protobuf)),
        )

        self.factory().register(
            type_name(sp.VariantConstraint),
            lambda protobuf: s.VariantConstraint(
                t.cast(sp.VariantConstraint, protobuf)
            ),
        )
        self.factory().register(
            type_name(sp.Predicate),
            lambda protobuf: Predicate(t.cast(sp.Predicate, protobuf)),
        )
        self.factory().register(
            type_name(sp.Schema),
            lambda protobuf: Schema(t.cast(sp.Schema, protobuf)),
        )
        self.factory().register(
            type_name(sp.Marginals),
            lambda protobuf: Marginals(t.cast(sp.Marginals, protobuf)),
        )
        self.factory().register(
            type_name(sp.Size),
            lambda protobuf: Size(t.cast(sp.Size, protobuf)),
        )
        self.factory().register(
            type_name(sp.Bounds),
            lambda protobuf: Bounds(t.cast(sp.Bounds, protobuf)),
        )

    def factory(self) -> Factory:
        return self._factory

    def storage(self) -> Storage:
        raise NotImplementedError()

    def manager(self) -> Manager:
        raise NotImplementedError()

    def __enter__(self) -> Context:
        push_global_context(self)
        return self

    def __exit__(
        self,
        type: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        traceback: t.Optional[TracebackType],
    ) -> None:
        pop_global_context()
        return None
