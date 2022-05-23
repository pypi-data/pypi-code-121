"""CLI module for asciify package."""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import click
from PIL import Image

from .algo import AsciiManager


@click.command()
@click.argument(
    'input_path',
    type=click.Path(dir_okay=False, readable=True))
@click.option(
    '-w', '--width',
    type=click.IntRange(min=1, max=1000),
    help='Output ASCII art width (input image width by default).')
@click.option(
    '-h', '--height',
    type=click.IntRange(min=1, max=1000),
    help='Output ASCII art height (input image height by default).')
@click.option(
    '-o', '--output',
    type=click.Path(dir_okay=False, writable=True, readable=False),
    help='Output ASCII art path (stdout by default).')
@click.option(
    '-f', '--fontname',
    type=click.Path(dir_okay=False, readable=True),
    help='Path to a font for image approximation.')
@click.option(
    '-s', '--fontsize',
    type=click.IntRange(min=1, max=96),
    default=42,
    show_default=True,
    help='Font size for image approximation.')
@click.option(
    '-v/-q', '--verbose/--quiet',
    is_flag=True,
    show_default=True,
    default=True,
    help='Verbosity flag.')
def asciify(input_path: Union[str, Path],
            width: Optional[int] = None,
            height: Optional[int] = None,
            output: Optional[Union[str, Path]] = None,
            fontname: Optional[Union[str, Path]] = None,
            fontsize: int = 42,
            verbose: bool = True,
            ) -> None:
    """Transform an image to an ASCII art and dump it to stdout or a file."""

    options: Dict[str, Any] = {
        'fontname': fontname,
        'fontsize': fontsize,
        'verbose': verbose,
    }
    manager = AsciiManager(**{
        key: val
        for key, val in options.items()
        if val is not None
    })

    image = Image.open(input_path)
    if width is None:
        if height is None:
            width, height = image.size
        else:
            width = image.width * height // image.height
    elif height is None:
        height = image.height * width // image.width

    text = manager.transform(image, (width, height))
    if output is None:
        print(text)
        return
    with open(output, 'w', encoding='utf-8') as file:
        print(text, file=file)


if __name__ == '__main__':
    asciify()
