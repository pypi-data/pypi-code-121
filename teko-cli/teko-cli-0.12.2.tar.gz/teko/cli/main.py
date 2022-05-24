import typer

from teko.cli import jira_command, cs_command, oas_command

app = typer.Typer()
app.add_typer(jira_command.app, name="jira")
app.add_typer(cs_command.app, name="cs")
app.add_typer(oas_command.app, name="oas")

if __name__ == "__main__":
    app()
