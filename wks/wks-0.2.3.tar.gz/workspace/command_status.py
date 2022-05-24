import os
import subprocess
from colorama import Fore, Back, Style
from workspace import env, git, message, cmake

name = "status"
help = """Shows status for projects"""
usage = ""
min_args = 0


def run(args):
    config = env.get_config(os.getcwd())

    group_not_sync = []
    group_untracked_file = []
    group_modified_file = []

    for directory in git.get_directories():
        parts = directory.split("/")
        vendor = parts[-2]
        if config is None or vendor in config["status"]:
            branch = git.branch(directory)
            message_header = "* In " + directory + " [" + message.emphasis(branch) + "]"

            status = git.status(directory).strip()
            if not status:
                message.bright(message_header)
                print(message.success("- Everything is ok"))
            else:
                lines = status.split("\n")
                has_modified = False
                for line in lines:
                    parts = line.strip().split(" ")
                    if parts[0] != "??":
                        has_modified = True
                        break

                if has_modified:
                    group_modified_file.append(message_header)
                else:
                    group_untracked_file.append(message_header)

            if git.is_ahead(directory):
                group_not_sync.append(message_header)

    for m in group_not_sync:
        message.bright(m)
        print(message.error("- Is not in sync with remote"))

    for m in group_modified_file:
        message.bright(m)
        print(message.warn("- Has modified files"))

    for m in group_untracked_file:
        message.bright(m)
        print(message.error("- Has untracked files"))

    print("")
