import os
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

from whitenoise import WhiteNoise


class BaseStaticFilesEngine(ABC):
    """The base static files engine class.

    The static files engine is responsible for loading static files and rendering them.

    This class can be subclassed to implement a custom engine.
    """

    def __init__(
        self,
        app,
        root_dir: str = None,
        prefix: Optional[str] = "static/",
        **kwargs,
    ):
        if not root_dir or not os.path.isdir(root_dir):
            raise FileNotFoundError(f"{root_dir} is not a directory.")

        self._app = app
        self._root_dir = root_dir
        self._prefix = prefix
        self._kwargs = kwargs

    @abstractmethod
    def __call__(self, environ: Dict, start_response: Callable) -> Any:
        """The callable interface for the engine.

        It needs to be implemented by the subclass.
        """

    @abstractmethod
    def has_file(self, file_name: str) -> bool:
        """Check if the engine has a static file with the given name.

        Arguments:
            file_name (str): The name of the static file to check.

        Returns:
            bool: True if the engine has a static file with the given name,
                False otherwise.
        """


class WhiteNoiseEngine(BaseStaticFilesEngine):
    """The WhiteNoise static files engine class.

    The static files engine is responsible for loading static files and rendering them.
    This engine uses WhiteNoise library to load, and render static files.
    """

    _env: WhiteNoise = None

    def __init__(
        self,
        app,
        root_dir: str = None,
        prefix: Optional[str] = "static/",
        **kwargs,
    ):
        super().__init__(app, root_dir, prefix, **kwargs)

        self._env = WhiteNoise(
            self._app, root=self._root_dir, prefix=self._prefix, **self._kwargs
        )

    def __call__(self, environ: Dict, start_response: Callable) -> Any:
        """The callable interface for the engine."""
        return self._env(environ, start_response)

    def has_file(self, file_name: str) -> bool:
        """Check if the engine has a static file with the given name.

        Arguments:
            file_name (str): The name of the static file to check.

        Returns:
            bool: True if the engine has a static file with the given name,
                False otherwise.
        """
        return file_name in self._env.files


__all__ = ["BaseStaticFilesEngine", "WhiteNoiseEngine"]
