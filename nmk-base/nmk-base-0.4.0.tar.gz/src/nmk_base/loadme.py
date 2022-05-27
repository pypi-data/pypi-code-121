from typing import Dict, List

from nmk_base.common import TemplateBuilder


class BuildLoadMe(TemplateBuilder):
    def prepare_deps(self, deps: Dict[str, Dict[str, str]], source: str) -> Dict[str, str]:
        return {
            name: " ".join(sources[source]) if isinstance(sources[source], list) else sources[source]
            for name, sources in filter(lambda t: source in t[1], deps.items())
        }

    def build(self, deps: Dict[str, Dict[str, str]], venv_pythons: List[str]):
        # Prepare sysdeps list per keys
        apt_deps = self.prepare_deps(deps, "apt")
        url_deps = self.prepare_deps(deps, "url")
        kwargs = {
            "aptDeps": apt_deps,
            "urlDeps": url_deps,
        }

        # Iterate on combination of templates, outputs and venv command
        for template, output, venv_python in zip(self.inputs, self.outputs, venv_pythons):
            specific_kwargs = {"pythonForVenv": venv_python}
            specific_kwargs.update(kwargs)
            self.build_from_template(template, output, specific_kwargs)
