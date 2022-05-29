from typing import Dict, Union, List
import os
import colorama
import logging
import tempfile
import json
import shutil
import subprocess
from urllib import request
import zipfile
import tarfile
import argparse
import filecmp
import difflib


# logger
colorama.init()
class CustomFormatter(logging.Formatter):

    log_colors = {
        'DEBUG'  : colorama.Fore.BLUE,
        'INFO'   : colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR'  : colorama.Fore.RED
    }

    log_levels = {
        'DEBUG': 'DEBUG',
        'INFO': 'INFO ',
        'WARNING': 'WARN ',
        'ERROR': 'ERROR'
    }

    def __init__(self, color: bool = False):
        self.color = color
        if color:
            fmt = f'%(log_color)s[%(log_level)s]{colorama.Style.RESET_ALL} %(message)s'
        else:
            fmt = '[%(log_level)s] %(message)s'
        super().__init__(fmt=fmt)

    def format(self, record: logging.LogRecord) -> str:
        if self.color:
            record.__dict__['log_color'] = self.log_colors[record.levelname]
        record.__dict__['log_level'] = self.log_levels[record.levelname]
        return super().format(record)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(CustomFormatter(True))

log_file = os.path.join(tempfile.gettempdir(), 'homeman.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(CustomFormatter())

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


# homeman
class HomeManException(Exception):
    '''homeman exception'''
    pass


def path_exists(path: str):
    if os.path.islink(path):
        raise HomeManException(f'occur link: {path}')
    return os.path.exists(path)


def path_remove(path: str, clear: bool = False):
    if os.path.islink(path):
        raise HomeManException(f'occur link: {path}')
    elif os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        raise HomeManException(f'cannot remove: {path}')
    if clear:
        os.makedirs(path)
        os.removedirs(path)


def path_make_space(path: str):
    try:
        os.makedirs(path)
    except:
        raise HomeManException(f'cannot make space for: {path}')
    else:
        os.rmdir(path)


def path_move(path1: str, path2: str):
    shutil.move(path1, path2)


def path_copy(path1: str, path2: str):
    if os.path.islink(path1):
        raise HomeManException(f'occur link: {path1}')
    if os.path.isfile(path1):
        shutil.copy(path1, path2)
    elif os.path.isdir(path1):
        shutil.copytree(path1, path2)
    else:
        raise HomeManException(f'cannot copy: {path1}')


class HomeMan:
    '''homeman operations'''

    def __enter__(self):
        '''prepare'''
        self.usr_home = os.path.expanduser('~')
        self.man_home = os.getenv('MAN_HOME', os.path.join(self.usr_home, '.manhome'))

        # check man_home
        if self.man_home != os.path.realpath(self.man_home):
            raise HomeManException(f'home directory is not a real path: {self.man_home}')
        if not os.path.isdir(self.man_home):
            try:
                os.makedirs(self.man_home)
            except:
                raise HomeManException(f'cannot create home directory: {self.man_home}')
        
        # check man_json
        self.man_json = os.path.join(self.man_home, 'homeman.json')
        if not os.path.isfile(self.man_json):
            with open(self.man_json, 'w') as f:
                f.write('{}')

        # avoid repeatly run this scripts
        self.lock_file = os.path.join(tempfile.gettempdir(), 'homeman.lock')
        try:
            # create the lock file
            with open(self.lock_file, 'x'):
                pass
        except:
            raise HomeManException('acquire lock failed, another script is running')
        else:
            logger.debug('acquire lock')

        # load man_json
        with open(self.man_json, 'r') as f:
            self.data: Dict = json.load(f)
            logger.debug('load data')
        return self
    
    def __mark_data_changed(self):
        '''mark the data, and indicate that data need save when exit'''
        self.data['homeman_changed'] = True
    
    def __exit__(self, t, e, tb):
        '''post handle'''
        if e is None:
            if 'homeman_changed' in self.data.keys():
                # delete the mark
                del self.data['homeman_changed']
                # tidy the data and delete the empty node
                self.__tidy_data()
                # save the data
                with open(self.man_json, 'w') as f:
                    json.dump(self.data, f, indent=2)
                    logger.debug('save data')
        
        # delete the lock file
        os.remove(self.lock_file)
        logger.debug('release lock')

    def get_route(self, path: str) -> str:
        '''transfor path to route'''

        # get absolute path
        path = os.path.abspath(path)

        # extract route from path
        if path == self.man_home or path == self.usr_home:
            route = ''
        elif path.startswith(self.man_home + os.path.sep):
            route = path[len(self.man_home):]
        elif path.startswith(self.usr_home + os.path.sep):
            route = path[len(self.usr_home):]
        else:
            raise HomeManException(f'path illegal: {path}')
        
        # check the route
        if 'homeman' in route:
            raise HomeManException(f'route illegal: {route}')
        logger.debug('route: %s', route)
        return route

    def get_data(self, route: str, force: bool = False) -> Union[Dict, None]:
        '''get corresponding data by route, if force is true, create empty data if not exists'''

        # assign root data and make through...
        cur_data: Dict = self.data
        for name in route.split(os.path.sep)[1:]:
            if 'homeman' in cur_data.keys():
                # cannot make through if 'homeman' exists
                return
            if name not in cur_data.keys():
                if force:
                    cur_data[name] = {}
                else:
                    return
            # make through
            cur_data: Dict = cur_data[name]
        return cur_data

    def __scan_data(self, data: Dict, tag: Union[str, None] = None) -> List[Dict]:
        '''scan some data that contains 'homeman' key'''

        if 'homeman' in data.keys():
            if tag is None:
                return [data]
            elif 'tags' not in data.keys():
                return []
            elif tag in data['tags']:
                return [data]
            else:
                return []
        else:
            d_list = []
            for key in data.keys():
                d_list += self.__scan_data(data[key], tag)
            return d_list

    def __tidy_data(self):
        '''tidy data from root data'''
        self.__do_tidy_data(self.data)

    def __do_tidy_data(self, d: Dict[str, Dict]) -> bool:
        '''tidy data recursively, and return true if current data is empty'''
        flag = True
        empty_keys = []
        for key in d.keys():
            dd = d[key]
            if len(dd.keys()) != 0:
                if 'homeman' in dd.keys():
                    flag = False
                else:
                    if self.__do_tidy_data(dd):
                        empty_keys.append(key)
                    else:
                        flag = False
            else:
                empty_keys.append(key)
        for key in empty_keys:
            del d[key]
        return flag
    
    def add(self, route: str, meta: Dict):
        '''add a route into home'''

        logger.debug('========< add >========')
        if route == '':
            raise HomeManException('cannot add home itself')
        data = self.get_data(route, True)
        if data is None or len(data.keys()) != 0:
            raise HomeManException(f'conflict occur: {route}')
        
        # 'homeman' mark this data is a special data
        data['homeman'] = route

        # assign meta
        for key in meta.keys():
            if key == 'auto':
                # 'auto' is a special key, indicate auto sync
                auto: List[str] = meta['auto']
                new_auto: List[str] = []
                # check each item in 'auto'
                for auto_route in auto:
                    auto_data = self.get_data(auto_route)
                    if auto_data is None or 'homeman' not in auto_data.keys():
                        # not a special data
                        continue
                    
                    # 'auto' is paired
                    if 'auto' not in auto_data.keys():
                        auto_data['auto'] = []
                    auto_data['auto'].append(route)

                    new_auto.append(auto_route)

                if len(new_auto) != 0:
                    data['auto'] = new_auto

            data[key] = meta[key]

        logger.info('add: %s', route)
        self.__mark_data_changed()

        # try to fill
        try:
            if 'url' in meta.keys():
                # this is a remote source
                self.__pull(data, True)
            else:
                # this is a local source
                self.__sync(data, True)
        except HomeManException as e:
            logger.warning(e)

    def remove(self, route: str, tag: Union[str, None] = None):
        '''remove a route, may contains multi special route'''

        logger.debug('========< remove >========')
        data = self.get_data(route)
        if data is None:
            logger.debug('route not exists: %s', route)
            return

        for homeman_data in self.__scan_data(data, tag):
            try:
                self.__remove(homeman_data)
            except HomeManException as e:
                logger.warning(e)

    def __remove(self, data: Dict):
        # restore first
        self.__restore(data)

        route = data['homeman']
        # remove inside path
        man_path = self.man_home + route
        path_remove(man_path, True)
        # clear 'auto' if present
        if 'auto' in data.keys():
            for auto_route in data['auto']:
                auto_route['auto'].remove(route)
        data.clear()
        self.__mark_data_changed()
        logger.info('remove: %s', route)

    def pull(self, route: str, force: bool = False, tag: Union[str, None] = None):
        '''pull remote resource'''

        logger.debug('========< pull >========')
        data = self.get_data(route)
        if data is None:
            logger.debug('route not exists: %s', route)
            return

        for homeman_data in self.__scan_data(data, tag):
            try:
                self.__pull(homeman_data, force)
            except HomeManException as e:
                logger.warning(e)
    
    def __pull(self, data: Dict, force: bool = False):
        if 'url' not in data.keys():
            return
        route = data['homeman']
        man_path = self.man_home + route
        if not force and path_exists(man_path):
            return
        url = data['url']
        with tempfile.TemporaryDirectory() as tempdir:
            temp_node = os.path.join(tempdir, 'node')
            if url.endswith('.git'):
                cmd = ['git', 'clone', '--depth', '1']
                if 'branch' in data.keys():
                    cmd.append('--branch')
                    cmd.append(data['branch'])
                cmd.append(url)
                cmd.append(temp_node)
                returncode = subprocess.call(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if returncode != 0:
                    raise HomeManException(f'cannot clone git repo: {url}')
                else:
                    shutil.rmtree(os.path.join(temp_node, '.git'))
            else:
                try:
                    request.urlretrieve(url, filename=temp_node)
                except:
                    raise HomeManException(f'cannot download url: {url}')
                if url.endswith('.zip'):
                    shutil.move(temp_node, temp_node + '.zip')
                    try:
                        with zipfile.ZipFile(temp_node + '.zip') as z:
                            z.extractall(temp_node)
                    except:
                        raise HomeManException(f'cannot extract zip from url: {url}')
                elif url.endswith('.tar') or \
                        url.endswith('.tar.gz') or url.endswith('.tgz') or \
                        url.endswith('.tar.bz2') or url.endswith('.tbz2') or \
                        url.endswith('.tar.xz') or url.endswith('.txz'):
                    shutil.move(temp_node, temp_node + '.tarfile')
                    try:
                        with tarfile.open(temp_node + '.tarfile') as t:
                            t.extractall(temp_node)
                    except:
                        raise HomeManException(f'cannot extract tar from url: {url}')
            path_remove(man_path, False)
            path_make_space(man_path)
            path_move(temp_node, man_path)
            data['mode'] = bin(os.stat(man_path).st_mode)
            self.__mark_data_changed()
            logger.info('pull: %s', route)
            self.__sync(data, False)
            self.__auto_sync(data, [route])

    def sync(self, route: str, reverse: bool = False, tag: Union[str, None] = None):
        '''keep sync between two home'''

        logger.debug('========< sync >========')
        data = self.get_data(route)
        if data is None:
            logger.debug('route not exists: %s', route)
            return

        for homeman_data in self.__scan_data(data, tag):
            try:
                self.__sync(homeman_data, reverse)
            except HomeManException as e:
                logger.warning(e)
    
    def __sync(self, data: Dict, reverse: bool = False):
        route = data['homeman']
        usr_path = self.usr_home + route
        man_path = self.man_home + route
        if reverse:
            if not path_exists(usr_path):
                raise HomeManException(f'not exists: {usr_path}')
            self.__backup(data, False)
            path_remove(man_path, False)
            path_make_space(man_path)
            path_copy(usr_path, man_path)
            data['mode'] = bin(os.stat(man_path).st_mode)
            self.__mark_data_changed()
            logger.info('sync reversely: %s', route)
            self.__auto_sync(data, [route])
        else:
            if not path_exists(man_path):
                raise HomeManException(f'not exists: {man_path}')
            self.__backup(data, False)
            path_remove(usr_path)
            path_make_space(usr_path)
            path_copy(man_path, usr_path)
            os.chmod(usr_path, int(data['mode'], 2))
            logger.info('sync: %s', route)

    def __auto_sync(self, data: Dict, global_routes: List[str]):
        if 'auto' not in data.keys():
            return
        route = data['homeman']
        man_path = self.man_home + route
        for slave_route in data['auto']:
            if slave_route in global_routes:
                continue
            global_routes.append(slave_route)
            slave_data = self.get_data(slave_route)
            if slave_data is None or 'homeman' not in slave_data.keys():
                continue
            slave_man_path = self.man_home + slave_data['homeman']
            path_remove(slave_man_path, False)
            path_make_space(slave_man_path)
            path_copy(man_path, slave_man_path)
            slave_data['mode'] = bin(os.stat(slave_man_path).st_mode)
            self.__mark_data_changed()
            logger.info('auto sync: %s', slave_route)
            self.__sync(slave_data, False)
            self.__auto_sync(slave_data, global_routes)

    def backup(self, route: str, force: bool = False, tag: Union[str, None] = None):
        '''backup outside node'''

        logger.debug('========< backup >========')
        data = self.get_data(route)
        if data is None:
            logger.debug('route not exists: %s', route)
            return

        for homeman_data in self.__scan_data(data, tag):
            try:
                self.__backup(homeman_data, force)
            except HomeManException as e:
                logger.warning(e)
    
    def __backup(self, data: Dict, force: bool = False):
        route = data['homeman']
        usr_path = self.usr_home + route
        usr_path_bak = usr_path + '.homeman.bak'
        usr_path_bak2 = usr_path_bak + '.empty'
        if not force and (path_exists(usr_path_bak) or path_exists(usr_path_bak2)):
            return
        if path_exists(usr_path):
            path_remove(usr_path_bak)
            path_remove(usr_path_bak2)
            path_copy(usr_path, usr_path_bak)
        else:
            path_make_space(usr_path)
            with open(usr_path_bak2, 'w'):
                pass
        logger.info('backup: %s', route)

    def restore(self, route: str, tag: Union[str, None] = None):
        '''restore outside node'''

        logger.debug('========< restore >========')
        data = self.get_data(route)
        if data is None:
            logger.debug('route not exists: %s', route)
            return

        for homeman_data in self.__scan_data(data, tag):
            try:
                self.__restore(homeman_data)
            except HomeManException as e:
                logger.warning(e)
    
    def __restore(self, data: Dict):
        route = data['homeman']
        usr_path = self.usr_home + route
        usr_path_bak = usr_path + '.homeman.bak'
        usr_path_bak2 = usr_path_bak + '.empty'
        if not path_exists(usr_path_bak) and not path_exists(usr_path_bak2):
            return
        path_remove(usr_path)
        if path_exists(usr_path_bak):
            path_move(usr_path_bak, usr_path)
        else:
            path_remove(usr_path_bak2, True)
        logger.info('restore: %s', route)

    def check(self, route: str, show_diff: bool, tag: Union[str, None] = None):
        logger.debug('========< check >========')
        data = self.get_data(route)
        if data is None:
            logger.debug('route not exists: %s', route)
            return

        for homeman_data in self.__scan_data(data, tag):
            try:
                self.__check(homeman_data, show_diff)
            except HomeManException as e:
                logger.warning(e)
    
    def __check(self, data: Dict, show_diff: bool):
        route = data['homeman']
        usr_path = self.usr_home + route
        usr_path_bak = usr_path + '.homeman.bak'
        usr_path_bak2 = usr_path_bak + '.empty'
        if not path_exists(usr_path_bak) and not path_exists(usr_path_bak2):
            logger.warning('not backup: %s', route)
        else:
            man_path = self.man_home + route
            if not path_exists(man_path):
                logger.warning('not exists inside: %s', route)
            elif not path_exists(usr_path):
                logger.warning('not exists outside: %s', route)
            else:
                diff_files = []
                if os.path.isfile(usr_path) and os.path.isfile(man_path):
                    if not filecmp.cmp(usr_path, man_path):
                        diff_files.append(route)
                elif os.path.isdir(usr_path) and os.path.isdir(man_path):
                    def collect_diff_files(dcmp, dfs: List[str]):
                        for name in dcmp.diff_files:
                            dfs.append(dcmp.left[len(self.usr_home):] + os.path.sep + name)
                        for sub_dcmp in dcmp.subdirs.values():
                            collect_diff_files(sub_dcmp, dfs)
                    collect_diff_files(filecmp.dircmp(usr_path, man_path), diff_files)
                if len(diff_files) == 0:
                    logger.info('sync: %s', route)
                else:
                    logger.warning('no sync: %s', route)
                    if show_diff:
                        differ = difflib.Differ()
                        for f in diff_files:
                            print(f'[{f}]')
                            usr_f = self.usr_home + f
                            man_f = self.man_home + f
                            if not os.path.exists(usr_f):
                                print('not exists outside')
                            elif not os.path.exists(man_f):
                                print('not exists inside')
                            elif os.path.isdir(usr_f):
                                print('is dir outside')
                            elif os.path.isdir(man_f):
                                print('is dir inside')
                            else:
                                with open(usr_f, 'r') as uf, open(man_f, 'r') as mf:
                                    if 'formatter' in data.keys():
                                        formatter = data['formatter']
                                        if formatter == 'json':
                                            ulines = json.dumps(
                                                json.load(uf), indent=2
                                            ).splitlines(keepends=True)
                                            mlines = json.dumps(
                                                json.load(mf), indent=2
                                            ).splitlines(keepends=True)
                                        else:
                                            raise HomeManException(f'unknown formatter: {formatter}')
                                    else:
                                        ulines = uf.readlines()
                                        mlines = mf.readlines()
                                    res = ['------ start ------\n']
                                    res.extend(list(differ.compare(ulines, mlines)))
                                    res.append('------ end ------\n')
                                    common_counter = 0
                                    last_line = '\n'
                                    for line in res:
                                        if line.startswith('  '):
                                            common_counter += 1
                                            last_line = line
                                        else:
                                            if common_counter != 0:
                                                if common_counter == 1:
                                                    print(last_line, end='')
                                                else:
                                                    print(f'------ {common_counter} common lines ------')
                                            print(line, end='')
                                            common_counter = 0


def main():
    homeman_parse = argparse.ArgumentParser(
        prog='homeman',
        description='a small management tool to keep files synchronized between user home and your special home directory.'
    )

    homeman_parse.add_argument(
        '-d', '--debug', action='store_true',
        help='set the console log level to DEBUG'
    )
    homeman_parse.add_argument(
        '-i', '--info', action='store_true',
        help='set the console log level to INFO'
    )
    homeman_parse.add_argument(
        '-w', '--warn', action='store_true',
        help='set the console log level to WARNING'
    )
    homeman_parse.add_argument(
        '-e', '--error', action='store_true',
        help='set the console log level to ERROR'
    )
    homeman_parse.add_argument(
        '-q', '--quit', action='store_true',
        help='DO NOT print console log'
    )

    homeman_commands = homeman_parse.add_subparsers(dest='command')

    # add
    command_add = homeman_commands.add_parser(
        'add', help='add a resource to homeman'
    )
    command_add.add_argument(
        'path', type=str,
        help='the location of resource'
    )
    command_add.add_argument(
        '-u', '--url', type=str,
        help='special a remote resource'
    )
    command_add.add_argument(
        '-b', '--branch', type=str,
        help='special the branch name when resource type is git'
    )
    command_add.add_argument(
        '-f', '--formatter', type=str, choices=['none', 'json'], default='none',
        help='formatter the content'
    )
    command_add.add_argument(
        '-a', '--auto', nargs='*', default=[],
        help='auto sync'
    )
    command_add.add_argument(
        '--tags', nargs='*', default=[],
        help='filter node'
    )

    # pull
    command_pull = homeman_commands.add_parser(
        'pull', help='load a resource'
    )
    command_pull.add_argument(
        'path', type=str,
        help='the location of resource'
    )
    command_pull.add_argument(
        '-f', '--force', action='store_true',
        help='set the console log level to DEBUG'
    )
    command_pull.add_argument(
        '-t', '--tag', type=str, default=None,
        help='filter node'
    )

    # remove
    command_remove = homeman_commands.add_parser(
        'remove', help='remove a resource'
    )
    command_remove.add_argument(
        'path', type=str,
        help='the location of resource'
    )
    command_remove.add_argument(
        '-t', '--tag', type=str, default=None,
        help='filter node'
    )

    # sync
    command_sync = homeman_commands.add_parser(
        'sync', help='list a resource'
    )
    command_sync.add_argument(
        'path', type=str,
        help='the location of resource'
    )
    command_sync.add_argument(
        '-v', '--reverse', action='store_true',
        help='set the console log level to DEBUG'
    )
    command_sync.add_argument(
        '-t', '--tag', type=str, default=None,
        help='filter node'
    )

    # backup
    command_backup = homeman_commands.add_parser(
        'backup', help='list a resource'
    )
    command_backup.add_argument(
        'path', type=str,
        help='the location of resource'
    )
    command_backup.add_argument(
        '-f', '--force', action='store_true',
        help='set the console log level to DEBUG'
    )
    command_backup.add_argument(
        '-t', '--tag', type=str, default=None,
        help='filter node'
    )

    # restore
    command_restore = homeman_commands.add_parser(
        'restore', help='list a resource'
    )
    command_restore.add_argument(
        'path', type=str,
        help='the location of resource'
    )
    command_restore.add_argument(
        '-t', '--tag', type=str, default=None,
        help='filter node'
    )

    # check
    command_check = homeman_commands.add_parser(
        'check', help='list a resource'
    )
    command_check.add_argument(
        'path', type=str,
        help='the location of resource'
    )
    command_check.add_argument(
        '-v', '--show', action='store_true',
        help='show diff'
    )
    command_check.add_argument(
        '-t', '--tag', type=str, default=None,
        help='filter node'
    )

    args = homeman_parse.parse_args()

    if args.quit:
        console_handler.setLevel(logging.CRITICAL)
    elif args.error:
        console_handler.setLevel(logging.ERROR)
    elif args.warn:
        console_handler.setLevel(logging.WARNING)
    elif args.info:
        console_handler.setLevel(logging.INFO)
    elif args.debug:
        console_handler.setLevel(logging.DEBUG)

    try:
        with HomeMan() as hm:
            route = hm.get_route(args.path)
            if args.command == 'add':
                meta = {}
                if args.url:
                    meta['url'] = args.url
                    if args.branch:
                        meta['branch'] = args.branch
                if args.formatter != 'none':
                    meta['formatter'] = args.formatter
                if len(args.auto) != 0:
                    for i, e in enumerate(args.auto):
                        args.auto[i] = hm.get_route(e)
                    meta['auto'] = args.auto
                if len(args.tags) != 0:
                    meta['tags'] = args.tags
                hm.add(route, meta)
            elif args.command == 'remove':
                hm.remove(route, args.tag)
            elif args.command == 'pull':
                hm.pull(route, args.force, args.tag)
            elif args.command == 'sync':
                hm.sync(route, args.reverse, args.tag)
            elif args.command == 'backup':
                hm.backup(route, args.force, args.tag)
            elif args.command == 'restore':
                hm.restore(route, args.tag)
            elif args.command == 'check':
                hm.check(route, args.show, args.tag)
    except HomeManException as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.exception(e)
        return 2
    else:
        return 0
