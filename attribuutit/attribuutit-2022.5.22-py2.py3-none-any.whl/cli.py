#! /usr/bin/env python
"""Scan a tree of files and extract attributes of the underlying vector or raster data."""
import json
import pathlib
import sys

import typer

import attribuutit.shp as shp
import attribuutit.tif as tif
import attribuutit.vpf as vpf

app = typer.Typer()


@app.command()
def eject(name: str) -> int:
    """Eject an example configuration in JSON format with stem equal to name."""
    typer.echo(f'This will eject an example configuration as {name}.json')
    return 0


@app.command()
def scan(name: str, dry_run: bool = False) -> int:
    """Scan the file system based on the configuration given in name.json and persist the report eventually."""
    if not dry_run:
        typer.echo(f'Real run changing the world following the configuration {name}.json - later ...')
        return 2

    typer.echo(f'Dry run exposing the plan of execution when following the configuration {name}.json - later ...')
    return 0


@app.command()
def inspect(path_str: str, dry_run: bool = False) -> int:
    """Inspect the file at path and persist the report eventually."""
    if not dry_run:
        typer.echo(f'Real run inspecting file at {path_str}')
        path = pathlib.Path(path_str)
        suffix = path.suffix
        if suffix == '.shp':
            shp.load(path)
        elif suffix == '.tif':
            tif.load(path)
        else:
            with open(path, 'rb') as source:
                vpf_artifact = vpf.Table(str(path), (b for b in source.read()))
            print(json.dumps(vpf_artifact.table, indent=2))
        return 0

    typer.echo(f'Dry run exposing the plan of execution when inspecting file at {path_str}')
    return 0


if __name__ == '__main__':
    sys.exit(app())
