import typer

app = typer.Typer()


@app.command(name="tournament-result")
def create_dsa_problem(
        tournament_id: str = typer.Argument(..., help='The id of the tournament'),
   ):
    """
    """
    print(f"Getting tournament: {tournament_id}")
