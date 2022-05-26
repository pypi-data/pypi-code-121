import click 
from rich.console import Console

from rename_tools import rename

console = Console()

@click.command()
@click.argument('path', nargs=1)
@click.argument('old', nargs=1)
@click.argument('new', nargs=1)
@click.option('--recursive', is_flag=True, help='Rename recursively.')
def main(path, old, new, recursive):
    console.print(f'Renaming [red]"{old}"[/red] to [green]"{new}"[/green] in [black]"{path}"[/black]')
    rename(path, old, new, recursive)
    

if __name__ == '__main__':
    main()