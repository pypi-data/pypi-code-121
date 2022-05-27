import sys,os,time
import feios_utils.funcs as utils

################################
def load_cmd(cmd : str):
    """Load a cmd."""
    if cmd[0] == "#":
        return
    elif cmd[:3] == "out":
        if cmd[3] == " ":
            utils.out(cmd[4:])
            return
        else:
            utils.outline("""Input error:               ERROR 001
            There should be a space.
            Execution halted.
            """)
            return
    elif cmd[:4] == "exit":
        if len(cmd) >= 5:
            exit(cmd[5:])
        else:
            exit()
    elif cmd == "":
        return
    else:
        utils.outline("""Input error:                   ERROR 002
        No such command.
        Execution halted.
        """)
        return
    return

while True:
    s = input(">>>")
    load_cmd(s)