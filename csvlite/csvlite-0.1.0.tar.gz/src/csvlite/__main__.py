import typer

app = typer.Typer()


@app.command()
def main() -> None:
    """CSVLite."""


if __name__ == "__main__":
    app(prog_name="csvlite")  # pragma: no cover
