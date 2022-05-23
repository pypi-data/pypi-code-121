import json
import os
import re
import sys
from configparser import ConfigParser
from typing import List

import click

from app.core.package_class import PackageList

config = ConfigParser()
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-b', '--blocked', is_flag=True, default=False, type=bool, help='Print blocked licenses list.')
@click.option('-p', '--permitted', is_flag=True, default=False, type=bool, help='Print permitted licenses list.')
@click.option('-i', '--interactive', is_flag=True, default=False, type=bool,
              help='Block packages interactively by analysing their licenses.')
@click.option('-q', '--quiet', is_flag=True, default=False, type=bool, help='Do not print any output.')
@click.option('-v', '--verbose', is_flag=True, default=False, type=bool,
              help='Print a detailed output for blocked packages.')
@click.option('-P', '--paranoid', is_flag=True, default=False, type=bool,
              help='Paranoid mode for the interactive option, loop through each package even if contains \
              a license that was already checked.')
@click.option('-r', 'requirements', default="requirements.txt", type=str,
              help='Indicate the requirements file to be used.')
@click.option('-a', '--all', 'all_requirements', is_flag=True, default=False, type=str,
              help='Print all available licenses based on the requirements file.')
@click.option(
    '--mode', type=click.Choice(['permitted', 'blocked'],
                                case_sensitive=False), default='blocked',
    help='Mode which will be used to check packages, either from the permitted list or blocked list perspective.')
@click.option(
    '--format', 'format_to', type=click.Choice(['text', 'json', 'column', 'content'],
                                               case_sensitive=False), default='json',
    help='Format output.')
@click.option('--get-allowed', is_flag=True, default=False, type=bool,
              help='Retrieve allowed packages instead.')
@click.pass_context
def cli(ctx, blocked, permitted, interactive, quiet, #pylint: disable=unused-argument
        verbose, paranoid, requirements, all_requirements, mode, format_to, get_allowed):
    """
    CLI tool that helps us easily define which licenses are not good based on the requirements.txt file.
    It uses pkg_resources to get details from the packages, given us the licenses listed byt the package
    owner and returns exit 1 if found a package that contains a blocked license.
    """
    packages = PackageList(requirements=requirements)
    blocked_licenses, allowed_packages = packages.check_blocked_licenses(mode=mode)

    if get_allowed:
        format_output(content_list=allowed_packages,
                      verbose=verbose, format_to=format_to)
        sys.exit(0)

    # if get_allowed

    if all_requirements:
        # Print all packages found on requirements:
        format_output(content_list=packages.detailed_list,
                      verbose=verbose, format_to=format_to)
        print()
        return sys.exit(0)

    if permitted:
        # Print Permitted list:
        format_output(content_list=packages.permitted_licenses,
                      verbose=verbose, format_to=format_to)
        return sys.exit(0)

    if blocked:
        # Print Blocked list:
        format_output(content_list=packages.blocked_licenses,
                      verbose=verbose, format_to=format_to)
        return sys.exit(0)

    if interactive:
        # Prompt interactively to build a licenses.ini:
        build_interactively(packages.detailed_list, paranoid)
        sys.exit(0)

    if len(blocked_licenses) > 0:
        if not quiet:
            click.echo(f"Found Blocked on '{mode}' mode:")
            format_output(blocked_licenses, verbose=verbose,
                          format_to=format_to)
            sys.exit(1)
        sys.exit(1)


def format_output(content_list: List, verbose: bool = False, format_to: str = 'json'):
    """
    Helper function to print the output of the content list as 'json', 'text' or 'column'.

    Args:
        content_list(list): Content list to be formatted and printed.
        verbose(bool): Either to print more detailed info or not.
        format_to(str): DEFAULT 'json' - format option to be printed.
    """
    has_package_details = isinstance(content_list[0], dict)

    # Removing License Content
    if format_to != 'content':

        # TODO: rethink this for retrive only licenses:
        for item in content_list:
            if not isinstance(item, str):
                del item['license_content']

    # FORMAT TO JSON:
    if format_to == 'json':
        click.echo(json.dumps(content_list, indent=2))

    # FORMAT TO TEXT or CONTENT:
    if format_to == 'text' or format_to == 'content':
        if verbose:
            click.echo(f'{"NAME": <70} {"VERSION": >12} {"": ^4} LICENSES\n')
        else:
            click.echo(f'{"NAME": <70} {"VERSION": >12}\n')
        for item in content_list:
            name, version, licenses = item['package'], item['version'], item['licenses']
            if has_package_details:
                if verbose:
                    click.echo(f'{name: <70} {version: >12} {"": ^4} {licenses[:2]}')
                else:
                    click.echo(f'{name: <70} {version: >12}')
            else:
                click.echo(f' - {item}' if verbose else f'{item}')
        if format_to == 'content':

            for item in content_list:
                appendix = f'APPENDIX - {item["package"]} ({item["version"]})'
                horizontal_line = f'{"_" * len(appendix)}\n'
                click.echo(f'\n\n{"#" * 100}\n\n')
                click.echo(appendix)
                click.echo(horizontal_line)

                if len(item['license_content']) > 0:
                    click.echo(item['license_content'][0])
                else:
                    click.echo('LICENSE NOT PROVIDED ON PACKAGE')

    # FORMAT TO COLUMN:
    if format_to == 'column':
        for item in content_list:
            if has_package_details:
                if verbose:
                    click.echo(
                        f'| {item.get("package")} | {item.get("licenses")} |')
                else:
                    click.echo(f'| {item.get("package")} |')
            else:
                click.echo(f' - {item}' if verbose else f'{item}')


def build_interactively(detailed_list, paranoid):
    """
    Function to build a licenses.ini file interactively.

    Args:
        detailed_list(list): List of the detailed packages generated by PackageList instance.
        paranoid(bool): Avoid sanitizing packages to loop through each package regardless if a license was checked.
    """
    blocked_licenses = []
    permitted_licenses = []
    unknown_licenses = []

    for index, package in enumerate(detailed_list):
        # PROMPT LICENSES:
        if len(package['licenses']) > 0:

            previous_package = None
            for license_name in package['licenses']:
                # Avoid List helps not repeat the same license:
                avoid_list = blocked_licenses + \
                    permitted_licenses + ['UNKNOWN', '']
                if paranoid or license_name.lower() not in avoid_list:
                    if not package:
                        break
                    if license_name == 'UNKNOWN':
                        unknown_licenses.append(package)
                        break

                    if previous_package != package:
                        click.echo('PACKAGE DETAILS:')
                        click.echo(json.dumps(package, indent=2))
                    if not click.confirm(
                            f"Should the license '{license_name.upper()}' be blocked? "
                            f"({index + 1}/{len(detailed_list)})"):
                        permitted_licenses.append(license_name.lower())
                    else:
                        blocked_licenses.append(license_name.lower())
                    previous_package = package

                if not paranoid:
                    sanitize_licenses(detailed_list, license_name)

    with open('licenses.ini', 'w', encoding='UTF-8') as file:
        file.write('[licenses]\npermitted:\n')
        write_lines_to_file(file, permitted_licenses)

        file.write('\nblocked:\n')
        write_lines_to_file(file, blocked_licenses)

    if len(unknown_licenses) > 0:
        click.echo('---')
        click.echo('Found unknown licenses for the following packages:')
        format_output(content_list=unknown_licenses, format_to='text')
        click.echo('\nPlease check those licenses manually on PyPi.')


def write_lines_to_file(file, content_list):
    """
    Helper function that will write lines to the given file.

    Args:
        file(IO Stream): File to be used.
        content_list(list): List of contents to be written in the file.
    """
    for license_name in content_list:
        file.write(f"    {license_name}\n")


def sanitize_licenses(detailed_list, license_name) -> list:
    """
    This will remove any packages that contain a license that was already verified.

    Args:
        detailed_list(list): List of the detailed packages generated by PackageList instance.
        license_name(str): Name of the license to be checked.

    Returns:
        Sanitized detailed_list.
    """
    for package in detailed_list:
        if len(package['licenses']) > 0:
            package['licenses'] = [
                value for value in package['licenses'] if value != license_name]
    return detailed_list
