#!/usr/bin/python3
"""Fuel dataset downloading utility."""
import argparse
from kdmt.download import default_downloader
import os
from kdmt.file import read_json_file
from kolibri.data.downloader import NeedURLPrefix
from kolibri.settings import DATA_PATH
url_prefix_message = """
Some files for this dataset do not have a download URL.

Provide a URL prefix with --url-prefix to prepend to the filenames,
e.g. http://path.to/files/
""".strip()




def __fill_subparser(subparser, dataset, urls,filenames=None):
    """Set up a subparser to download the adult dataset file.

    The Adult dataset file `adult.data` and `adult.test` is downloaded from
    the UCI Machine Learning Repository [UCIADULT].

    .. [UCIADULT] https://archive.ics.uci.edu/ml/datasets/Adult

    Parameters
    ----------
    subparser : :class:`argparse.ArgumentParser`
        Subparser handling the adult command.

    """
    subparser.set_defaults(
        directory=os.path.join(DATA_PATH, "datasets", dataset),
        urls=urls,
        filenames=filenames)
    return default_downloader



def main(args=None):
    """Entry point for `fuel-download` script.

    This function can also be imported and used from Python.

    Parameters
    ----------
    args : iterable, optional (default: None)
        A list of arguments that will be passed to Fuel's downloading
        utility. If this argument is not specified, `sys.argv[1:]` will
        be used.

    """

    built_in_datasets = dict(read_json_file("datasets_configs.json"))

    parser = argparse.ArgumentParser(
        description='Download script for built-in datasets.')
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-d", "--directory", help="where to save the downloaded files",
        type=str, default=os.getcwd())
    parent_parser.add_argument(
        "--clear", help="clear the downloaded files", action='store_true')
    subparsers = parser.add_subparsers()
    download_functions = {}
    for name, subparser_data in built_in_datasets.items():
        subparser = subparsers.add_parser(
            name, parents=[parent_parser],
            help='Download the {} dataset'.format(name))
        # Allows the parser to know which subparser was called.
        subparser.set_defaults(which_=name)
        download_functions[name] = __fill_subparser(subparser, name, subparser_data["urls"], subparser_data["filenames"])
    args = parser.parse_args()
    args_dict = vars(args)
    which=args_dict.pop('which_')
    download_function = download_functions[which]
    try:
        download_function(**args_dict)
    except NeedURLPrefix:
        parser.error(url_prefix_message)


if __name__ == "__main__":
    main()
