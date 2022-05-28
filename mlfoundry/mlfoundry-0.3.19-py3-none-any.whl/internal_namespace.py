import os
import typing

from mlfoundry.exceptions import MlFoundryException


class _InternalNamespace:
    NAMESPACE = "mlf"
    DELIMETER = "."
    NAMESPACE_VIOLATION_MESSAGE = """
        {name} cannot start with {prefix}
    """

    def __call__(self, name: str, delimeter: str = DELIMETER):
        if not name:
            raise MlFoundryException("name should be a non empty string")
        return _InternalNamespace.NAMESPACE + delimeter + name

    def __truediv__(self, path: str):
        return os.path.join(_InternalNamespace.NAMESPACE, path)

    @staticmethod
    def _validate_name_not_using_namespace(name: typing.Optional[str], delimeter: str):
        if name and name.startswith(_InternalNamespace.NAMESPACE + delimeter):
            raise MlFoundryException(
                _InternalNamespace.NAMESPACE_VIOLATION_MESSAGE.format(
                    name=name, prefix=_InternalNamespace.NAMESPACE + delimeter
                )
            )

    def validate_namespace_not_used(
        self,
        names: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
        delimeter: str = DELIMETER,
        path: typing.Optional[str] = None,
    ):
        if isinstance(names, str):
            names = [names]
        if names is not None:
            for name_ in names:
                self._validate_name_not_using_namespace(name_, delimeter)
        if path:
            prefix = os.path.normpath(os.path.join(_InternalNamespace.NAMESPACE, ""))
            if os.path.normpath(path).startswith(prefix):
                raise MlFoundryException(
                    _InternalNamespace.NAMESPACE_VIOLATION_MESSAGE.format(
                        name=path, prefix=prefix
                    )
                )


NAMESPACE = _InternalNamespace()
