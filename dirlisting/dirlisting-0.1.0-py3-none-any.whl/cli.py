import click

from dirlisting.dirlisting import Dirlisting


@click.command()
@click.argument("file", type=click.File())
def app(file):
    """Create a directory listing given an input FILE.

    The input should be a yaml file with directories having a colon
    after them and files without.

    Example
    -------
    This is a very simple input file.::

        \b
        - topdir:
          - file1.txt
          - somedir:
            - another_file.txt
    """
    listing = Dirlisting(file)
    listing.print()


if __name__ == "__main__":
    app()
