from __future__ import annotations

from typing import (
    Any,
    Collection,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    cast,
)
import pickle as pkl

from sarus_data_spec.base import Referring
from sarus_data_spec.transform import Transform
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


class Scalar(Referring[sp.Scalar]):
    """A python class to describe scalars"""

    def __init__(self, protobuf: sp.Scalar) -> None:
        if protobuf.spec.HasField("transformed"):
            transformed = protobuf.spec.transformed
            self._referred = {
                transformed.transform,
                *transformed.arguments,
                *list(transformed.named_arguments.values()),
            }

        super().__init__(protobuf=protobuf)

    def prototype(self) -> Type[sp.Scalar]:
        """Return the type of the underlying protobuf."""
        return sp.Scalar

    def name(self) -> str:
        return self._protobuf.name

    def doc(self) -> str:
        return self._protobuf.doc

    def is_transformed(self) -> bool:
        """Is the scalar composed."""
        return self._protobuf.spec.HasField("transformed")

    def is_remote(self) -> bool:
        """Is the dataspec a remotely defined dataset."""
        return self.manager().is_remote(self)

    def is_model(self) -> bool:
        """Is the scalar a model."""
        return self._protobuf.spec.HasField("model")

    def status(self) -> st.Status:
        return cast(st.Status, self.manager().status(self))

    def transform(self) -> st.Transform:
        return cast(
            st.Transform,
            self.storage().referrable(
                self.protobuf().spec.transformed.transform
            ),
        )

    def parents(
        self,
    ) -> Tuple[List[st.DataSpec], Dict[str, st.DataSpec]]:
        if not self.is_transformed():
            return list(), dict()

        args_id = self._protobuf.spec.transformed.arguments
        kwargs_id = self._protobuf.spec.transformed.named_arguments

        args_parents = [
            cast(st.DataSpec, self.storage().referrable(uuid))
            for uuid in args_id
        ]
        kwargs_parents = {
            name: cast(st.DataSpec, self.storage().referrable(uuid))
            for name, uuid in kwargs_id.items()
        }

        return args_parents, kwargs_parents

    def is_compliant(
        self,
        kind: st.ConstraintKind,
        public_context: List[str],
        epsilon: Optional[float] = None,
    ) -> bool:
        return self.manager().is_compliant(self, kind, public_context, epsilon)

    def variant(
        self,
        kind: st.ConstraintKind,
        public_context: List[str],
        epsilon: Optional[float] = None,
    ) -> Optional[st.DataSpec]:
        return self.manager().variant(self, kind, public_context, epsilon)

    def variant_constraint(self) -> Optional[st.VariantConstraint]:
        return self.manager().variant_constraint(self)

    def variants(self) -> Collection[st.DataSpec]:
        return self.manager().variants(self)

    def verifies(
        self,
        kind: st.ConstraintKind,
        public_context: Collection[str],
        epsilon: Optional[float],
    ) -> bool:
        variant_constraint = self.variant_constraint()
        if variant_constraint:
            return self.manager().verifies(
                variant_constraint=variant_constraint,
                kind=kind,
                public_context=public_context,
                epsilon=epsilon,
            )
        else:
            return False

    def value(self) -> st.DataSpecValue:
        return self.manager().value(self)

    async def async_value(self) -> st.DataSpecValue:
        return await self.manager().async_value(self)

    # A Visitor acceptor
    def accept(self, visitor: st.Visitor) -> None:
        visitor.all(self)
        if self.is_transformed():
            visitor.transformed(
                self,
                cast(
                    Transform,
                    self.storage().referrable(
                        self._protobuf.spec.transformed.transform
                    ),
                ),
                *(
                    cast(Scalar, self.storage().referrable(arg))
                    for arg in self._protobuf.spec.transformed.arguments
                ),
                **{
                    name: cast(Scalar, self.storage().referrable(arg))
                    for name, arg in self._protobuf.spec.transformed.named_arguments.items()  # noqa: E501
                },
            )
        else:
            visitor.other(self)

    def dot(self) -> str:
        """return a graphviz representation of the scalar"""

        class Dot(st.Visitor):
            visited: Set[st.DataSpec] = set()
            nodes: Dict[str, Tuple[str, str]] = {}
            edges: Dict[Tuple[str, str], str] = {}

            def transformed(
                self,
                visited: st.DataSpec,
                transform: st.Transform,
                *arguments: st.DataSpec,
                **named_arguments: st.DataSpec,
            ) -> None:
                if visited not in self.visited:
                    if visited.prototype() == sp.Dataset:
                        self.nodes[visited.uuid()] = (
                            visited.name(),
                            "Dataset",
                        )
                    else:
                        self.nodes[visited.uuid()] = (visited.name(), "Scalar")

                    if not visited.is_remote():
                        for argument in arguments:
                            self.edges[
                                (argument.uuid(), visited.uuid())
                            ] = transform.name()
                            argument.accept(self)
                        for _, argument in named_arguments.items():
                            self.edges[
                                (argument.uuid(), visited.uuid())
                            ] = transform.name()
                            argument.accept(self)
                    self.visited.add(visited)

            def other(self, visited: st.DataSpec) -> None:
                if visited.prototype() == sp.Dataset:
                    self.nodes[visited.uuid()] = (
                        visited.name(),
                        "Dataset",
                    )
                else:
                    self.nodes[visited.uuid()] = (visited.name(), "Scalar")

        visitor = Dot()
        self.accept(visitor)
        result = 'digraph {'
        for uuid, (label, node_type) in visitor.nodes.items():
            shape = "polygon" if node_type == "Scalar" else "ellipse"
            result += (
                f'\n"{uuid}" [label="{label} ({uuid[:2]})", shape={shape}];'
            )
        for (u1, u2), label in visitor.edges.items():
            result += f'\n"{u1}" -> "{u2}" [label="{label} ({uuid[:2]})"];'
        result += '}'
        return result


# Builders
def model(
    model_class: sp.Scalar.Model.ModelClass.V, *args: Any, **kwargs: Any
) -> Scalar:
    return Scalar(
        sp.Scalar(
            name=sp.Scalar.Model.ModelClass.Name(model_class),
            spec=sp.Scalar.Spec(
                model=sp.Scalar.Model(
                    model_class=model_class,
                    arguments=pkl.dumps(args),
                    named_arguments=pkl.dumps(kwargs),
                )
            ),
        )
    )


class Visitor:
    """A visitor class for Scalar"""

    def all(self, visited: Scalar) -> None:
        return

    def transformed(
        self,
        visited: Scalar,
        transform: Transform,
        *arguments: Scalar,
        **named_arguments: Scalar,
    ) -> None:
        return

    def other(self, visited: Scalar) -> None:
        return
