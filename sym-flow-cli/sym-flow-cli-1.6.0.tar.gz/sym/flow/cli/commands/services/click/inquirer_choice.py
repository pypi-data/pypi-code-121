from typing import List, Optional

import click
import inquirer

from sym.flow.cli.errors import MissingChoicesError


class InquirerChoiceOption(click.Option):
    """Custom click.Option that uses inquirer to prompt."""

    def __init__(self, *args, **kwargs):
        self.message: Optional[str] = kwargs.pop("inquirer_prompt", None)
        try:
            self.choices: List = kwargs.pop("inquirer_choices")
        except KeyError:
            raise MissingChoicesError()

        super().__init__(*args, **kwargs)

    def prompt_for_value(self, ctx):
        """Replaces click prompt with inquirer's prompt.
        Prompts for the given service types"""
        value = inquirer.list_input(
            self.message or self.prompt, choices=sorted(self.choices)
        )
        return self.process_value(ctx, value)
