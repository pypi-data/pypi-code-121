import subprocess
from typing import List


def execute_command_and_print(command: List[str]) -> None:
    print("\n".join(execute_command(command)))


def execute_command(command: List[str]) -> List[str]:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    if process.stdin:
        process.stdin.write("uname -a\n")
        process.stdin.write("uptime\n")
        process.stdin.close()

    return [line.strip() for line in process.stdout] if process.stdout else []


__all__ = [
    "execute_command",
    "execute_command_and_print",
]
