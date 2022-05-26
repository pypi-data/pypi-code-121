import os
from typing import Callable

from ..models.domains.cells import (
    ConfigCell, ServiceCell, MapperCell, ViewCell, EmitterCell, ErrorCell
)


class Build:
    """Proxy mapping class with collection of initial project instances to be builded by assembler.
    
    Should be inherited by build class in root folder."""
    def __init__(
        self,
        version: str = "",
        config_dir: str = "./src/configs",
        service_cells: list[ServiceCell] = [],
        mapper_cells: list[MapperCell] = [],
        view_cells: list[ViewCell] = [],
        emitter_cells: list[EmitterCell] = [],
        error_cells: list[ErrorCell] = [],
        shell_processors: list[Callable] = [],
        cli_cmds: list[Callable] = [],
        ctx_processor_func: Callable | None = None,
        each_request_func: Callable | None = None,
        first_request_func: Callable | None = None,
    ) -> None:
        # Use native root module path.
        # Because this class imported from root directory, root_path below will be assigned from there during class's
        # initialization.
        # NOTE: This path can be overrided by assembler in order of getting arguments on it's own initialization.
        self.root_path = os.getcwd()

        self.version = version
        self.config_dir = config_dir
        self.service_cells = service_cells
        self.mapper_cells = mapper_cells
        self.view_cells = view_cells
        self.emitter_cells = emitter_cells
        self.error_cells = error_cells
        self.shell_processors = shell_processors
        self.cli_cmds = cli_cmds
        self.ctx_processor_func = ctx_processor_func
        self.each_request_func = each_request_func
        self.first_request_func = first_request_func
