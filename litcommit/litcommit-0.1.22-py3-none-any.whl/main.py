from venv import create
import click
import requests
import json
from git import Repo
import os
import sys 
from pydriller import Git
from library import iterate_over_diffs
from library import put_into_df
from library import create_prompt

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")


@click.group()
def apis():
    """Welcome to LitCommit 🔥"""


@apis.command()
def predict():
    """Run prediction"""
    click.echo("Use this function to run a prediction!")

@apis.command()
def commit():
    """Commit current diffs and have CodeCommenter comment the commit for you"""
    # Git add -A
    # Get current difs
    # Get preds
    # Commit
    repo = Repo(os.getcwd())

    # commit current changes
    repo.git.commit('-am',"pre commit")
    # get last commit
    gr = Git(os.getcwd())
    commit = gr.get_head()

    # reset the pre commit
    # repo.git.reset('--soft')
    repo.head.reset('HEAD~1')

    # get a LIST of parsed diffs, one entry per file
    parsed_diffs = []
    for mod in commit.modified_files:
        parsed_diff = mod.diff_parsed
        parsed_diffs.append(parsed_diff)

    parsed_diffs_cleaned = iterate_over_diffs(parsed_diffs)
    df = put_into_df(parsed_diffs_cleaned)
    prompt = create_prompt(df)
    click.echo("PROMPT")
    click.echo(str(prompt))
    

    resp = requests.post('https://api.litcommit.com/predict/commit', json={"prompt": str(prompt)}) 
    # Then commit those
    # print(resp.status_code)
    # resp = resp.json()
    # click.echo(results[0]['text'])
    click.echo(" 🔥 Here are 3 commit messages, which would you like to use? Hit 1., 2., or 3. to commit.")
    results = resp.json()
    click.echo('Option 1: {}'.format(results[0]['text']))
    click.echo('Option 2: {}'.format(results[1]['text']))
    click.echo('Option 3: {}'.format(results[2]['text']))
    value = click.prompt('Please enter 1, 2, or 3:')

    repo.git.commit('-am', results[int(value)-1]['text'])


def predict():
    """Run prediction"""
    username = click.prompt('Username', type=str)
    password = click.prompt('Password', type=str, hide_input=True)
    if authenticate_warrant(username=username, password=password):
        click.echo("Successfully authenticated with Spikit!")
    else:
        click.echo("Invalid username and password. Login")


def main():
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("CVE")
    apis(prog_name="lit")

if __name__=='__main__':
    main()