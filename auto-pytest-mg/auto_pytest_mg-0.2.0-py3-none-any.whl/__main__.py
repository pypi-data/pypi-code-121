# type: ignore[attr-defined]
from pathlib import Path

import typer
from rich.console import Console

from auto_pytest_mg import mg_file_gen, version

app = typer.Typer(
    name="auto_pytest_mg",
    help="Generate a pytest/pytest-mock-generator featured test file given a valid python file",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]auto_pytest_mg[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.command(name="")
def main(
    file_path: Path = typer.Argument(..., help="Python file path to generate test file."),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the auto_pytest_mg package.",
    ),
) -> None:
    mg_file_gen.write_mg_test_file(file_path)


if __name__ == "__main__":
    app()
