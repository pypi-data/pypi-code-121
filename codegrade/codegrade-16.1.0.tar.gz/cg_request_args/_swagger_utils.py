"""This module contains utils for swagger generation.
"""
import typing as t
import contextlib

if t.TYPE_CHECKING:  # pragma: no cover
    # pylint: disable=unused-import
    from .open_api import OpenAPISchema
else:

    class OpenAPISchema:
        """Stub class for ``OpenAPISchema``
        """


_CUR_OPEN_API_SCHEMA: t.Optional[OpenAPISchema] = None


class Schema(BaseException):
    """Schema that should be raised when running an API function while
    generating swagger file.
    """
    def __init__(self, typ: str, schema: t.Mapping[str, t.Any]) -> None:
        super().__init__()
        self.schema = schema
        self.typ = typ


def maybe_raise_schema(
    make_schema: t.Callable[[OpenAPISchema], Schema]
) -> None:
    """Maybe raise a schema if swagger generation is enabled.

    :param make_schema: The function that will be called to generate the
        schema.
    """
    if _CUR_OPEN_API_SCHEMA is not None:
        raise make_schema(_CUR_OPEN_API_SCHEMA)


@contextlib.contextmanager
def as_schema_generator(
    open_api: OpenAPISchema
) -> t.Generator[None, None, None]:
    """Enable schema generation as a context manager.

    :param open_api: The schema collector currently used.
    """
    global _CUR_OPEN_API_SCHEMA  # pylint: disable=global-statement
    _CUR_OPEN_API_SCHEMA = open_api
    try:
        yield
    finally:
        _CUR_OPEN_API_SCHEMA = None
