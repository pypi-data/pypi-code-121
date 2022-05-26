import os
import subprocess
import yaml
from pathlib import Path

from savitrigen.config import CodegenConfig

class Bootstrap():
    @staticmethod
    def clone_repo(config:CodegenConfig):
        cwd = Path('source')
        if not Path(cwd / Path('.gitignore')).exists():
            process = subprocess.Popen([
                'git',
                'clone',
                config.boilerplate_repo_url,
                str(cwd)
            ])

            stdout, stderr = process.communicate()

        os.chdir(str(cwd))
        return cwd

    @staticmethod
    def install():
        if Path(Path.cwd() / Path('node_modules')).exists():
            return

        os.system('npm install')
        os.system('cd node_modules/\@savitri/frontend && npm install')

