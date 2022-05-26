import os.path
import re

from pkg_resources import Requirement

MANAGED_MESSAGE = """
# ServicefoundryManaged
# Below this line dependencies was added by servicefoundry.
""".splitlines()


class SfPackage:
    def __init__(self, package_name, package_version, is_installed=False):
        self.package_name = package_name
        self.package_version = package_version
        self.is_installed = is_installed

    def update_version(self, version):
        self.is_installed = True
        self.package_version = version

    def to_str(self):
        if self.package_version:
            return f"{self.package_name}=={self.package_version}"
        else:
            return f"{self.package_name}"


class PythonRequirements:
    def __init__(self, old_requirements_txt: str):
        self.old_user_lines = []
        self.old_packages = set()
        self.final_packages = {}
        source_lines = old_requirements_txt.splitlines()
        self._load(source_lines)

    def _load(self, source_lines):
        is_managed_block = False
        for line in source_lines:
            if re.match("^\s*#\s*ServicefoundryManaged\s*$", line):
                is_managed_block = True
            if not is_managed_block:
                self.old_user_lines.append(line)
            sline = line.strip()
            if sline.strip() != "" and re.match("^\s*#", line) is None:
                requirement = Requirement(line)
                package_name = requirement.key.lower()
                if not is_managed_block:
                    self.old_packages.add(package_name)
                else:
                    try:
                        version = requirement.specs[0][1]
                    except IndexError:
                        version = None
                    self.final_packages[package_name] = SfPackage(package_name, version)

    def update_requirements_txt(self, new_dependencies: dict):
        for package_name, package_version in new_dependencies.items():
            # To prevent servicefoundry==0.0.0 lines
            if package_version != "0.0.0":
                if package_name not in self.old_packages:
                    if package_name in self.final_packages:
                        self.final_packages[package_name].update_version(
                            package_version
                        )
                    else:
                        self.final_packages[package_name] = SfPackage(
                            package_name, package_version, is_installed=True
                        )

    def get_requirements_txt(self):
        # Generate lines.
        ret_lines = []
        for line in self.old_user_lines:
            ret_lines.append(line)
        ret_lines.extend(MANAGED_MESSAGE)
        for package_name, package in sorted(self.final_packages.items()):
            ret_lines.append(package.to_str())
        return os.linesep.join(ret_lines)
