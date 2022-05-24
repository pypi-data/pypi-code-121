from typing import Callable, Any, List


class LazyDescriptor:
    """
    Descriptor which instantiates another descriptor only when it is
    first accessed.
    """
    def __init__(self, descriptor_constructor: Callable[[], Any]):
        # The function that will create the descriptor when needed
        self._descriptor_constructor: Callable[[], Any] = descriptor_constructor

        # Any time we might have been attached to something
        self._names: List[str] = []
        self._owners: List = []

    def __get__(self, instance, owner):
        # Resolve and defer
        return self._resolve().__get__(instance, owner)

    def __set__(self, instance, value):
        # Resolve and defer
        self._resolve().__set__(instance, value)

    def __delete__(self, instance):
        # Resolve and defer
        self._resolve().__delete__(instance)

    def __set_name__(self, owner, name):
        # Save the arguments for actual construction time
        self._names.append(name)
        self._owners.append(owner)

    def _resolve(self):
        # Create the actual descriptor
        descriptor = self._descriptor_constructor()

        # If we're attached to anything, replace ourselves with the new descriptor
        for name, owner in zip(self._names, self._owners):
            if getattr(owner, name, None) is self:
                setattr(owner, name, descriptor)

        return descriptor
