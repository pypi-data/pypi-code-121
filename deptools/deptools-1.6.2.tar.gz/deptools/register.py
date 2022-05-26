# -*- coding: utf-8 -*-
'''AlazarTech Package Registration Script

Usage:
  register [--dev] [--dry-run] [-p <passfile>] <specfile> <base_url> <version>
  register -h | --help
  register --version

Options:
  -h --help      Show this screen
  -p <passfile>  If a password should be registered with the website, you can
                 give the file containing the password here.
  --dev          Register packages specified with the development website,
                 instead of the release version.
  --dry-run      Performs a practice run of the operation, without actually
                 sending an HTTP request to the website.

Arguments:
  <specfile>      Path to the YAML deployment specification file to use for
                  this deployment. See deploy.py for more information about the
                  file's format.
  <base_url>      Azure blob storage container path where the files are hosted.
  <version>       The version of the application to release

'''

import json
from collections import namedtuple

from docopt import docopt
import requests

from .spec import get_specs_from_file, get_things, getenv

# The nomenclature in this module can be confusing. Here is a breakdown of all
# important concepts:
#
# - Product: An item that can be sold or distributed for free by AlazarTech.
#   For example, ATS-SDK is a product. Each product has:
#
#   * a product key: a string of characters that is used in the filename of the
#    installation packages for products to identify them
#
#   * a product ID: a number used by the website to uniquely identify each
#     product.
#
# - Package: The installation software for a product on a specific OS. The .exe
#   package to install ATS-SDK on Windows is a package. In the code, we refer to
#   `PackageId` to mean the combination of a product key and an OS. This should
#   not be confused with product IDs.

PRODUCTS = {
    # Key: ID
    "ATS-GPU-BASE": '1034',
    "ATS-GPU-OCT": '1035',
    "ATS-GPU-NUFFT": '1040',
    "AlazarDSO": '1017',
    "ATS-SDK": '1018',
    "ATS310": '13',
    "ATS330": '12',
    "ATS460": '11',
    "ATS660": '1025',
    "ATS850": '15',
    "ATS860": '14',
    "ATS9120": '1028',
    "ATS9130": '1030',
    "ATS9146": '1039',
    "ATS9350": '4',
    "ATS9351": '5',
    "ATS9352": '1036',
    "ATS9353": '1041',
    "ATS9360": '2',
    "ATS9371": '1027',
    "ATS9373": '1',
    "ATS9416": '1016',
    "ATS9440": '9',
    "ATS9462": '8',
    "ATS9625": '6',
    "ATS9626": '7',
    "ATS9870": '3',
    "ATS9872": '1042',
    "ATS9628": '1047',
    "ATS9470": '1043',
    "ATST371": '1044',
    "ATST352": '1045',
    "ATST146": '1046',
}

# Identifies a package that can be registered to the website
PackageId = namedtuple(
    'PackageId',
    [
        'key',  # type: str
        'os',  # type: str
    ])


def get_os(filename):
    filename = filename.lower()
    if filename.endswith('.exe'):
        return 'Windows'
    if filename.endswith('.deb'):
        return 'Linux (.deb)'
    if filename.endswith('.rpm'):
        return 'Linux (.rpm)'
    if 'windows' in filename:
        return 'Windows'
    if 'debian' in filename:
        return 'Linux (.deb)'
    if 'centos' in filename:
        return 'Linux (.rpm)'
    if 'rpm' in filename:
        return 'Linux (.rpm)'
    raise ValueError("Could not determine OS for file {}".format(filename))


def get_product_key(filename):
    for key in PRODUCTS:
        if key.lower() in filename.lower():
            return key
    raise ValueError("Could not identify product for file {}".format(filename))


# The file and optional release notes associated with a package
Package = namedtuple(
    'Package',
    [
        'os',  # type: str
        'product_id',  # type: str
        'installer',  # type: str
        'readme',  # type: str
    ])


def packages_from_files(files):
    installers = {}  # type: Dict[PackageId, PackageContents]
    readmes = {}  # type: Dict[str, PackageContents]
    for filename in files:
        key = get_product_key(filename)
        if filename.endswith('.html'):
            # This is a release notes file
            if key in readmes:
                raise ValueError(
                    "Multiple release notes files for package {} found".format(
                        key))
            readmes[key] = filename
        else:
            # This is an installer
            packageid = PackageId(key, get_os(filename))
            if packageid in installers:
                raise ValueError(
                    "Multiple installers files for package ID {} found.".
                    format(packageid))
            installers[packageid] = filename
    packages = []  # type: List[Package]
    for packageid in installers:
        packages.append(
            Package(os=packageid.os,
                    product_id=PRODUCTS[packageid.key],
                    installer=installers[packageid],
                    readme=readmes[packageid.key]))
    return packages


def payload_from_packages(packages, base_url, version, password):
    if not base_url.endswith('/'):
        base_url = base_url + '/'
    if password is None:
        password = ""
    payload = []
    for package in packages:
        payload.append({
            "os": package.os,
            "product_id": package.product_id,
            "url": base_url + package.installer,
            "release_notes_url": base_url + package.readme,
            "version": version,
            "password": password,
        })
    return json.dumps(payload)


def register(development, passfile, specsfile, baseurl, version, dry_run):
    specs = get_specs_from_file(specsfile)
    files = [thing for spec in specs for thing in get_things(spec)]
    packages = packages_from_files(files)
    if development:
        endpoint = "https://dev.alazartech.com/go/to/the/dci/password-file-update/"
    else:
        endpoint = "https://www.alazartech.com/go/to/the/dci/password-file-update/"
    password = None
    if passfile:
        with open(passfile, 'r') as passf:
            password = passf.readline().strip()
    payload = payload_from_packages(packages, baseurl, version, password)
    print("The POST request parameters:")
    print("- endpoint: {}".format(endpoint))
    print("- data: {}".format(payload))
    if dry_run:
        print("Dry run, stopping here.")
        return
    res = requests.post(endpoint,
                        params={"key": getenv("WEBSITE_API_KEY")},
                        data=payload)
    if res.status_code != 200:
        raise ValueError("Registration request returned status code {}".format(
            res.status_code))


def main():
    '''Main function'''
    arguments = docopt(__doc__, version='Deloy Utility')
    register(development=arguments['--dev'],
             passfile=arguments['-p'],
             specsfile=arguments['<specfile>'],
             baseurl=arguments['<base_url>'],
             version=arguments['<version>'],
             dry_run=arguments['--dry-run'])

if __name__ == "__main__":
    main()
