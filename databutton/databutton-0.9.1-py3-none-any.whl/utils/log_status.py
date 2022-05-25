import click

from databutton import __version__
from databutton.utils.build import ArtifactDict

string_length = 24


def log_devserver_screen(components: ArtifactDict, time_spent_starting: int):
    click.clear()
    click.echo()
    local_url = click.style("http://localhost:8000", fg="cyan")
    click.echo(
        click.style(
            f"databutton v{__version__} dev server running on {local_url}",
            fg="green",
        )
    )

    if len(components.streamlit_apps) > 0:
        click.echo()
        click.echo(click.style("apps", fg="cyan", bold=True))
        for st in components.streamlit_apps:
            click.echo(f"name: {st.name:<24} > http://localhost:8000{st.route}")

    if len(components.schedules) > 0:
        click.echo()
        click.echo(click.style("jobs", fg="cyan", bold=True))
        for job in components.schedules:
            click.echo(f"name: {job.name:<24}> every: {job.seconds}s")

    click.echo()
    click.echo(click.style(f"ready in {time_spent_starting}ms.", fg="cyan"))
    click.echo(click.style("waiting for changes.", fg="cyan"))
