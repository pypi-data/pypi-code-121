# MIT License

# Copyright (c) 2022 Divine Darkey

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

import click

from . import dupliCat, NoDuplicatesFound, NoFilesFoundError, __version__


@click.group()
def main() -> bool:  # type: ignore
    pass


@main.command(name="version")
def version():
    """outputs the version number of the script"""
    click.echo(click.style(f"\ndupliCat {__version__}", fg="green", bold=True))


@main.command(name="search-duplicates")
@click.option("--no-recurse", is_flag=True, help="Do not recurse into subdirectories")
@click.option("--path", default=os.getcwd(), help="Path to the directory to be scanned")
@click.option("--delete", is_flag=True, help="Delete duplicate files.")
def search_duplicates(path: str, no_recurse: bool, delete: bool) -> None:
    click.echo(click.style(f"Scanning {path!r}...\n", fg="green", bold=True))

    duplicat = dupliCat(path=path, recurse=not no_recurse)
    try:
        # do raw search
        duplicat.search_duplicate()
        duplicates = duplicat.junk_files  # take junk files from duplicat
    except NoDuplicatesFound:
        click.echo(click.style("No duplicates found.", fg="green", bold=True))
        return None
    except NoFilesFoundError:
        click.echo(click.style(f"{path!r} directory is empty.", bold=True))
        return None
    else:  # code below this lime should only execute when a duplicate is found

        # Print duplicated files if any found

        click.echo(click.style(f"\t {'File':94} Size", fg="blue", bold=True))
        click.echo(click.style(f"\t{'-' * 100}", fg="blue", bold=True))

        for file_ in sorted(duplicates):
            q = click.style(
                f"\t {file_.shorten_path(file_.relative(duplicat.path)):94} {file_.human_size}",
                fg="yellow",
                bold=True,
            )
            click.echo(q)

        # print out total size of duplicates
        total_size = sum(f.size for f in duplicates)
        length = len(duplicat.hash_index)  # number of duplicate files
        click.echo(click.style(f"\t{'-' * 100}", fg="yellow", bold=True))
        click.echo(
            click.style(
                f"\tFound {length} {'duplicate' if length == 1 else 'duplicates'}",
                bold=True,
                fg="green"
            )
        )
        click.echo(
            click.style(
                f"\tTotal size: {duplicat.human_size(total_size)}\n",
                fg="green",
                bold=True,
            )
        )

        if delete and length > 0:
            # asking for confirmation on whether to delete files
            confirmation = click.confirm(
                click.style(
                    "\nDo you want to delete duplicates? (This action is irreversible)",
                    bold=True,
                )
            )
            if not confirmation:
                return None

            # ask if we should keep a copy of a duplicate file or not
            keep_copy = click.confirm(
                click.style(
                    "Do you want to keep a copy of the original file?", bold=True
                )
            )

            # get all files from the duplicates data if we should delete all
            if not keep_copy:
                duplicates = duplicat.duplicates

            # deleting files
            counter = 0
            for file_ in duplicates:
                file_.delete()  # delete file
                counter += 1

            color = (
                "green"
                if counter == len(duplicates)
                else "yellow"
                if counter > 0
                else "red"
            )
            click.echo(
                click.style(
                    f"\nDeleted {counter} {'file' if counter == 1 else 'files'} out of {len(duplicates)}",
                    bold=True,
                    fg=color,
                )
            )


if __name__ == "__main__":
    main()
