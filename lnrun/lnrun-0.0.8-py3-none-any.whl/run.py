import subprocess

import tempfile
import sys

from lnrun.send_message import send_message
from lnrun.config import get_config, is_script_path_setted


def main(_: bool = False):
    if not is_script_path_setted():
        print('script path is not setted, run "lnrun set_config script_path https://your.path.here" to set your path')
        exit()

    cmds = sys.argv[1:]
    if cmds[0] == 'run':
        cmds = cmds[1:]

    send_errors = get_config('send_errors')

    if send_errors:
        file = tempfile.NamedTemporaryFile()
        process = subprocess.run(cmds, stderr=file)
    else:
        process = subprocess.run(cmds)
    return_code = process.returncode
    # popen = subprocess.Popen(cmds, stderr=file)
    # return_code = popen.wait()

    message = f'lnrun done running : {cmds}'
    if send_errors:
        if return_code:
            file.seek(0)
            lines = file.readlines()
            try:
                lines = [line.decode(errors='replace') for line in lines]
                lines = ''.join(lines)
            except Exception:
                pass
            file.close()
            message += f'\nwith error:\n{lines}'
        else:
            message += ' without errors'
    else:
        message += ' with error.' if return_code else ' without error.'
    print(message)
    send_message(message)


if __name__ == '__main__':
    main()
