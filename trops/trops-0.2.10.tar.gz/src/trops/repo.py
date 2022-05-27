import os
import subprocess

from configparser import ConfigParser
from textwrap import dedent

from .trops import Trops


class TropsRepo(Trops):

    def __init__(self, args, other_args):
        super().__init__(args, other_args)

        if other_args:
            msg = f"""\
                Unsupported argments: { ', '.join(other_args)}
                > trops repo --help"""
            print(dedent(msg))
            exit(1)

    def _check_current_branch(self):

        cmd = self.git_cmd + ['branch', '--show-current']
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            print(result.stderr.decode('utf-8'))
            exit(result.returncode)
        return result.stdout.decode('utf-8').strip()

    def push(self):

        current_branch = self._check_current_branch()
        git_conf = ConfigParser()
        git_conf.read(self.git_dir + '/config')
        if not git_conf.has_option('remote "origin"', 'url'):
            cmd = self.git_cmd + ['remote', 'add',
                                  'origin', self.git_remote]
            subprocess.call(cmd)
        if not git_conf.has_option(f'branch "{current_branch}"', 'remote'):
            cmd = self.git_cmd + \
                ['push', '--set-upstream', 'origin', current_branch]
        else:
            cmd = self.git_cmd + ['push']
        subprocess.call(cmd)

    def pull(self):
        """trops repo pull"""

        pull_work_tree = f'{self.trops_dir}/files/{self.trops_env}'
        if not os.path.isdir(pull_work_tree):
            os.makedirs(pull_work_tree, exist_ok=True)
        self.git_dir = os.path.expandvars(
            self.config[self.trops_env]['git_dir'])
        self.git_cmd = ['git', '--git-dir=' + self.git_dir,
                        f'--work-tree={pull_work_tree}']

        os.chdir(pull_work_tree)
        cmd = self.git_cmd + ['pull']
        subprocess.call(cmd)

    def clone(self):

        clone_work_tree = f'{self.trops_dir}/files/{self.trops_env}'
        if not os.path.isdir(clone_work_tree):
            os.makedirs(clone_work_tree, exist_ok=True)
        self.git_cmd = ['git', '--git-dir=' + self.git_dir,
                        f'--work-tree={clone_work_tree}']

        # git clone --bare -b <git_remote> <git_dir>
        cmd = ['git', 'clone', '--bare', '-b', f'{ self.args.git_branch }',
               f'{self.git_remote}', self.git_dir]
        subprocess.call(cmd)

        os.chdir(clone_work_tree)
        cmd = self.git_cmd + ['checkout']
        subprocess.call(cmd)


def repo_push(args, other_args):

    tf = TropsRepo(args, other_args)
    tf.push()


def repo_pull(args, other_args):

    tf = TropsRepo(args, other_args)
    tf.pull()


def repo_clone(args, other_args):

    tf = TropsRepo(args, other_args)
    tf.clone()


def add_repo_subparsers(subparsers):

    # trops repo
    parser_repo = subparsers.add_parser(
        'repo', help='track file operations')
    parser_repo.add_argument(
        '-e', '--env', help='Set environment name')
    repo_subparsers = parser_repo.add_subparsers()
    # trops repo push
    parser_repo_push = repo_subparsers.add_parser(
        'push', help='push repo')
    parser_repo_push.set_defaults(handler=repo_push)
    # trops repo pull
    parser_repo_pull = repo_subparsers.add_parser(
        'pull', help='pull repo')
    parser_repo_pull.set_defaults(handler=repo_pull)
    # trops file push
    parser_repo_clone = repo_subparsers.add_parser(
        'clone', help='clone repo')
    parser_repo_clone.add_argument(
        '--git-branch', help='Name of the git branch to clone', required=True)
    parser_repo_clone.set_defaults(handler=repo_clone)
