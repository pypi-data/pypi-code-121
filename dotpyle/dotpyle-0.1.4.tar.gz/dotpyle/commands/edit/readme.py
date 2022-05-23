import click
from os import path
from shutil import copy2
from dotpyle.utils.path import get_dotpyle_readme_path
from dotpyle.utils import constants
from dotpyle.decorators.pass_repo_handler import pass_repo_handler
from dotpyle.services.repo_handler import RepoHandler


@click.command()
@pass_repo_handler
def readme(repo_handler: RepoHandler):
    """
    Open README.md file in the default editor and if it does not already
    exist, it will create it from a template
    """

    readme_path = get_dotpyle_readme_path()

    if not path.exists(readme_path):
        # Generate a README with default template
        copy2(constants.README_TEMPLATE_PATH, readme_path)

    # Open user default editor
    click.edit(filename=readme_path)

    repo_handler.add(constants.README_NAME, config_file_changed=False)
