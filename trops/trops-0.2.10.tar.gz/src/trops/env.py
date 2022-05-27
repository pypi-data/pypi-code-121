import os
import subprocess

from configparser import ConfigParser
from shutil import rmtree
from textwrap import dedent

from .utils import absolute_path, yes_or_no


class TropsEnv:

    def __init__(self, args, other_args):

        if other_args:
            msg = f"""\
                Unsupported argments: { ', '.join(other_args)}
                > trops env <subcommand> --help"""
            print(dedent(msg))
            exit(1)

        self.args = args

        if hasattr(args, 'dir'):
            self.trops_dir = absolute_path(args.dir) + '/trops'
        elif 'TROPS_DIR' in os.environ:
            self.trops_dir = absolute_path('$TROPS_DIR')
        else:
            print('TROPS_DIR does not exists')
            exit(1)

        if hasattr(args, 'work_tree'):
            self.trops_work_tree = args.work_tree

        if hasattr(args, 'git_remote'):
            self.trops_git_remote = args.git_remote
        else:
            self.trops_git_remote = None

        if hasattr(args, 'env') and args.env:
            # Exit if the env name has a space
            if ' ' in args.env:
                print("You cannot use a space in environment name")
                exit(1)
            else:
                self.trops_env = args.env
        elif os.getenv('TROPS_ENV'):
            self.trops_env = os.getenv('TROPS_ENV')
        else:
            self.trops_env = None

        if hasattr(args, 'git_branch') and args.git_branch:
            self.trops_git_branch = args.git_branch
        else:
            self.trops_git_branch = f'trops/{self.trops_env}'

        if hasattr(args, 'git_dir') and args.git_dir:
            self.trops_git_dir = args.git_dir
        elif hasattr(self, 'trops_env'):
            self.trops_git_dir = self.trops_dir + \
                f'/repo/{ self.trops_env }.git'

        self.trops_conf = self.trops_dir + '/trops.cfg'
        self.trops_log_dir = self.trops_dir + '/log'

    def _setup_dirs(self):

        # Create trops_dir
        try:
            os.makedirs(self.trops_dir, exist_ok=True)
        except FileExistsError:
            print(f"{ self.trops_dir } already exists")

        # Create trops_dir/log
        try:
            os.mkdir(self.trops_log_dir)
        except FileExistsError:
            print(f'{ self.trops_log_dir} already exists')

        # Create trops_dir/repo
        repo_dir = f"{self.trops_dir}/repo"
        try:
            os.mkdir(repo_dir)
        except FileExistsError:
            print(f'{ repo_dir } already exists')

    def _setup_trops_conf(self):

        config = ConfigParser()
        if os.path.isfile(self.trops_conf):
            config.read(self.trops_conf)
            if config.has_section(self.trops_env):
                print(
                    f"The '{ self.trops_env }' environment already exists on { self.trops_conf }")
                exit(1)

        config[self.trops_env] = {'git_dir': f'$TROPS_DIR/repo/{ self.trops_env }.git',
                                  'sudo': 'False',
                                  'work_tree': f'{ self.trops_work_tree}'}
        if self.trops_git_remote:
            config[self.trops_env]['git_remote'] = self.trops_git_remote
        if self.args.logfile:
            config[self.trops_env]['logfile'] = self.args.logfile
        if self.args.tags:
            config[self.trops_env]['tags'] = self.args.tags

        with open(self.trops_conf, mode='w') as configfile:
            config.write(configfile)

    def setup_git_config(self, git_dir):

        git_cmd = ['git', '--git-dir=' + git_dir]
        git_conf = ConfigParser()
        git_conf.read(git_dir + '/config')
        # Set "status.showUntrackedFiles no" locally
        if not git_conf.has_option('status', 'showUntrackedFiles'):
            cmd = git_cmd + ['config', '--local',
                             'status.showUntrackedFiles', 'no']
            subprocess.call(cmd)
        # Set $USER as user.name
        if not git_conf.has_option('user', 'name'):
            username = os.environ['USER']
            cmd = git_cmd + ['config', '--local', 'user.name', username]
            subprocess.call(cmd)
        # Set $USER@$HOSTNAME as user.email
        if not git_conf.has_option('user', 'email'):
            useremail = username + '@' + os.uname().nodename
            cmd = git_cmd + ['config', '--local', 'user.email', useremail]
            subprocess.call(cmd)

    def _setup_bare_git_repo(self):

        git_cmd = ['git', '--git-dir=' + self.trops_git_dir]
        # Create trops's bare git directory
        if not os.path.isdir(self.trops_git_dir):
            cmd = ['git', 'init', '--bare', self.trops_git_dir]
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0:
                print(result.stdout.decode('utf-8'))
            else:
                print(result.stderr.decode('utf-8'))
                exit(result.returncode)

        self.setup_git_config(self.trops_git_dir)

        cmd = git_cmd + ['branch', '--show-current']
        branch_name = subprocess.check_output(cmd).decode("utf-8").strip()
        new_branch_name = self.trops_git_branch
        print(f'new_branch_name = {new_branch_name}')
        if new_branch_name not in branch_name:
            cmd = git_cmd + ['--work-tree=/',
                             'checkout', '-b', new_branch_name]
            subprocess.call(cmd)

    def create(self):

        self._setup_dirs()
        self._setup_trops_conf()
        self._setup_bare_git_repo()

    def _delete_env_from_conf(self):

        config = ConfigParser()
        if os.path.isfile(self.trops_conf):
            config.read(self.trops_conf)
            if config.has_section(self.trops_env):
                if yes_or_no(f"Really want to remove { self.trops_env } from { self.trops_conf }?"):
                    config.remove_section(self.trops_env)
                    print(
                        f"Deleting { self.trops_env } from { self.trops_conf }..")
                    with open(self.trops_conf, mode='w') as configfile:
                        config.write(configfile)

    def _delete_git_dir(self):

        # Check if the self.trops_git_dir ends with .git
        dirname = os.path.basename(self.trops_git_dir)
        if dirname[-4:] == '.git':
            really_ok1 = True
        else:
            really_ok1 = False

        # Check if self.trops_git_dir/config
        # has_option('status', 'showUntrackedFiles')
        git_config_file = f"{ self.trops_git_dir }/config"
        git_config = ConfigParser()
        if os.path.isfile(git_config_file):
            git_config.read(git_config_file)
            if git_config.has_option('status', 'showUntrackedFiles'):
                really_ok2 = True
            else:
                really_ok2 = False

        # then delete it
        if really_ok1 and really_ok2:
            if yes_or_no(f"Really want to delete { self.trops_git_dir }?"):
                rmtree(self.trops_git_dir)
                print(f"Deleting { self.trops_git_dir }..")

    def delete(self):

        if self.trops_env == os.getenv('TROPS_ENV'):
            msg = f"""\
                You're still on the {self.trops_env} environment. Please go off from it before deleting it.
                    > offtrops
                    > trops env delete {self.trops_env}"""
            raise SystemExit(dedent(msg))

        self._delete_env_from_conf()
        self._delete_git_dir()

    def update(self):

        config = ConfigParser()
        if os.path.isfile(self.trops_conf):
            config.read(self.trops_conf)
            if not config.has_section(self.trops_env):
                print(
                    f"The '{ self.trops_env }' environment does not exists on { self.trops_conf }")
                exit(1)

        if self.args.git_remote:
            config[self.trops_env]['git_remote'] = self.args.git_remote
        if self.args.logfile:
            config[self.trops_env]['logfile'] = self.args.logfile
        if self.args.tags:
            config[self.trops_env]['tags'] = self.args.tags
        # --tags='' should delete the tags option
        if self.args.tags == '':
            config.remove_option(self.trops_env, 'tags')

        with open(self.trops_conf, mode='w') as configfile:
            config.write(configfile)

    def list(self):

        config = ConfigParser()
        config.read(self.trops_conf)
        current_env = self.trops_env

        for envname in config.sections():
            if envname == current_env:
                print(f'- { envname }*')
            else:
                print(f'- { envname}')

    def show(self):

        print('ENV')
        try:
            print(f"  {'TROPS_DIR '.ljust(11)} = {os.getenv('TROPS_DIR')}")
        except KeyError:
            print(f"  {'TROPS_DIR '.ljust(11)} = None")
            exit(1)
        try:
            print(f"  {'TROPS_ENV'.ljust(11)} = {os.environ['TROPS_ENV']}")
            trops_env = os.environ['TROPS_ENV']
        except KeyError:
            print(f"  {'TROPS_ENV'.ljust(11)} = None")
            trops_env = 'default'
        try:
            print(f"  {'TROPS_SID'.ljust(11)} = {os.environ['TROPS_SID']}")
        except KeyError:
            print(f"  {'TROPS_SID'.ljust(11)} = None")

        if os.getenv('TROPS_TAGS'):
            print(f"  {'TROPS_TAGS'.ljust(11)} = { os.getenv('TROPS_TAGS') }")

        config = ConfigParser()
        config.read(self.trops_conf)
        print('Git')
        if config.has_option(trops_env, 'git_dir'):
            print(f"  {'git-dir'.ljust(11)} = { config.get(trops_env, 'git_dir') }")
        if config.has_option(trops_env, 'work_tree'):
            print(
                f"  {'work-tree'.ljust(11)} = { config.get(trops_env, 'work_tree') }")
        if config.has_option(trops_env, 'git_remote'):
            print(
                f"  {'git-remote'.ljust(11)} = { config.get(trops_env, 'git_remote') }")
        if config.has_option(trops_env, 'logfile'):
            print(f"  {'logfile'.ljust(11)} = { config.get(trops_env, 'logfile') }")
        else:
            print(f"  {'logfile'.ljust(11)} = $TROPS_DIR/log/trops.log")


def env_create(args, other_args):
    """Setup trops project"""

    trenv = TropsEnv(args, other_args)
    trenv.create()


def env_delete(args, other_args):
    """Setup trops project"""

    trenv = TropsEnv(args, other_args)
    trenv.delete()


def env_show(args, other_args):

    trenv = TropsEnv(args, other_args)
    trenv.show()


def env_update(args, other_args):

    trenv = TropsEnv(args, other_args)
    trenv.update()


def env_list(args, other_args):

    trenv = TropsEnv(args, other_args)
    trenv.list()


def add_env_subparsers(subparsers):

    # trops env
    parser_env = subparsers.add_parser(
        'env', help='initialize trops environment')
    env_subparsers = parser_env.add_subparsers()
    # trops env show
    perser_env_show = env_subparsers.add_parser(
        'show', help='show current environment')
    perser_env_show.set_defaults(handler=env_show)
    # trops env list
    perser_env_list = env_subparsers.add_parser(
        'list', help='show list of environment')
    perser_env_list.set_defaults(handler=env_list)
    # trops env create <env>
    parser_env_create = env_subparsers.add_parser(
        'create', help='create trops environment')
    parser_env_create.add_argument(
        '-w', '--work-tree', default='/', help='Set work-tree (default: %(default)s)')
    parser_env_create.add_argument(
        'env', help='Set environment name (default: %(default)s)')
    parser_env_create.add_argument(
        '--git-remote', help='Remote git repository')
    parser_env_create.add_argument(
        '--git-branch', help='Name of the git branch (*default=trops/<envname>)')
    parser_env_create.add_argument(
        '--logfile', help='Path of log file')
    parser_env_create.add_argument(
        '--tags', help='Tags (e.g. issue numbers)')
    parser_env_create.set_defaults(handler=env_create)
    # trops env delete <env>
    parser_env_delete = env_subparsers.add_parser(
        'delete', help='delete trops environment')
    parser_env_delete.add_argument(
        'env', help='Set environment name (default: %(default)s)')
    parser_env_delete.set_defaults(handler=env_delete)
    # trops env update
    parser_env_update = env_subparsers.add_parser(
        'update', help='update trops environment')
    parser_env_update.add_argument(
        'env', default=os.getenv('TROPS_ENV'), nargs='?', help='Set environment name (default: %(default)s)')
    parser_env_update.add_argument(
        '-w', '--work-tree', default='/', help='work-tree')
    parser_env_update.add_argument(
        '-g', '--git-dir', help='git-dir')
    parser_env_update.add_argument(
        '--git-remote', help='Remote git repository')
    parser_env_update.add_argument(
        '--logfile', help='Path of log file')
    parser_env_update.add_argument(
        '--tags', help='Tags (e.g. issue numbers)')
    parser_env_update.set_defaults(handler=env_update)
    # TODO: Add trops deactivate
