import subprocess

# def execute(process_name: str | list[str], check: bool = False):
def execute(command, check: bool = False):
    result = subprocess.run(
        # "%s" % command, capture_output=False, check=check, shell=True
        # command, capture_output=False, check=check, shell=True
        command,
        shell = True,
        capture_output=False,
        check=check,
    )
    return result.stdout


def create_command(process_name: str, arguments: tuple[str]) -> list[str]:
    command = list(arguments)
    command.insert(0, process_name)
    return command
