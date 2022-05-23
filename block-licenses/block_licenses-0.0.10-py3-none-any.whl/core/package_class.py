"""Module stores PackageList Class."""
import json
import os
import sys
from configparser import ConfigParser
from itertools import chain, compress
from os.path import exists
from typing import List

import click
import pkg_resources
from pkg_resources import DistributionNotFound, get_distribution

class PackageList:
    """Package List Class."""

    def __init__(self, requirements: str = "requirements.txt"):
        if not os.path.isfile(requirements):
            click.echo(f"Did not found a '{requirements}' file.")
            sys.exit(1)

        # Getting the configuration file to check for licenses:
        config = ConfigParser()
        config_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '../config/default.ini')
        config.read(config_path)
        if exists("licenses.ini"):
            config.read('./licenses.ini')

        self.permitted_licenses = [value for value in config.get(
            'licenses', 'permitted').splitlines() if value]
        self.blocked_licenses = [value for value in config.get(
            'licenses', 'blocked').splitlines() if value]
        self.requirements = requirements
        self.detailed_list = self.get_package_list_from_requirements()

    @staticmethod
    def __filters(line):
        return compress(
            (line[9:],),
            (line.startswith('License:'),),
        )

    def get_package_list_from_requirements(self) -> List:
        """Returns a detailed package list based on the packages on requirements.txt.

        Returns:
            List: Detailed packages list.
        """
        packages_list = []
        with open(file=self.requirements, encoding='UTF-8') as file:
            for line in file:
                package = line.split('==')[0]
                if package[0] != "-":
                    packages_list.append(package)

        package_details = []
        for package in packages_list:
            package = self.get_licenses_from_package(package)

            # Sanitizing empty and UNKNOWN licenses:
            package['licenses'] = [
                l for l in package['licenses'] if l not in ['UNKNOWN', '', 'UNLICENSED']]
            package_details.append(package)

        return package_details

    def get_licenses_from_package(self, pkg_name: str):
        """Retrieve a dict of packages.

        Args:
            pkg_name (str): Name of the package.

        Returns:
            dict: List of packages.
        """
        try:
            dist = get_distribution(pkg_name)
        except DistributionNotFound:
            click.echo(f"Package '{pkg_name}' not found.\n \
                Have you installed all packages from the '{self.requirements}' file?")
            sys.exit(1)

        file_type_list = ['', '.txt', '.md', '.rst']
        file_name_list = ['license', 'copying', 'licenses']

        # just generating the meta_licenses_list:
        meta_licenses_list = []
        for file_type in file_type_list:
            # licenses meta as upper case:
            _ = [meta_licenses_list.append(
                f'{file_name.upper()}{file_type}') for file_name in file_name_list]

            # licenses meta as lower case:
            _ = [meta_licenses_list.append(
                f'{file_name}{file_type}') for file_name in file_name_list]

        license_content = [dist.get_metadata(
            meta) for meta in meta_licenses_list if dist.has_metadata(meta)]

        try:
            lines = dist.get_metadata_lines('METADATA')
        except OSError:
            print('LICENSE not found', pkg_name)
            lines = dist.get_metadata_lines('PKG-INFO')

        licenses_list = self.remove_license_word(list(chain.from_iterable(map(self.__filters, lines))))
        return {'package': dist.project_name, "version": dist.version,
                'licenses': licenses_list, "license_content": license_content}

    def check_blocked_licenses(self, mode: str = 'blocked'):
        """Returns a list with possible blocked packages.

        Args:
            verbose (bool, optional): Verbose output. Defaults to False.
            mode (str, optional): Block mode. Defaults to 'blocked'.

        Returns:
            List: List containing blocked packages.
        """
        blocked_list = []
        for index, package in enumerate(self.detailed_list):
            package_licenses = package.get('licenses')
            for license_name in package_licenses:
                if not license_name or license_name == 'UNKNOWN':
                    break
                if mode == 'permitted':
                    if license_name.lower() not in self.permitted_licenses:
                        blocked_list.append(self.detailed_list[index])
                        break
                else:
                    if license_name.lower() in self.blocked_licenses:
                        blocked_list.append(self.detailed_list[index])
                        break
        allowed_packages_list = [i for i in self.detailed_list if i not in blocked_list]

        for index, package in enumerate(allowed_packages_list):
            if len(package['licenses']) == 0:
                package['licenses'] = ['PSF']
                allowed_packages_list[index] = package
        return blocked_list, allowed_packages_list


    def remove_license_word(self, licenses_list):
        """
        Removes the word 'license' from a given list
        """
        sanatized_license = ""
        for index, value in enumerate(licenses_list):
            for i in value.split():
                if i.lower() != 'license':
                    sanatized_license += f'{i} '
            licenses_list[index] = sanatized_license.strip()
        return licenses_list
