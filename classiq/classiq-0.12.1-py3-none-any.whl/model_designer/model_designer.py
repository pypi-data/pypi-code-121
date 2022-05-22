"""ModelDesigner module, implementing facilities for designing models and generating circuits using Classiq platform."""
from __future__ import annotations

import distutils.spawn
import logging
import tempfile
from contextlib import nullcontext
from typing import IO, AnyStr, ContextManager, List, Optional, Type, Union

from classiq.interface.generator import function_call, result
from classiq.interface.generator.model import Constraints, Model, Preferences

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import AsyncifyABC
from classiq.exceptions import (
    ClassiqAPIError,
    ClassiqFileNotFoundError,
    ClassiqGenerationError,
)
from classiq.model_designer import function_handler, wire
from classiq.quantum_functions.function_library import FunctionLibrary

_logger = logging.getLogger(__name__)

_SupportedIO = Union[IO, str]

# TODO: Add docstrings for auto generated methods.


def _file_handler(fp: Optional[_SupportedIO], mode: str = "r") -> ContextManager[IO]:
    if fp is None:
        temp_file = tempfile.NamedTemporaryFile(mode, suffix=".qmod", delete=False)
        print(f'Using temporary file: "{temp_file.name}"')
        return temp_file

    if isinstance(fp, str):
        return open(fp, mode)

    return nullcontext(fp)


class ModelDesigner(function_handler.FunctionHandler, metaclass=AsyncifyABC):
    """Facility to generate circuits, based on the model."""

    def __init__(self, **kwargs) -> None:
        """Init self."""
        super().__init__()
        self._model = Model(**kwargs)

    @property
    def _output_wire_type(self) -> Type[wire.Wire]:
        return wire.Wire

    @property
    def _logic_flow(self) -> List[function_call.FunctionCall]:
        return self._model.logic_flow

    @property
    def constraints(self) -> Constraints:
        """Get the constraints aggregated in self.

        Returns:
            The constraints data.
        """
        return self._model.constraints

    @property
    def preferences(self) -> Preferences:
        """Get the preferences aggregated in self.

        Returns:
            The preferences data.
        """
        return self._model.preferences

    async def synthesize_async(self) -> result.GeneratedCircuit:
        """Async version of `generate`
        Generates a circuit, based on the aggregation of requirements in self.

        Returns:
            The results of the generation procedure.
        """
        try:
            generation_result = await ApiWrapper.call_generation_task(self._model)
        except ClassiqAPIError as exc:
            raise ClassiqGenerationError(f"Generation failed: {exc}") from exc

        if (
            generation_result.status != result.GenerationStatus.SUCCESS
            or not isinstance(generation_result.details, result.GeneratedCircuit)
        ):
            raise ClassiqGenerationError(
                f"Generation failed: {generation_result.details}"
            )

        return generation_result.details

    def include_library(self, library: FunctionLibrary) -> None:
        """Includes a user-defined custom function library.

        Args:
            library (FunctionLibrary): The custom function library.
        """
        super().include_library(library=library)
        self._model.function_library = library.data

    def dumps(self, ignore_warning: bool = False) -> str:
        """Serialize model to a JSON formatted `str`

        Args:
            ignore_warning (bool): Whether to ignore the warning print
        """
        if not ignore_warning:
            _logger.warning(
                "Saving to json is currently unstable since versions may change"
            )

        return self._model.json(exclude_defaults=True, indent=4)

    def dump(
        self, fp: Optional[_SupportedIO] = None, ignore_warning: bool = False
    ) -> None:
        """Serialize model to a JSON formatted stream to `fp` (a `.write()`)-supporting file-like object

        Args:
            fp (IO | str | None): a file-like object
                if None -> a temporaty file will be created
                if str -> this will be treated as the file path
            ignore_warning (bool): Whether to ignore the warning print
        """
        with _file_handler(fp, "w") as f:
            f.write(self.dumps(ignore_warning=ignore_warning))

    @classmethod
    def loads(cls, s: AnyStr) -> ModelDesigner:
        """Deserialize `s`, a JSON formatted `str`, to a ModelDesigner

        Args:
            s (str | bytes): A JSON-formatted `str` | `bytes`
        """
        new_instance = cls()
        new_instance._model = Model.parse_raw(s)
        return new_instance

    @classmethod
    def load(cls, fp: Optional[_SupportedIO]) -> ModelDesigner:
        """Deserialize `fp` (a `.read()`-supporting file-like object) containing a JSON formatted document to a ModelDesigner

        Args:
            fp (IO | str): a file-like object
                if str -> this will be treated as the file path
        """
        with _file_handler(fp, "r") as f:
            return cls.loads(f.read())

    def export_to_vscode(self, ignore_warning: bool = False) -> None:
        """Export the model to a file, and display in VisualStudioCode"""

        if not distutils.spawn.find_executable("code"):
            raise ClassiqFileNotFoundError(
                "Please install VSCode to path\nIn VSCode, press [Ctrl/Command]+Shift+p, and then type \"install 'code' command in PATH\""
            )

        fp = tempfile.NamedTemporaryFile("w", suffix=".qmod", delete=False)
        self.dump(fp, ignore_warning=ignore_warning)
        fp.close()
        distutils.spawn.spawn(["code", fp.name])
