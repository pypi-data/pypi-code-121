import subprocess
from pathlib import Path
from typing import Dict, List

from nmk.errors import NmkStopHereError
from nmk.model.builder import NmkTaskBuilder
from nmk.model.keys import NmkRootConfig
from nmk.model.resolver import NmkStrConfigResolver
from nmk.utils import run_with_logs

from nmk_base.common import TemplateBuilder


class GitVersionRefresh(NmkTaskBuilder):
    def build(self, version: str):
        # Check if update is needed
        self.logger.debug(f"New version: {version}")
        do_update = True
        stamp_file = self.main_output
        if stamp_file.is_file():
            with stamp_file.open() as f:
                persisted_version = f.read().splitlines(keepends=False)[0]
                self.logger.debug(f"Previously persisted version: {persisted_version}")
                do_update = version != persisted_version
        if do_update:
            # Yep, update persisted version
            self.logger.info(self.task.emoji, self.task.description)
            with stamp_file.open("w") as f:
                f.write(version)
        else:
            self.logger.debug("Persisted git version already up to date")


class GitClean(NmkTaskBuilder):
    def build(self):
        # Full clean, just warn before
        self.logger.warning("Clean all git ignored files; use loadme script to setup the project again")
        subprocess.run(["git", "clean", "-fdX"], cwd=self.model.config[NmkRootConfig.PROJECT_DIR].value, check=True)
        raise NmkStopHereError()


class GitVersionResolver(NmkStrConfigResolver):
    def get_value(self, name: str) -> str:
        # Get version from git
        cwd = self.model.config[NmkRootConfig.PROJECT_DIR].value
        cp = run_with_logs(["git", "describe", "--tags", "--dirty"], cwd=cwd, check=False)
        if cp.returncode == 0:
            # At least one tag
            return cp.stdout.splitlines(keepends=False)[0]
        else:
            # Probably no tags, build the version by hand
            # 1. get latest commit
            cp = run_with_logs(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, check=False)
            if cp.returncode != 0:
                # Definitely not a git repo; use a default version
                return "0.0.0"
            ref = cp.stdout.splitlines(keepends=False)[0]

            # 2. get revisions count
            rev_count = run_with_logs(["git", "rev-list", "--count", ref, "--"], cwd=cwd).stdout.splitlines(keepends=False)[0]
            # 3. get hash
            rev_hash = run_with_logs(["git", "describe", "--always", "--dirty"], cwd=cwd).stdout.splitlines(keepends=False)[0]

            # Build version from parts
            return f"0.0.0-{rev_count}-g{rev_hash}"


class GitFileFragmentUpdater(TemplateBuilder):
    def allow_missing_input(self, missing_input: Path) -> bool:
        # Allow project root .gitignore/.gitattributes to be missing
        return missing_input == self.main_input

    def build_fragment(self, kwargs: Dict[str, str], template: str):
        # Generate fragment (in stamp file)
        fragment = self.build_from_template(Path(template), self.outputs[1], kwargs)

        # Read (eventually manually modified) file
        fragment_lines = list(filter(len, fragment.splitlines(keepends=False)))
        if self.main_input.is_file():
            fragment_header = fragment_lines[0]
            fragment_footer = fragment_lines[-1]
            with self.main_input.open() as f:
                file_content = f.read().splitlines(keepends=False)

            # Delete fragment, if any
            if fragment_header in file_content:
                insert_pos = file_content.index(fragment_header)
                footer_pos = (file_content.index(fragment_footer) + 1) if fragment_footer in file_content else len(file_content)
                self.logger.debug(f"Merge {self.main_output.name} content by replacing fragment at lines {insert_pos+1}-{footer_pos}")
                del file_content[insert_pos:footer_pos]
            else:
                self.logger.debug(f"Insert generated fragment at and of existing {self.main_output.name} file")
                insert_pos = len(file_content)
        else:
            self.logger.debug(f"Create new {self.main_output.name} file")
            file_content = []
            insert_pos = 0

        # Insert fragment
        for p in range(len(fragment_lines)):
            file_content.insert(insert_pos + p, fragment_lines[p])

        # Write final content
        with self.main_output.open("w") as f:
            self.logger.debug(f"Update {self.main_output.name} file")
            f.write("\n".join(file_content + [""]))


class GitIgnore(GitFileFragmentUpdater):
    def prepare_ignored_file(self, ignored_file: str) -> str:
        p = Path(ignored_file)

        # Just prepare ignored absolute project-relative paths
        if p.is_absolute():
            try:
                # Assume path is relative to project
                return p.relative_to(self.model.config[NmkRootConfig.PROJECT_DIR].value).as_posix()
            except ValueError:
                self.logger.warning(f"Can't ignore non project-relative absolute path: {ignored_file}")
                return None

        return ignored_file

    def build(self, ignored_files: List[str], template: str):
        # Generate gitignore
        self.build_fragment({"gitIgnoredFiles": list(filter(lambda p: p is not None, map(self.prepare_ignored_file, ignored_files)))}, template)


class GitAttributes(GitFileFragmentUpdater):
    def build(self, template: str):
        # Generate gitattributes
        self.build_fragment({}, template)
