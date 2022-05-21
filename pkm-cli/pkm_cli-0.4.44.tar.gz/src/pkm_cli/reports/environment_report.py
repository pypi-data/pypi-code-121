from dataclasses import dataclass, field
from typing import Dict, List

from pkm.api.dependencies.dependency import Dependency
from pkm.api.environments.environment import Environment
from pkm.api.packages.site_packages import InstalledPackage, SitePackages
from pkm_cli.display.display import Display
from pkm_cli.reports.report import Report


class EnvironmentReport(Report):

    def __init__(self, env: Environment):
        self._env = env

    def display(self, dumb: bool = Display.is_dumb()):
        env = self._env

        line = "-" * 80
        Display.print(line)

        Display.print("Environment Basic Info")
        Display.print(line)
        Display.print(f"Path: {env.path}")
        Display.print(f"Interpreter Version: {env.interpreter_version}")
        Display.print(line)

        Display.print("Installed Packages")
        Display.print(line)

        package_info: Dict[str, _PackageInfo] = {
            SitePackages.normalize_package_name(package.name): _PackageInfo(package)
            for package in env.site_packages.installed_packages()
        }

        for p in package_info.values():
            dependencies = p.package.dependencies(env)
            for d in dependencies:
                norm_package_name = SitePackages.normalize_package_name(d.package_name)
                if q := package_info.get(norm_package_name):
                    q.required_by.append(p.package)
                else:
                    p.missing_dependencies.append(d)

        for p in package_info.values():
            p.display()


@dataclass
class _PackageInfo:
    package: InstalledPackage
    required_by: List[InstalledPackage] = field(default_factory=list)
    missing_dependencies: List[Dependency] = field(default_factory=list)

    def display(self):
        dsp = f"- {self.package.name} {self.package.version}, "
        if ur := self.package.user_request:
            dsp += f"required by the user ({ur})"
        else:
            dsp += f"required by: " + ', '.join(str(r.name) for r in self.required_by)

        Display.print(dsp)
        if self.missing_dependencies:
            Display.print("* WARNING: this package has missing dependencies: ")
            for md in self.missing_dependencies:
                Display.print(f"  - {md}")
