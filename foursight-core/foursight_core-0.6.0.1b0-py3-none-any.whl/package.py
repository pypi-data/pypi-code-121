import argparse
import subprocess
from foursight_core.deploy import Deploy
from sys import stdout
from os.path import dirname


class PackageDeploy(Deploy):
    config_dir = dirname(dirname(__file__))


def main(package_deploy=PackageDeploy):
    parser = argparse.ArgumentParser('chalice_package')
    parser.add_argument(
        'stage',
        type=str,
        choices=['dev', 'prod'],
        help="chalice package stage. Must be one of 'prod' or 'dev'")
    parser.add_argument(
        'output_file',
        type=str,
        help='Directory where generated template should be written')
    parser.add_argument(
        '--merge_template',
        type=str,
        help='Location of a YAML template to be merged into the generated template')
    parser.add_argument(
        '--trial',
        action='store_true',
        help='Use TRIAL creds when building the config and the trial S3 global env bucket (experimental)')
    args = parser.parse_args()
    package_deploy.build_config_and_package(args)


if __name__ == '__main__':
    main()
