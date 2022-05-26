from importlib.metadata import entry_points
from typing import Optional, TypeVar, Dict, Generic

BackendType = TypeVar('BackendType')


class BackendLoader(Generic[BackendType]):
    def __init__(self, ep_name: str, ep_function: str):
        self._load = False
        self._ep_name = ep_name
        self._ep_function = ep_function
        self._backends: Dict[str, BackendType] = dict()

    def load_backends(self):
        if self._load:
            return

        for bb in entry_points().get(self._ep_name, []):
            path = f'{self._ep_name}.backends.{bb.name}'

            # noinspection PyBroadException
            try:
                module = __import__(path, fromlist=f'{self._ep_name}.backends')
                if hasattr(module, self._ep_function):
                    backend = getattr(module, self._ep_function)()
                    self._backends[backend.name] = backend
                    self.on_load(backend)

            except Exception as e:
                continue

        self._load = True

    def get_backend(self, name: str) -> Optional[BackendType]:
        return self._backends.get(name)

    def on_load(self, backend: BackendType):
        pass
