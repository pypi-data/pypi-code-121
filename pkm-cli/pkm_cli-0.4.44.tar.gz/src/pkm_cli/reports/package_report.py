from typing import Optional, Any

from pkm.api.dependencies.dependency import Dependency
from pkm.api.environments.environment import Environment
from pkm.api.pkm import pkm
from pkm.api.projects.project import Project
from pkm.api.repositories.repository import Repository
from pkm_cli.display.display import Display
from pkm_cli.reports.report import Report
from rich.markdown import Markdown


class PackageReport(Report):
    def __init__(self, context: Optional[Any], dependency: str):
        self._context = context
        self._dependency = Dependency.parse(dependency)

    def display(self, dumb: bool = Display.is_dumb()):
        line = "-" * 80
        Display.print(line)

        repository: Repository = pkm.repositories.main
        env: Environment = Environment.current()

        if isinstance(self._context, Project):
            repository = self._context.attached_repository
            env = self._context.attached_environment
        elif isinstance(self._context, Environment):
            env = self._context

        match = repository.match(self._dependency, env)

        if not match:
            Display.print(f"No package matched for {self._dependency}")
        else:
            Display.print(f"Dependency: {self._dependency}")
            Display.print(line)
            if len(match) > 3:
                Display.print(
                    f"Matched Versions: {', '.join(str(p.version) for p in match[:3])} and {len(match) - 3} more.")
            else:
                Display.print(
                    f"Matched Versions: {', '.join(str(p.version) for p in match)}")

            context_env: Optional[Environment] = None
            if isinstance(self._context, Project):
                deps = self._context.config.project.all_dependencies
                req = [p.version_spec for p in deps if p.package_name == self._dependency.package_name]

                if req:
                    Display.print(f"Dependency In Current Project: {', '.join(str(r) for r in req)}")
                else:
                    Display.print(f"Dependency In Current Project: None")

                context_env = self._context.attached_environment

            if context_env or (isinstance(self._context, Environment) and (context_env := self._context)):
                installed = context_env.site_packages.installed_package(self._dependency.package_name)

                if installed:
                    Display.print(f"Installed In Current Environment: {installed.version}")
                else:
                    Display.print(f"Installed In Current Environment: None")

            Display.print(line)
            selected = match[0]
            Display.print(f"Metadata (from Version {selected.version})")
            Display.print(line)
            if metadata := selected.published_metadata:
                Display.print(f"Summary: {metadata.summary}")
                Display.print(f"Requires Python: {metadata.required_python_spec}")
                if not dumb:
                    desc = Markdown(metadata.description)
                else:
                    desc = ("\n" + metadata.description).replace("\n", "\n\t| ")

                Display.print(f"Description:")
                Display.print(desc)
            else:
                Display.print("No metadata for this package was provided by the supplying repository")
