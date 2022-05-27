#!/usr/bin/env python
import click

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass

