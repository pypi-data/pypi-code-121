from typing import List

import click
import inquirer
from inquirer.questions import Question


def ask(questions: List[Question]):
    answers = inquirer.prompt(questions)
    if not answers:
        raise click.Abort()
    return answers
