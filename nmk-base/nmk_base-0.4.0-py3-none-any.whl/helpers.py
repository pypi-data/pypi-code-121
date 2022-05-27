from typing import Dict

from nmk import __version__
from nmk.model.builder import NmkTaskBuilder
from rich.emoji import Emoji


class VersionBuilder(NmkTaskBuilder):
    def build(self, plugins: Dict[str, str]):
        # Displays all versions
        all_versions = {"nmk": __version__}
        all_versions.update(plugins)
        for name, version in all_versions.items():
            self.logger.info(self.task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {version}")


class HelpBuilder(NmkTaskBuilder):
    def build(self, links: Dict[str, str]):
        # Displays all online help links
        all_links = {"nmk": "https://github.com/dynod/nmk/wiki"}
        all_links.update(links)
        for name, link in all_links.items():
            self.logger.info(self.task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {link}")


class TaskListBuilder(NmkTaskBuilder):
    def build(self):
        # Iterate on all model tasks
        for name, task in ((k, self.model.tasks[k]) for k in sorted(self.model.tasks.keys())):
            self.logger.info(task.emoji, f" {Emoji('backhand_index_pointing_right')} {name}: {task.description}")
