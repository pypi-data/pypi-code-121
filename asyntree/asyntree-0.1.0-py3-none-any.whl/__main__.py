import typer

app = typer.Typer()


@app.command()
def main() -> None:
    """Asyntree."""


if __name__ == "__main__":
    app(prog_name="asyntree")  # pragma: no cover
