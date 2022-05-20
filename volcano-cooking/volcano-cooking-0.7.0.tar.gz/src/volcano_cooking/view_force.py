"""CLI for the view_generated_forcing module.

This implements a wrapper for a function to be able to use it as a stand-alone program. It
takes a filename as a mandatory input parameter.
"""

import sys

import click

import volcano_cooking.helper_scripts.view_generated_forcing as v


@click.command()
@click.argument("filename", type=click.Path(exists=True), required=False)
@click.option(
    "--dark/--no-dark",
    "-k/-K",
    default=False,
    show_default=True,
    type=bool,
    help="Plot with dark background",
)
@click.option(
    "--width",
    "-w",
    default=2,
    show_default=True,
    type=int,
    help="Width of the plot in number of columns",
)
@click.option(
    "--style",
    "-t",
    default="connected",
    show_default=True,
    type=str,
    help="Plot style used to draw the data",
)
@click.option(
    "--style-options",
    "style_options",
    default=False,
    show_default=True,
    is_flag=True,
    help="Show the available styles and exit",
)
@click.option(
    "--save/--no-save",
    "-s/-S",
    default=False,
    show_default=True,
    type=bool,
    help="Save the plot",
)
def main(
    filename: str, width: int, style: str, style_options: bool, dark: bool, save: bool
):
    """View a plot of `filename`."""
    styles = {"connected", "bars"}
    if style_options:
        print(f"Available styles: {styles}")
        return
    if style not in styles:
        sys.exit(f"Style '{style}' not available. Available styles: {styles}")
    v.view_forcing(in_file=filename, width=width, style=style, dark=dark, save=save)
