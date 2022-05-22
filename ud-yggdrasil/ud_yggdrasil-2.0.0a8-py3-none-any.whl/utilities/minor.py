import subprocess

from yggdrasil.utilities.logger import logger


def unique_match(ls):
    if len(ls) == 0:
        raise Exception("Problem: Unrecognised drivers type")
    if len(ls) > 1:
        raise Exception("Problem: Several apps match this type")
    return ls[0]


class CmdException(Exception):
    def __init__(self, error: str):
        self.message = 'Aborting, error in commands communicated:\n{0}'.format(error)
        super().__init__(self.message)


def run_cmds(cmds:[]):
    for cmd in cmds:
        logger.debug("running command: {0}".format(cmd))
        output = subprocess.run(cmd, shell=True, check=False, capture_output=True)
        logger.debug("command output: {0}".format(output.stdout.decode("utf-8")))
        logger.debug("return code: {0}".format(output.returncode))
        if output.returncode != 0:
            raise CmdException(output.stderr.decode("utf-8"))


def generate_custom_batch(source: str, destination: str, replacements: []):
    # Generate batch launcher
    with open(source) as f:
        batch = f.readlines()
    for i, row in enumerate(batch):
        for find, repl in replacements:
            row = row.replace(find, repl)
            batch[i] = row
    with open(destination, 'w+') as f:
        f.write("".join(batch))
