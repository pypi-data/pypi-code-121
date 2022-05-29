"""
This module installs npm packages
"""


from pydmt.utils.filesystem import unlink_files, mkdir_touch
from pydmt.utils.subprocess import check_call

from pydmt.api.one_source_one_target import OneSourceOneTarget


class Installer(OneSourceOneTarget):
    def build(self) -> None:
        unlink_files(self.target)
        args = [
            'npm',
            'install',
            '--quiet',
            '--silent',
        ]
        check_call(args)
        mkdir_touch(self.target)
