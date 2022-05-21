from pkm.api.pkm import pkm
from pkm_cli.display.display import Display
from pkm_cli.reports.report import Report


class InstalledRepositoriesReport(Report):

    def display(self, dumb: bool = Display.is_dumb()):
        line_sep = "-" * 80
        Display.print(line_sep)
        Display.print("Builtin Repositories")
        Display.print(line_sep)

        for repo_type_info in pkm.repository_loader.available_repository_types():
            if repo_type_info.is_builtin():
                Display.print(f" - {repo_type_info.builder.repo_type}")

        Display.print(line_sep)
        Display.print("User-Installed Repositories")
        Display.print(line_sep)

        found = False
        for repo_type_info in pkm.repository_loader.available_repository_types():
            if not repo_type_info.is_builtin():
                found = True
                p = repo_type_info.provider
                Display.print(f" - {repo_type_info.builder.repo_type} comes from {p.containing_package.name}::{p.name}")

        if not found:
            Display.print("None")

        Display.print(line_sep)
