import json
from pathlib import Path
from typing import List

from nmk_base.common import TemplateBuilder


class SettingsBuilder(TemplateBuilder):
    def contribute(self, settings: dict, update: dict):
        for k, v in update.items():
            # Already exists in target model?
            if k in settings:
                # List: extend
                if isinstance(v, list):
                    settings[k].extend(v)
                # Map: update
                elif isinstance(v, dict):
                    settings[k].update(v)
                # Otherwise: replace
                else:
                    settings[k] = v
            else:
                # New key
                settings[k] = v

    def build(self, files: List[str], items: dict):
        # Iterate on files to merge them
        settings = {}
        for file_p in map(Path, files):
            self.logger.debug(f"Loading settings fragment: {file_p}")
            self.contribute(settings, json.loads(self.render_template(file_p, {})))

        # Post-process with raw provided items
        self.logger.debug(f"Update settings from config: {items}")
        self.contribute(settings, items)

        # Generate settings file
        with self.main_output.open("w") as f:
            json.dump(settings, f, indent=4)
