import argparse
import logging
import os
import subprocess
import sys

from .version import __version__, __codename__


RED = ""
GREEN = ""
CYAN = ""
END = ""

if sys.stdout.isatty():
    RED = '\033[31m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    END = '\033[0m'


def die(msg):
    sys.stdout.write(msg + "\n")
    sys.exit(1)


def run_verbose(action, cmd_list, badval=None):
    result = subprocess.run(cmd_list)
    action_out = (action + ":").ljust(6)
    success = False

    if badval:
        if result.returncode != badval:
            success = True
    elif result.returncode == 0:
        success = True
    if success:
        sys.stderr.write(GREEN + f"{' '.join(cmd_list)}" + END + "\n")
    else:
        sys.stderr.write(RED + "!!!" + END + f" {action_out}: {' '.join(cmd_list)}\n")
    return success


def parse_binds(bind_args, newroot):
    binds = {}
    invalid_dest = ["/sys", "/dev", "/proc"]
    for bindval in bind_args:
        bindval = bindval[0]
        colon = bindval.rfind(":")
        if colon == -1:
            die(f"Error: For --bind option, specify a colon separating both paths. ('--bind={bindval}')")
        src = bindval[:colon]
        src = src.rstrip("/")
        dest = bindval[colon + 1:]
        dest = dest.rstrip("/")
        if dest.startswith("/"):
            dest = dest.lstrip("/")
        if not os.path.isabs(src):
            die(f"Error: Source path '{src}' must be absolute. ('--bind={bindval}')")
        if not os.path.isabs("/"+dest):
            die(f"Error: Destination path '{dest}' does not appear valid. ('--bind={bindval}')")
        dest_abs = os.path.join(newroot, dest)
        if not os.path.exists(dest_abs):
            die(f"Error: Destination path '{dest}' does not appear to exist within the chroot. ('--bind={bindval}')")
        if not os.path.isdir(src):
            die(f"Error: Could not find source for bind '{src}'. Must exist and be a directory. ('--bind={bindval}')")
        if dest in invalid_dest:
            die(f"Error. Bind destination '{dest}' is already managed by fchroot automatically. ('--bind={bindval}')")
        binds[dest] = src
    return binds


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', action='version', version=f"fchroot {__version__} ({__codename__})")
    ap.add_argument("newroot", type=str)
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--preserve-env", action="store_true", default=False,
                    help="Preserve the current environment settings rather than wiping them by default.")
    ap.add_argument("--cpu", action="store", default=None, help="Specify specific CPU type for QEMU to use")
    ap.add_argument("--bind", action="append", nargs=1, default=[], help="Specify additional bind mounts in src:dest format")
    ap.add_argument("--nobind", action="store_true", default=False, help="Disable all bind mounts when entering fchroot")
    known, remainder = ap.parse_known_args()
    if known.nobind and len(known.bind):
        die(f"Error -- the --nobind and --bind arguments cannot be used at the same time.")
    binds = parse_binds(known.bind, known.newroot)
    return known, binds, remainder


args, local_binds, commands = parse_args()
logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)


def bind_mount(chroot_path, umount=False):
    global_binds = {
        "proc": "/proc",
        "sys": "/sys",
        "dev": "/dev"
    }

    for recurse, bind_groups in (True, global_binds), (False, local_binds):
        for dest, src in bind_groups.items():
            dest = dest.lstrip("/")
            dest_abs = os.path.join(chroot_path, dest)
            if umount:
                action = "umount"
                mount_cmd = ["/bin/umount", "-R", "--lazy", dest_abs]
                badval = 10
            else:
                action = "mount"
                if not os.path.isdir(dest_abs):
                    die(f"Required chroot directory '{dest_abs}' does not exist. Exiting.")
                if recurse:
                    bindopt = "--rbind"
                else:
                    bindopt = "--bind"
                mount_cmd = ["/bin/mount", bindopt, f"/{src}", dest_abs]
                badval = None
            if action == "mount" and os.path.ismount(dest_abs):
                sys.stderr.write(GREEN + f" {action}: /{dest} (already mounted)\n")
            else:
                run_verbose(action, mount_cmd, badval=badval)

