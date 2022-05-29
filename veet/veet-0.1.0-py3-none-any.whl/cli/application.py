import typer
import sys
from importlib import import_module

from .. import __version__, config
from ..core import paths


class Application:

    app: typer.Typer

    @classmethod
    def bootstrap(self):
        self.app = typer.Typer(
            help=f"Veet {typer.style(__version__, fg=typer.colors.GREEN)}")

        sys.path.append(paths.PROJECT_PATH)

        self.dynamic_commands(["OsEnv", "FrameworkNew", "Install"], "veet.commands")

        if config.get("framework"):
            self.dynamic_commands(["Serve"], "veet.framework.commands")

        self.dynamic_commands(paths.COMMANDS_PATH, "commands")
        self.dynamic_commands(paths.COMMANDS_PATH_APP, "app.commands")

        return self

    def dynamic_commands(path: str | list, module_path: str):
        try:
            for module in (paths.list_dir(path) if isinstance(path, str) else path):
                try:
                    import_module(f"{module_path}.{module}")
                except Exception:
                    pass
        except Exception:
            pass