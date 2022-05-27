from typing import Dict, List

from nmk_base.common import TemplateBuilder


class ActionFileBuilder(TemplateBuilder):
    def build(self, python_versions: List[str], commands: Dict[str, str]):
        # Create directory and build from template
        self.main_output.parent.mkdir(parents=True, exist_ok=True)
        self.build_from_template(self.main_input, self.main_output, {"pythonVersions": python_versions, "commands": commands})
