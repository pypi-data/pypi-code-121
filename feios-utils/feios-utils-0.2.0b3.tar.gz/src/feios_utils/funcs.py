# FEI OS useful utils

__all__ = ["out", "outline", "run", "runbatch","load_cmd"]


def out(txt: str):
    """Print function within line."""
    print(txt, end="")


def outline(txt: str):
    """Normal print function."""
    print(txt, end="\n")


def run(tl: list[str]):
    """Run a list of commands given."""
    for line in tl:
        if line.startswith("#"):
            continue
        elif line[:4] == "outl":
            if len(line) == 4:
                print("")
                continue
            else:
                if line[4] == " ":
                    print(line[5:])
                    continue
                else:
                    print("""Input and/or script error:\
                    ERROR 001
                    There should be a space.
                    Execution halted.
                    """)
                    return 2
        elif line[:3] == "out":
            if len(line) == 3:
                print("",end="")
                continue
            if line[3] != " ":
                print("""Input and/or script error:\
                ERROR 001
                There should be a space.
                Execution halted.
                """)
                return 2
            else:
                print(line[4:])
                continue
        elif line[:4] == "exit":
            return 0
        else:
            print("""Input and/or script error:\
            ERROR 002
            No such command
            Execution halted.
            """)
            return 2


def runbatch(pof):
    """Read a batch script and execute it."""
    f = open(pof, 'r')
    content = f.readlines()
    ret = run(content)
    return ret


def load_cmd(cmd : str):
    """Load a cmd."""
    if cmd[0] == "#":
        return
    elif cmd[:4] == "outl":
        if len(cmd) == 4:
            print("")
            return
        else:
            if cmd[4] == " ":
                print(cmd[5:])
            else:
                print("""Input error:               ERROR 001
            There should be a space.
            Execution halted.
            """)
            return
    elif cmd[:3] == "out":
        if len(cmd) == 3:
            print("")
            return
        if cmd[3] == " ":
            print(cmd[4:],end="")
        else:
            print("""Input error:               ERROR 001
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
        print("""Input error:                   ERROR 002
        No such command.
        Execution halted.
        """)
        return
    return