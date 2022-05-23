"""
Command-line interface
"""
import sys
import click
import json

from aaindexer.scrape import scrape_parse


@click.command(help="Scrapes a single aaindex database, and prints the result to stdout. A progress bar is shown via stderr.")
@click.argument("database_number", type=int)
@click.option("--pretty/--no-pretty", default=True, help="If pretty (the default), pretty print the JSON, with newlines and indentation.")
def main(database_number: int, pretty: bool):
    result = scrape_parse(index=database_number, progress=True)
    indent = 4 if pretty else None
    json.dump(result, sys.stdout, indent=indent, default=lambda obj: obj.dict())
