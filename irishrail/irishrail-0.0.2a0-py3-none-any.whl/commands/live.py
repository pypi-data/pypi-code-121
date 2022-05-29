import itertools
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

from irishrail import IrishRail


def live(station):
    client = IrishRail()
    data = client.next_trains(station)

    northbound = []
    southbound = []
    for train in data:
        if train["Direction"] == "Southbound":
            southbound.append(train)
        else:
            northbound.append(train)

    title = Text.assemble(
        "\n",
        (station.title(), "bold"),
        "\n",
        ("Northbound", "light_green bold"),
        " / ",
        ("Southbound", "sandy_brown bold"),
    )

    table = Table(
        title=title,
        caption=f"Updated at: {datetime.now()}",
        border_style="grey70",
        box=box.DOUBLE_EDGE,
        row_styles=["", "dim"],
        title_style="white bold",
        caption_style="gray70",
    )
    table.add_column("Destination", style="light_green")
    table.add_column("Due in", style="light_green")
    table.add_column("Destination", style="sandy_brown")
    table.add_column("Due in", style="sandy_brown")

    for north, south in itertools.zip_longest(northbound, southbound, fillvalue={}):
        table.add_row(
            north.get("Destination", ""),
            north.get("Duein", ""),
            south.get("Destination", ""),
            south.get("Duein", ""),
        )

    return table
