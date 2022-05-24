from __future__ import annotations

import pickle as pkl
import typing as t

import numpy as np

from sarus_data_spec.base import Referrable
import sarus_data_spec.dataset as sd
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as sdt

try:
    from sarus_data_spec.path import paths
except ModuleNotFoundError:
    print('protection not available')


class Transform(Referrable[sp.Transform]):
    """A python class to describe transforms"""

    def prototype(self) -> t.Type[sp.Transform]:
        """Return the type of the underlying protobuf."""
        return sp.Transform

    def name(self) -> str:
        return self._protobuf.name

    def doc(self) -> str:
        return self._protobuf.doc

    def is_composed(self) -> bool:
        """Is the transform composed."""
        return self._protobuf.spec.HasField('composed')

    def is_variable(self) -> bool:
        """Is the transform a variable."""
        return self._protobuf.spec.HasField('variable')

    def is_external(self) -> bool:
        """Is the transform an external operation."""
        return self._protobuf.spec.HasField("external")

    def infer_output_type(
        self, *arguments: sdt.DataSpec, **named_arguments: sdt.DataSpec
    ) -> t.Tuple[str, t.Callable[[sdt.DataSpec], None]]:
        """Guess if the external transform output is a Dataset or a Scalar.

        Registers schema if it is a Dataset and returns the value type.
        """
        return self.manager().infer_output_type(
            self, *arguments, **named_arguments
        )

    def transforms(self) -> t.Set[sdt.Transform]:
        """return all transforms (and avoid infinite recursions/loops)"""

        class Transforms(sdt.TransformVisitor):
            visited: t.Set[sdt.Transform] = set()

            def all(self, visited: sdt.Transform) -> None:
                self.visited.add(visited)

            def composed(
                self,
                visited: sdt.Transform,
                transform: sdt.Transform,
                *arguments: sdt.Transform,
                **named_arguments: sdt.Transform,
            ) -> None:
                self.visited.add(transform)
                if transform not in self.visited:
                    transform.accept(self)
                for arg in arguments:
                    if arg not in self.visited:
                        arg.accept(self)
                for name, arg in named_arguments.items():
                    if arg not in self.visited:
                        arg.accept(self)

        visitor = Transforms()
        self.accept(visitor)
        return visitor.visited

    def variables(self) -> t.Set[sdt.Transform]:
        """Return all the variables from a composed transform"""
        return {
            transform
            for transform in self.transforms()
            if transform.is_variable()
        }

    def compose(
        self,
        *compose_arguments: sdt.Transform,
        **compose_named_arguments: sdt.Transform,
    ) -> sdt.Transform:
        class Compose(sdt.TransformVisitor):
            visited: t.Set[sdt.Transform] = set()
            result: sdt.Transform

            def variable(
                self,
                visited: sdt.Transform,
                position_name: t.Union[int, str] = 0,
            ) -> None:
                self.result = visited
                if isinstance(position_name, int):
                    if position_name < len(compose_arguments):
                        self.result = compose_arguments[position_name]
                else:
                    if position_name in compose_named_arguments:
                        self.result = compose_named_arguments[position_name]

            def composed(
                self,
                visited: sdt.Transform,
                transform: sdt.Transform,
                *arguments: sdt.Transform,
                **named_arguments: sdt.Transform,
            ) -> None:
                if visited not in self.visited:
                    self.result = composed(
                        transform,
                        *(
                            arg.compose(
                                *compose_arguments, **compose_named_arguments
                            )
                            for arg in arguments
                        ),
                        **{
                            name: arg.compose(
                                *compose_arguments, **compose_named_arguments
                            )
                            for name, arg in named_arguments.items()
                        },
                    )
                    self.visited.add(visited)
                else:
                    self.result = visited

            def other(self, visited: sdt.Transform) -> None:
                self.result = composed(
                    visited, *compose_arguments, **compose_named_arguments
                )

        visitor = Compose()
        self.accept(visitor)
        return visitor.result

    def apply(
        self,
        *apply_arguments: sdt.DataSpec,
        **apply_named_arguments: sdt.DataSpec,
    ) -> sdt.DataSpec:
        class Apply(sdt.TransformVisitor):
            visited: t.Dict[sdt.Transform, sdt.DataSpec] = {}
            result: sdt.DataSpec

            def variable(
                self,
                visited: sdt.Transform,
                position_name: t.Union[int, str] = 0,
            ) -> None:
                if isinstance(position_name, int):
                    if position_name < len(apply_arguments):
                        self.result = apply_arguments[position_name]
                else:
                    if position_name in apply_named_arguments:
                        self.result = apply_named_arguments[position_name]
                if self.result is None:
                    raise ValueError("Cannot substitute all variables")

            def composed(
                self,
                visited: sdt.Transform,
                transform: sdt.Transform,
                *arguments: sdt.Transform,
                **named_arguments: sdt.Transform,
            ) -> None:
                if visited not in self.visited:
                    self.result = t.cast(
                        sd.Dataset,
                        sd.transformed(
                            transform,
                            *(
                                arg.apply(
                                    *apply_arguments, **apply_named_arguments
                                )
                                for arg in arguments
                            ),
                            dataspec_type=None,
                            dataspec_name=None,
                            **{
                                name: arg.apply(
                                    *apply_arguments, **apply_named_arguments
                                )
                                for name, arg in named_arguments.items()
                            },
                        ),
                    )
                    self.visited[visited] = self.result

            def other(self, visited: sdt.Transform) -> None:
                self.result = sd.transformed(
                    visited,
                    *apply_arguments,
                    dataspec_type=None,
                    dataspec_name=None,
                    **apply_named_arguments,
                )

        visitor = Apply()
        self.accept(visitor)
        return visitor.result

    def abstract(
        self,
        *arguments: t.Union[int, str],
        **named_arguments: t.Union[int, str],
    ) -> sdt.Transform:
        return composed(
            self,
            *(variable(position_name=arg) for arg in arguments),
            **{
                name: variable(position_name=arg)
                for name, arg in named_arguments.items()
            },
        )

    def __call__(
        self,
        *arguments: t.Union[sdt.Transform, sdt.DataSpec, int, str],
        **named_arguments: t.Union[sdt.Transform, sdt.DataSpec, int, str],
    ) -> t.Union[sdt.Transform, sdt.DataSpec]:
        """Applies the transform to another element"""
        all_transforms = True
        all_datasets = True
        all_variables = True
        for arg in arguments:
            all_transforms = all_transforms and isinstance(arg, Transform)
            all_datasets = all_datasets and (isinstance(arg, sdt.DataSpec))
            all_variables = all_variables and (
                isinstance(arg, int) or isinstance(arg, str)
            )
        for arg in named_arguments.values():
            all_transforms = all_transforms and isinstance(arg, Transform)
            all_datasets = all_datasets and (isinstance(arg, sdt.DataSpec))
            all_variables = all_variables and (
                isinstance(arg, int) or isinstance(arg, str)
            )
        if all_transforms:
            return self.compose(
                *t.cast(t.Sequence[Transform], arguments),
                **t.cast(t.Mapping[str, Transform], named_arguments),
            )
        if all_datasets:
            return self.apply(
                *t.cast(t.Sequence[sdt.DataSpec], arguments),
                **t.cast(t.Mapping[str, sdt.DataSpec], named_arguments),
            )
        if all_variables:
            return self.abstract(
                *t.cast(t.Sequence[t.Union[int, str]], arguments),
                **t.cast(t.Mapping[str, t.Union[int, str]], named_arguments),
            )
        return self

    def __mul__(self, argument: sdt.Transform) -> sdt.Transform:
        return self.compose(argument)

    # A Visitor acceptor
    def accept(self, visitor: sdt.TransformVisitor) -> None:
        visitor.all(self)
        if self.is_composed():
            visitor.composed(
                self,
                t.cast(
                    Transform,
                    self.storage().referrable(
                        self._protobuf.spec.composed.transform
                    ),
                ),
                *(
                    t.cast(Transform, self.storage().referrable(transform))
                    for transform in self._protobuf.spec.composed.arguments
                ),
                **{
                    name: t.cast(
                        Transform, self.storage().referrable(transform)
                    )
                    for name, transform in self._protobuf.spec.composed.named_arguments.items()  # noqa: E501
                },
            )
        elif self.is_variable():
            var = self._protobuf.spec.variable
            if var.position == np.iinfo(np.int32).min32:
                visitor.variable(self, position_name=var.name)
            else:
                visitor.variable(self, position_name=var.position)
        else:
            visitor.other(self)

    def dot(self) -> str:
        """return a graphviz representation of the transform"""

        class Dot(sdt.TransformVisitor):
            visited: t.Set[sdt.Transform] = set()
            nodes: t.Dict[str, str] = {}
            edges: t.Set[t.Tuple[str, str]] = set()

            def variable(
                self,
                visited: sdt.Transform,
                position_name: t.Union[int, str] = 0,
            ) -> None:
                self.nodes[visited.uuid()] = str(position_name)

            def composed(
                self,
                visited: sdt.Transform,
                transform: sdt.Transform,
                *arguments: sdt.Transform,
                **named_arguments: sdt.Transform,
            ) -> None:
                if visited not in self.visited:
                    transform.accept(self)
                    for argument in arguments:
                        if argument.is_composed():
                            self.edges.add(
                                (
                                    argument.protobuf().spec.composed.transform,  # noqa: E501
                                    transform.uuid(),
                                )
                            )
                        else:
                            self.edges.add((argument.uuid(), transform.uuid()))
                        argument.accept(self)
                    for _, argument in named_arguments.items():
                        if argument.is_composed():
                            self.edges.add(
                                (
                                    argument.protobuf().spec.composed.transform,  # noqa: E501
                                    transform.uuid(),
                                )
                            )
                        else:
                            self.edges.add((argument.uuid(), transform.uuid()))
                        argument.accept(self)
                    self.visited.add(visited)

            def other(self, visited: sdt.Transform) -> None:
                self.nodes[visited.uuid()] = visited.name()

        visitor = Dot()
        self.accept(visitor)
        result = 'digraph {'
        for uuid, label in visitor.nodes.items():
            result += f'\n"{uuid}" [label="{label} ({uuid[:2]})"];'
        for u1, u2 in visitor.edges:
            result += f'\n"{u1}" -> "{u2}";'
        result += '}'
        return result


# Builders
def identity() -> Transform:
    return Transform(
        sp.Transform(
            name='Identity',
            spec=sp.Transform.Spec(identity=sp.Transform.Identity()),
            inversible=True,
            schema_preserving=True,
        )
    )


def variable(position_name: t.Union[int, str] = 0) -> Transform:
    if isinstance(position_name, int):
        return Transform(
            sp.Transform(
                name='Variable',
                spec=sp.Transform.Spec(
                    variable=sp.Transform.Variable(position=position_name)
                ),
                inversible=True,
                schema_preserving=True,
            )
        )
    return Transform(
        sp.Transform(
            name='Variable',
            spec=sp.Transform.Spec(
                variable=sp.Transform.Variable(
                    name=position_name, position=np.iinfo(np.int32).min32
                )
            ),
            inversible=True,
            schema_preserving=True,
        )
    )


def composed(
    transform: sdt.Transform,
    *arguments: sdt.Transform,
    **named_arguments: sdt.Transform,
) -> sdt.Transform:
    if transform.is_composed():
        # We want to compose simple transforms only
        return transform.compose(*arguments, **named_arguments)
    return Transform(
        sp.Transform(
            name='Composed',
            spec=sp.Transform.Spec(
                composed=sp.Transform.Composed(
                    transform=transform.uuid(),
                    arguments=(a.uuid() for a in arguments),
                    named_arguments={
                        n: a.uuid() for n, a in named_arguments.items()
                    },
                )
            ),
        )
    )


def external(
    op: sp.Transform.ExternalOp.V, *args: t.Any, **kwargs: t.Any
) -> Transform:
    return Transform(
        sp.Transform(
            name=sp.Transform.ExternalOp.Name(op),
            spec=sp.Transform.Spec(
                external=sp.Transform.External(
                    arguments=pkl.dumps(args),
                    named_arguments=pkl.dumps(kwargs),
                    op=op,
                ),
            ),
        )
    )


def project(projection: sdt.Type) -> Transform:
    return Transform(
        sp.Transform(
            name='Project',
            spec=sp.Transform.Spec(
                project=sp.Transform.Project(projection=projection.protobuf())
            ),
            inversible=False,
            schema_preserving=False,
        )
    )


def filter(filter: sdt.Type) -> Transform:
    return Transform(
        sp.Transform(
            name='Filter',
            spec=sp.Transform.Spec(
                filter=sp.Transform.Filter(filter=filter.protobuf())
            ),
            inversible=False,
            schema_preserving=False,
        )
    )


def shuffle() -> Transform:
    return Transform(
        sp.Transform(
            name='Shuffle',
            spec=sp.Transform.Spec(shuffle=sp.Transform.Shuffle()),
            inversible=False,
            schema_preserving=True,
        )
    )


def join(on: sdt.Type) -> Transform:
    return Transform(
        sp.Transform(
            name='Join',
            spec=sp.Transform.Spec(join=sp.Transform.Join(on=on.protobuf())),
            inversible=False,
            schema_preserving=False,
        )
    )


def cast(type: sdt.Type) -> Transform:
    return Transform(
        sp.Transform(
            name='Cast',
            spec=sp.Transform.Spec(
                cast=sp.Transform.Cast(type=type.protobuf())
            ),
            inversible=False,
            schema_preserving=False,
        )
    )


def sample(fraction_size: t.Union[float, int]) -> Transform:
    return Transform(
        sp.Transform(
            name='Sample',
            spec=sp.Transform.Spec(
                sample=sp.Transform.Sample(size=fraction_size)
                if isinstance(fraction_size, int)
                else sp.Transform.Sample(fraction=fraction_size)
            ),
            inversible=False,
            schema_preserving=False,
        )
    )


def user_settings(user_type: sdt.Type) -> Transform:
    return Transform(
        sp.Transform(
            name='Updated_schema',
            spec=sp.Transform.Spec(
                user_settings=sp.Transform.UserSettings(
                    type=user_type.protobuf()
                )
            ),
            inversible=True,
            schema_preserving=False,
        )
    )


def synthetic() -> Transform:
    return Transform(
        sp.Transform(
            name="Synthetic data",
            spec=sp.Transform.Spec(
                synthetic=sp.Transform.Synthetic(),
            ),
            inversible=False,
            schema_preserving=True,
        )
    )


def protect(
    protected_entities: t.List[t.List[t.Any]],
    public_entities: t.Optional[t.List[t.List[t.Any]]] = None,
) -> Transform:
    if public_entities is None:
        public_entities = []
    return Transform(
        sp.Transform(
            name='Dataset with Protected Entity',
            spec=sp.Transform.Spec(
                protect_dataset=sp.Transform.Protect(
                    protected_entities=[
                        path.protobuf() for path in paths(protected_entities)
                    ],
                    public_entities=[
                        path.protobuf() for path in paths(public_entities)
                    ],
                )
            ),
            inversible=True,
            schema_preserving=False,
        )
    )


def transcode(
    statistics: sdt.Statistics, data_type: sdt.Type, protected_path: sdt.Path
) -> sdt.Transform:
    return Transform(
        sp.Transform(
            name='Transcoding for synthetic data',
            spec=sp.Transform.Spec(
                transcode=sp.Transform.Transcode(
                    statistics=statistics.protobuf(),
                    data_type=data_type.protobuf(),
                    protected_path=protected_path.protobuf(),
                )
            ),
            inversible=True,
            schema_preserving=False,
        )
    )


def inverse_transcode(transcode_transform: sdt.Transform) -> sdt.Transform:

    assert transcode_transform.protobuf().spec.HasField('transcode')
    return Transform(
        sp.Transform(
            name='Inverse Transcoding for synthetic data',
            spec=sp.Transform.Spec(
                inverse_transcode=sp.Transform.InverseTranscode(
                    transcode=transcode_transform.protobuf().spec.transcode
                )
            ),
            inversible=True,
            schema_preserving=False,
        )
    )


if t.TYPE_CHECKING:
    test_transform: sdt.Transform = Transform(sp.Transform())
