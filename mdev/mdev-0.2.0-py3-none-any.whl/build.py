# Author: Snow Yang
# Date  : 2022/03/21

import subprocess
import shutil
import click
from pathlib import Path

from mdev.env import get_env, get_cmake, get_ninja
from mdev import log

from rich import print
from rich.panel import Panel

mxos_logo = '''
███╗   ███╗██╗  ██╗ ██████╗ ███████╗
████╗ ████║╚██╗██╔╝██╔═══██╗██╔════╝
██╔████╔██║ ╚███╔╝ ██║   ██║███████╗
██║╚██╔╝██║ ██╔██╗ ██║   ██║╚════██║
██║ ╚═╝ ██║██╔╝ ██╗╚██████╔╝███████║
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
'''

failed = '''
███████╗ █████╗ ██╗██╗     ███████╗██████╗ 
██╔════╝██╔══██╗██║██║     ██╔════╝██╔══██╗
█████╗  ███████║██║██║     █████╗  ██║  ██║
██╔══╝  ██╔══██║██║██║     ██╔══╝  ██║  ██║
██║     ██║  ██║██║███████╗███████╗██████╔╝
╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ 
'''

success = '''
███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗
██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝
███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗
╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║
███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║
╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝
'''

@click.command()
@click.argument("project", type=click.Path())
@click.argument("module")
@click.option(
    "--flash",
    "-f",
    type=click.Choice(["APP", "ALL", "None"], case_sensitive=False),
    help="Download firmware to flash after built.",
)
@click.option(
    "--clean",
    "-c",
    is_flag=True,
    help="Rebuild the project.",
)
@click.option(
    "--kconfig",
    "-k",
    is_flag=True,
    help="Open config menu",
)
def build(project: str, module: str, flash: str, clean: bool, kconfig: str) -> None:
    """
    Build a MXOS project.

    Arguments:

        PROJECT : Path to the MXOS project

        MODULE  : Module name

    Example:

        $ mdev build demos/helloworld emc3080
    """

    env_path = get_env()
    project = str(Path(project)).replace('\\', '/')
    build_diretory = f'build/{project}-{module}'

    print(Panel.fit(f"[cyan]{mxos_logo}", title="Thanks for using MXOS!", style='cyan'))

    if clean:
        log.dbg(f'Removing {build_diretory} ...')
        shutil.rmtree(build_diretory, ignore_errors=True)

    print(Panel(f"[magenta]Configuring ...", style='magenta'))
    command = f'{get_cmake()} -B {build_diretory} -GNinja -DAPP={project} -DMODULE={module} -DFLASH={flash} -DMXOS_ENV={env_path} -DCMAKE_MAKE_PROGRAM={get_ninja()}'
    log.dbg(command)
    ret = subprocess.run(command, shell=True)
    if ret.returncode != 0:
        exit(ret.returncode)

    print(Panel(f"[green]Building ...", style='green'))
    command = f'{get_cmake()} --build {build_diretory}'
    if kconfig:
        command += f' --target guiconfig'
    log.dbg(command)
    ret = subprocess.run(command, shell=True)
    if ret.returncode != 0:
        print(Panel.fit(f"[red]{failed}", title="Sorry ...", style='red'))
        exit(ret.returncode)
    print(Panel.fit(f"[green]{success}", title="Congratulation!", style='green'))
    
