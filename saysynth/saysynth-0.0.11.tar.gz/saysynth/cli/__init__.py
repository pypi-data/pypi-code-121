import click
import os

COMMAND_METHOD = "run"
COMMANDS_FOLDER = os.path.join(os.path.dirname(__file__), "commands")
COMMAND_NAMES = [
    filename[:-3]
    for filename in os.listdir(COMMANDS_FOLDER)
    if filename.endswith(".py") and not filename.startswith("__")
]


class SaySynthCLI(click.MultiCommand):
    commands = COMMAND_NAMES

    def list_commands(self, ctx):
        return self.commands

    def get_command(self, ctx, name):
        if name not in self.commands:
            raise ValueError(f"Invalid command name: {name}")
        ns = {}
        fn = os.path.join(COMMANDS_FOLDER, name + ".py")
        with open(fn) as f:
            code = compile(f.read(), fn, "exec")
            eval(code, ns, ns)
        return ns[COMMAND_METHOD]


main = SaySynthCLI(help="Make the `say` command a synthesizer")

if __name__ == "__main__":
    main()
