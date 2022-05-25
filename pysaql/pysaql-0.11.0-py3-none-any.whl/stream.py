"""Contains stream expressions and statements"""

from __future__ import annotations

from abc import ABC
import functools
import operator
from typing import List, Optional, Sequence, Tuple, Union

from .enums import FillDateTypeString, JoinType, Order
from .scalar import BinaryOperation, field, Scalar
from .util import flatten, stringify, stringify_list

__ALL__ = ["load", "cogroup"]


class StreamStatement(ABC):
    """Base class for a stream SAQL statement

    Each SAQL statement has an input stream, an operation, and an output stream.
    """

    stream: "Stream"

    def get_streams(self) -> list[Stream]:
        """Get a flat list of streams nested within this stream statement

        Returns:
            list of streams

        """
        return []


class Stream:
    """Base class for a SAQL data stream"""

    _id: int
    _statements: List[StreamStatement]

    def __init__(self) -> None:
        """Initializer"""
        super().__init__()
        self._id = 0
        self._statements: List[StreamStatement] = []

    def __str__(self) -> str:
        """Cast the stream to a string"""
        return "\n".join(str(op) for op in self._statements)

    @property
    def ref(self) -> str:
        """Stream reference in the SAQL query"""
        return f"q{self._id}"

    def get_streams(self) -> list[Stream]:
        """Get a flat list of streams nested within this stream

        Returns:
            list of streams

        """
        return flatten([s.get_streams() for s in self._statements])

    def add_statement(self, statement: StreamStatement) -> None:
        """Add a statement to the stream

        Args:
            statement: Stream statement

        """
        self._statements.append(statement)
        # Update all stream IDs
        for i, s in enumerate(flatten(statement.get_streams())):
            s._id = i

    def field(self, name: str) -> field:
        """Create a new field object scoped to this stream

        Args:
            name: Name of the field

        Returns:
            field object

        """
        return field(name, stream=self)

    def foreach(self, *fields: Scalar) -> Stream:
        """Applies a set of expressions to every row in a dataset.

        This action is often referred to as projection

        Args:
            fields: One or more fields to project

        Returns:
            self

        """
        self._statements.append(ProjectionStatement(self, fields))
        return self

    def group(self, *fields: Scalar) -> Stream:
        """Organizes the rows returned from a query into groups

        Within each group, you can apply an aggregate function, such as count() or sum()
        to get the number of items or sum, respectively.

        Args:
            fields: One or more fields to group by. If no fields are provided,
                "group by all" is assumed.

        Returns:
            self

        """
        self._statements.append(GroupStatement(self, fields))
        return self

    def filter(self, *filters: BinaryOperation) -> Stream:
        """Selects rows from a dataset based on a filter predicate

        Args:
            filters: One or more filters. If multiple filter arguments are provided,
                they will be combined using `and`.

        Returns:
            self

        """
        self._statements.append(FilterStatement(self, filters))
        return self

    def order(self, *fields: Union[Scalar, Tuple[Scalar, Order]]) -> Stream:
        """Sorts in ascending or descending order on one or more fields.

        Args:
            fields: One or more fields to sort by

        Returns:
            self

        """
        self._statements.append(OrderStatement(self, fields))
        return self

    def limit(self, limit: int) -> Stream:
        """Limits the number of rows returned.

        Args:
            limit: Maximum number of rows to return. Max 10,000

        Returns:
            self

        """
        self._statements.append(LimitStatement(self, limit))
        return self

    def fill(
        self,
        date_cols: Sequence[Scalar],
        date_type_string: FillDateTypeString,
        partition: Optional[Scalar] = None,
    ) -> Stream:
        """Fills missing date values by adding rows in data stream

        Args:
            date_cols: Date fields to check
            date_type_string: Date column type string for formatting dates that get
                injected into the stream
            partition: Optional dimension field used to partition the data stream.
                Defaults to None.

        Returns:
            self

        """
        self._statements.append(
            FillStatement(self, date_cols, date_type_string, partition=partition)
        )
        return self


class LoadStatement(StreamStatement):
    """Statement to load a dataset"""

    def __init__(self, stream: Stream, name: str) -> None:
        """Initializer

        Args:
            stream: Stream containing this statement
            name: Name of the dataset to load

        """
        super().__init__()
        self.stream = stream
        self.name = name

    def __str__(self) -> str:
        """Cast this load statement to a string"""
        return f'{self.stream.ref} = load "{self.name}";'

    def get_streams(self) -> list[Stream]:
        """Get a flat list of streams nested within this stream statement

        Returns:
            list of streams

        """
        return [self.stream]


class ProjectionStatement(StreamStatement):
    """Statement to project columns from a stream"""

    def __init__(self, stream: Stream, fields: Sequence[Scalar]) -> None:
        """Initializer

        Args:
            stream: Stream containing this statement
            fields: One or more fields to project

        """
        super().__init__()
        self.stream = stream
        if not fields:
            raise ValueError("At least one field is required")
        self.fields = fields

    def __str__(self) -> str:
        """Cast this projection statement to a string"""
        fields = ", ".join(str(f) for f in self.fields)
        return f"{self.stream.ref} = foreach {self.stream.ref} generate {fields};"


class OrderStatement(StreamStatement):
    """Statement to order rows in a stream"""

    def __init__(
        self,
        stream: Stream,
        fields: Sequence[Union[Scalar, Tuple[Scalar, Order]]],
    ) -> None:
        """Initializer

        Args:
            stream: Stream containing this statement
            fields: One or more fields to order by

        """
        super().__init__()
        self.stream = stream
        if not fields:
            raise ValueError("At least one field is required")
        self.fields = fields

    def __str__(self) -> str:
        """Cast this order statement to a string"""
        fields = []
        for f in self.fields:
            if isinstance(f, Scalar):
                fields.append(f"{f} asc")
            else:
                fields.append(f"{f[0]} {f[1]}")

        return (
            f"{self.stream.ref} = order {self.stream.ref} by {stringify_list(fields)};"
        )


class LimitStatement(StreamStatement):
    """Statement to limit the number of rows returned from a stream"""

    def __init__(self, stream: Stream, limit: int):
        """Initializer

        Args:
            stream: Stream containing this statement
            limit: Maximum number of rows to return. Max 10,000

        """
        super().__init__()
        self.stream = stream
        if limit <= 0 or limit > 10_000:
            raise ValueError(
                f"Limit must be a number between 1 and 10,000. Provided: {limit}"
            )
        self.limit = limit

    def __str__(self) -> str:
        """Cast this limit statement to a string"""
        return f"{self.stream.ref} = limit {self.stream.ref} {self.limit};"


class GroupStatement(StreamStatement):
    """Statement to group rows in a stream"""

    def __init__(self, stream: Stream, fields: Sequence[Scalar]):
        """Initializer

        Args:
            stream: Stream containing this statement
            fields: One or more fields to group by. If no fields are provided,
                "group by all" is assumed.

        """
        super().__init__()
        self.stream = stream
        self.fields = fields

    def __str__(self) -> str:
        """Cast this group statement to a string"""
        fields = stringify_list(self.fields) if self.fields else "all"
        return f"{self.stream.ref} = group {self.stream.ref} by {fields};"


class FilterStatement(StreamStatement):
    """Statement to filter rows in a stream"""

    def __init__(self, stream: Stream, filters: Sequence[BinaryOperation]) -> None:
        """Initializer

        Args:
            stream: Stream containing this statement
            filters: One or more operations to filter rows in a stream

        """
        super().__init__()
        self.stream = stream
        if not filters:
            raise ValueError("At least one filter is required")
        self.filters = filters

    def __str__(self) -> str:
        """Cast this filter statement to a string"""
        expr = functools.reduce(
            lambda left, right: BinaryOperation(operator.and_, left, right),
            self.filters,
        )
        return f"{self.stream.ref} = filter {self.stream.ref} by {expr};"


class CogroupStatement(StreamStatement):
    """Statement to combine (join) two or more streams into one"""

    def __init__(
        self,
        stream: Stream,
        streams: Sequence[Tuple[Stream, Union[Scalar, Sequence[Scalar], str]]],
        join_type: JoinType = JoinType.inner,
    ) -> None:
        """Initializer

        Args:
            stream: Stream containing this statement
            streams: List of tuples that each define the stream to combine and the
                common field(s) that will be used to combine results. If there are no
                specific fields to group by, pass "all" as the second item in the stream
                tuple.
            join_type: Type of join that determines how records are included in the
                combined stream

        """
        super().__init__()
        self.stream = stream
        if not streams:
            raise ValueError("At least one stream is required")
        self.streams = streams
        self.join_type = join_type

    def __str__(self) -> str:
        """Cast this cogroup statement to a string"""
        lines = []
        streams = []
        for i, item in enumerate(self.streams):
            stream, field_ = item
            if isinstance(field_, Scalar):
                groups = stringify(field_)
            elif field_ == "all":
                groups = "all"
            elif isinstance(field_, Sequence):
                groups = stringify_list(field_)
            else:
                raise ValueError(
                    f"Cogroup field type not supported. Provided: {field_}"
                )

            s = f"{stream.ref} by {groups}"
            if i == 0 and self.join_type != JoinType.inner:
                s += f" {self.join_type}"

            streams.append(s)
            lines.append(str(stream))

        lines.append(f"{self.stream.ref} = cogroup {', '.join(streams)};")

        return "\n".join(lines)

    def get_streams(self) -> list[Stream]:
        """Get a flat list of streams nested within this stream statement

        Returns:
            list of streams

        """
        return flatten(
            [
                [stream.get_streams() for (stream, _) in self.streams],
                [self.stream],
            ]
        )


class UnionStatement(StreamStatement):
    """Statement to combine (union) two or more streams with the same structure into one"""

    def __init__(
        self,
        stream: Stream,
        streams: Sequence[Stream],
    ) -> None:
        """Initializer

        Args:
            stream: Stream containing this statement
            streams: Streams that will be combined

        """
        super().__init__()
        self.stream = stream
        if not streams or len(streams) < 2:
            raise ValueError("At least two streams are required")
        self.streams = streams

    def __str__(self) -> str:
        """Cast this union statement to a string"""
        lines = []
        stream_refs = []

        for stream in self.streams:
            lines.append(str(stream))
            stream_refs.append(stream.ref)

        lines.append(f"{self.stream.ref} = union {', '.join(stream_refs)};")
        return "\n".join(lines)

    def get_streams(self) -> list[Stream]:
        """Get a flat list of streams nested within this stream statement

        Returns:
            list of streams

        """
        return flatten([[s.get_streams() for s in self.streams], [self.stream]])


class FillStatement(StreamStatement):
    """Statement to fill a data stream with missing dates"""

    def __init__(
        self,
        stream: Stream,
        date_cols: Sequence[Scalar],
        date_type_string: FillDateTypeString,
        partition: Optional[Scalar] = None,
    ) -> None:
        """Initializer

        Args:
            stream: Stream containing this statement
            date_cols: Date fields to check
            date_type_string: Date column type string for formatting dates that get
                injected into the stream
            partition: Optional dimension field used to partition the data stream.
                Defaults to None.

        """
        super().__init__()
        self.stream = stream
        self.date_cols = date_cols
        self.date_type_string = date_type_string
        self.partition = partition

    def __str__(self) -> str:
        """Cast this fill statement to a string"""
        args = [
            f"dateCols=({', '.join(str(c) for c in self.date_cols)}, {stringify(str(self.date_type_string))})"
        ]
        if self.partition:
            args.append(f"partition={stringify(self.partition)}")

        return f"{self.stream.ref} = fill {self.stream.ref} by ({', '.join(args)});"


def load(name: str) -> Stream:
    """Load a dataset

    Args:
        name: Name of the dataset to load

    Returns:
        new stream

    """
    stream = Stream()
    stream.add_statement(LoadStatement(stream, name))
    return stream


def cogroup(
    *streams: Tuple[Stream, Union[Scalar, Sequence[Scalar], str]],
    join_type: JoinType = JoinType.inner,
) -> Stream:
    """Combine data from two or more data streams into a single data stream

    Args:
        streams: Each item is a tuple of the stream to combine and the common field(s)
            that will be used to combine results. If there are no specific fields to
            group by, pass "all" as the second item in the stream tuple.
        join_type: Type of join that determines how records are included in the
            combined stream. Defaults to JoinType.inner.

    """
    stream = Stream()
    stream.add_statement(CogroupStatement(stream, streams, join_type))
    return stream


def union(*streams: Stream) -> Stream:
    """Union data from two or more data streams into a single data stream

    Each stream should have the same field names and structure. The streams do
    not need to be from the same dataset.

    Args:
        streams: Streams that will be unioned together

    Returns:
        a new stream

    """
    stream = Stream()
    stream.add_statement(UnionStatement(stream, streams))
    return stream
