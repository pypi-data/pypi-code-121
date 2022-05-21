from pkm.api.pkm import HasAttachedRepository
from pkm.utils.sequences import pop_or_none
from pkm.utils.sets import try_add
from pkm_cli.display.display import Display
from pkm_cli.reports.report import Report
import re


class AddedRepositoriesReport(Report):

    def __init__(self, with_repo: HasAttachedRepository):
        self._with_repo = with_repo

    def display(self, dumb: bool = Display.is_dumb()):
        line_sep = "-" * 80

        contexts = [self._with_repo]
        opened = set()
        while context := pop_or_none(contexts):
            if not try_add(opened, id(context)):
                continue
            contexts.extend(context.repository_management.parent_contexts())

            if defined_repositories := context.repository_management.defined_repositories():
                Display.print(line_sep)
                Display.print(f"[h1]{_context_name(context)} Context[/]")
                Display.print(line_sep)

                for added_repository in defined_repositories:
                    desc = f"{added_repository.name}: {added_repository.type}"
                    if added_repository.bind_only:
                        desc += " (bind only)"
                    Display.print(desc)

        Display.print(line_sep)


def _context_name(context: HasAttachedRepository) -> str:
    return re.sub('([A-Z])', r' \1', type(context).__name__).strip()
