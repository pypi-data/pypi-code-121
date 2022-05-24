import urllib3
from typing import List, Optional
from rich.live import Live
from rich.table import Table
from rich.console import Console
import typer
import time
import re
import requests


console = Console()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_site(url_list: List[str]):
    """main function to check the status of websites."""
    # configuring table
    table = Table()
    table.add_column("WEBSITE", justify="center")
    table.add_column("STATUS", justify="center")
    table.add_column("Last Request", justify="center")

    # validating URLS
    url_list = [validate_url(urls) for urls in url_list]

    for urls in url_list:
        try:
            requests.get(url=urls, timeout=2.5, verify=False)
            table.add_row(urls, "[green]ONLINE", f"{time.strftime('%H:%M:%S', time.localtime())}")
        except requests.exceptions.ConnectionError: # if the site is not online, the program will raise an exception.
            table.add_row(urls, "[red]OFFLINE", f"{time.strftime('%H:%M:%S', time.localtime())}")
        
    return table


def validate_url(url: str):
    """adds "http" scheme before url if it doesn't exist."""
    pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    if not re.match(pattern, url):
        return "http://" + url
    return url


def process_url(
    url: List[str] = typer.Option(..., "-u", "--url", help="URL of the site that needs to be checked."),
    cooldown: int = typer.Option(3, "-c", "--cooldown", help="Cooldown for the next request."),
    infinite: Optional[bool] = typer.Option(False, "-i", "--infinite", help="Runs an infinite loop until the user aborts it.")
    ):
    """Zeus the Investigator: Checks if a site is online at the moment."""
    if infinite:
        with Live(check_site(url), refresh_per_second=4) as live:
            live.console.print("\nInvestigator initiated!(Press [bold blue]CTRL+C[/] to quit)\n")
            while True:
                time.sleep(cooldown)
                live.update(check_site(url))
    else:
        console.print(check_site(url))
        console.print("\nInvestigation completed :thumbsup:\n")


def main():
    typer.run(process_url)