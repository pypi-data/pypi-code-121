import logging
import os

from rich.console import Console
from rich.table import Table
from rich.live import Live

from .game import Pydle
from ._stats import Stats
from . import app_paths

logging.basicConfig(filename=app_paths.log_file_path, level=logging.INFO)
_logger = logging.getLogger(__name__)


def clear():
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")


def _print_graph(attempts):
    import termplotlib as tpl

    attempts = dict(sorted(attempts.items()))

    fig = tpl.figure()
    fig.barh(list(attempts.values()), list(attempts.keys()), force_ascii=True)
    fig.show()


def run():
    stats = Stats()
    game = Pydle()
    console = Console()
    table = Table(title="Guesses", box=None)
    console.print(table)

    found: bool = False
    MAX_ATTEMPTS: int = 6
    retries: int = 6

    while retries and not found:
        game.get_user_guess(remaining=retries)
        found, result = game.process_user_guess()
        clear()
        with Live(table):
            guess_row = [
                f'[black on {res["color"]}] {res["letter"]} [/black on {res["color"]}]'
                for res in result
            ]
            table.add_row(*guess_row)
            table.add_row("")
            retries -= 1

    game_stats = {
        "attempts": MAX_ATTEMPTS - retries,
        "found": found,
    }

    stats.update(game_stats)

    if found:
        console.print(
            f"\n :thumbs_up: Wow, you aced it in {MAX_ATTEMPTS - retries} guesses!!\n"
        )
    else:
        console.print(
            f"\n\n☹️  [bold red]Correct Word is {game._word_choice.upper()} [/bold red]"
        )

    total_stats = stats.parse_stats()
    console.print(
        f'You have won {total_stats["wins"]} times out of {total_stats["games"]}!\n'
        f'That\'s {int(total_stats["wins"] / total_stats["games"] * 100)}% !'
    )
    try:
        console.print("[bold]Player Statistics[/bold]")
        total_attempts = total_stats["attempts"]
        for i in range(1, MAX_ATTEMPTS+1):
            if i not in total_attempts:
                total_attempts[i] = 0
        _print_graph(total_attempts)
    except:
        return


if __name__ == "__main__":
    run()
