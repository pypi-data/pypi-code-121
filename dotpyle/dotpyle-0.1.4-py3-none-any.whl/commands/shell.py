import click
from dotpyle.utils.path import get_default_path
from os import getenv, environ, read, write, setsid
import sys
import select
import termios
import tty
import pty
from subprocess import Popen
from dotpyle.decorators.pass_logger import pass_logger
from dotpyle.services.logger import Logger


@click.command()
@pass_logger
def shell(logger: Logger):
    """Open shell inside Dotpyle repository"""
    path = get_default_path()
    shell = getenv("SHELL", "/bin/sh")
    prompt = "(Dotpyle) repo [{}] > ".format(path)
    new_env = environ
    new_env["PS1"] = prompt

    logger.alert(
        "Opening shell session on Dotpyle git repo, make sure you understand"
        "what you are doing.\nType exit or <c-d> to return"
    )

    # https://www.it-swarm-es.com/es/python/ejecute-bash-interactivo-con-popen-y-un-tty-dedicado-python/828745020/
    # save original tty setting then set it to raw mode
    old_tty = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())

    # open pseudo-terminal to interact with subprocess
    master_fd, slave_fd = pty.openpty()

    # use os.setsid() make it run in a new process group, or bash job control will not be enabled
    p = Popen(
        ["bash", "--norc", "--noprofile"],
        # shell,          # TODO conflicts with oh-my-zsh
        env=new_env,
        preexec_fn=setsid,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        universal_newlines=True,
        cwd=path,
    )

    while p.poll() is None:
        r, _, _ = select.select([sys.stdin, master_fd], [], [])
        if sys.stdin in r:
            d = read(sys.stdin.fileno(), 10240)
            write(master_fd, d)
        elif master_fd in r:
            o = read(master_fd, 10240)
            if o:
                write(sys.stdout.fileno(), o)

    # restore tty settings back
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

    logger.success("Shell session end")
