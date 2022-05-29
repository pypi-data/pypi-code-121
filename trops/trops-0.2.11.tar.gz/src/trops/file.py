import distutils.util
import os
import subprocess

from configparser import ConfigParser
from textwrap import dedent

from .trops import Trops
from .utils import absolute_path


class TropsFile(Trops):

    def __init__(self, args, other_args):
        super().__init__(args, other_args)

        if other_args:
            msg = f"""\
                Unsupported argments: { ', '.join(other_args)}
                > trops file <subcommand> --help"""
            print(dedent(msg))
            exit(1)

        # trops file put <path> <dest>
        if hasattr(args, 'path'):
            self.path = args.path
        if hasattr(args, 'dest'):
            # Make sure destination(dest) is a directory
            if os.path.isdir(args.dest):
                # Change work_tree from orginal to args.dest
                self.work_tree = absolute_path(args.dest)
                self.git_cmd = ['git', '--git-dir=' + self.git_dir,
                                '--work-tree=' + self.work_tree]

                sudo_true = distutils.util.strtobool(
                    self.config[self.trops_env]['sudo'])
                if sudo_true:
                    self.git_cmd = ['sudo'] + self.git_cmd
            else:
                print(f"ERROR: '{ args.dest }' is not a directory")
                exit(1)

    def list(self):

        os.chdir(self.work_tree)
        cmd = self.git_cmd + ['ls-files']
        subprocess.call(cmd)

    def put(self):

        cmd = self.git_cmd + ['checkout', self.path]
        subprocess.call(cmd)


def file_list(args, other_args):

    tf = TropsFile(args, other_args)
    tf.list()


def file_put(args, other_args):

    tf = TropsFile(args, other_args)
    tf.put()


def add_file_subparsers(subparsers):

    # trops file
    parser_file = subparsers.add_parser(
        'file', help='track file operations')
    parser_file.add_argument(
        '-e', '--env', help='Set environment name')
    file_subparsers = parser_file.add_subparsers()
    # trops file list
    parser_file_list = file_subparsers.add_parser(
        'list', help='list files')
    parser_file_list.set_defaults(handler=file_list)
    # trops file put
    parser_file_put = file_subparsers.add_parser(
        'put', help='put file')
    parser_file_put.add_argument(
        'path', help='file/dir path')
    parser_file_put.add_argument(
        'dest', help='dest path where you put the file/dir')
    parser_file_put.set_defaults(handler=file_put)
