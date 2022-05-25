"""
This is a module that will install OS packages for you.
"""


from typing import List
import os

from pydmt.utils.filesystem import unlink_files, mkdir_touch
from pydmt.configs import ConfigSudo
from pydmt.utils.subprocess import check_call

from pydmt.api.one_source_one_target import OneSourceOneTarget


class BuilderApt(OneSourceOneTarget):
    def __init__(self, source: str, target: str, packages: List[str]):
        super().__init__(source, target)
        self.packages = packages

    def build(self) -> None:
        unlink_files(self.target)
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        args = []
        if ConfigSudo.sudo:
            args.append("sudo")
        # Here is how to keep apt-get quiet:
        # https://stackoverflow.com/questions/52642097/apt-get-with-quiet-option-is-still-noisy
        args.extend([
            'apt-get',
            '-q=2',
            '--yes',
            'install',
        ])
        args.extend(self.packages)
        check_call(args)
        mkdir_touch(self.target)
