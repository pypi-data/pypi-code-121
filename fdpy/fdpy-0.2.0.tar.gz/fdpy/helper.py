import os
import shutil
from pathlib import Path


def check_path():
    config_file = f'{Path.home()}/.fdpyrc'
    if not Path(config_file).exists():
        PATH = []
        for file in [
                '.bashrc', '.zshrc', '.bash_profile', '.profile', '.zshenv'
        ]:
            if Path(f'{Path.home()}/{file}').exists():
                with open(f'{Path.home()}/{file}') as f:
                    path = [
                        x.strip() for x in f.readlines()
                        if x.startswith('export PATH=')
                    ]
                    if path:
                        PATH.append(':'.join(path).replace('export PATH=', ''))
        os.environ['PATH'] = os.environ['PATH'] + ':' + ':'.join(PATH)
        if not shutil.which('fd'):
            print(
                'ERROR: Could not retrieve the path to `fd` from your shell!')
            ans = input('Enter the path to `fd` manually: ')
            if Path(ans).exists():
                os.environ['PATH'] = os.environ['PATH'] + ':' + ans
            else:
                raise FileNotFoundError(ans)

        with open(config_file, 'w') as f:
            f.write(shutil.which('fd'))

    with open(config_file) as rc:
        fd = rc.read()
    return fd
