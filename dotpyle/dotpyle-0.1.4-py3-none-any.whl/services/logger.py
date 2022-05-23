from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class Logger:
    def __init__(self, verbose):
        self.verbose = verbose
        if self.verbose:
            self.console = Console(color_system="auto")
        self.forced_console = Console(color_system="auto")

    def __print(self, text: Text) -> None:
        """
        Prints the message.
        """
        if self.verbose:
            self.console.print(text)

    def _print(self, *args) -> None:
        """
        Prints the message.
        """
        if self.verbose:
            self.console.print(*args)

    # def log(self, msg) -> None:
    # """
    # Prints a message to the console.
    # """
    # self.__print(Text(msg))

    def log(self, *msg) -> None:
        """
        Prints a message to the console.
        """
        self._print(*msg)

    def warning(self, msg) -> None:
        """
        Prints a warning message to the console.
        """
        self.__print(Text(msg, style="yellow"))

    def error(self, msg) -> None:
        """
        Prints an error message to the console.
        """
        self.__print(Text(msg, style="red"))

    def failure(self, *args) -> None:
        """
        Allways prints an error to user formated
        """
        self.forced_console.print("Error:", style="red bold", end=" ")
        self.forced_console.print(*args, style="bold")

    def alert(self, *args) -> None:
        """
        Allways prints an alert message to user
        """
        self.forced_console.print("Alert:", style="yellow", end=" ")
        self.forced_console.print(*args, style="yellow")

    def success(self, *args) -> None:
        """
        Allways prints a success message to user
        """
        self.forced_console.print("Success:", style="green bold", end=" ")
        self.forced_console.print(*args, style="")

    def print(self, *args) -> None:
        self.forced_console.print(*args)

    def print_config_errors(self, errors):
        tree = Tree(
            "🌲 [b red]Errors",
            highlight=True,
            guide_style="bold bright_blue",
        )

        for key, value in errors.items():
            # print('out', key, value)
            tree.add(f"[bold yellow]:open_file_folder:[link file://{key}]{key}")
            self.get_error(tree, key, value)
        self.forced_console.print(tree, style="")

    # TODO: move this to ConfigParser and create exceptions
    def get_error(self, tree, key, value):
        if type(value) == list:
            for elem in value:
                print("list", elem)
                self.get_error(tree, key, elem)
        elif type(value) == dict:
            for k, v in value.items():
                tree = tree.add(
                    f"[bold blue]:open_file_folder:[link file://{k}]{k}"
                )
                self.get_error(tree, k, v)
        else:
            # print(" - {}: '{}'".format(key, value))
            tree.add(value)
