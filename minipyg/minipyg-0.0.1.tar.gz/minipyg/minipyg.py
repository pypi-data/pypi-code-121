import argparse
import subprocess
import sys
import json


def install_package(package, version=None):
    if version or '==' in package:
        if '==' in package:
            version = package.split('==')[1]
            package = package.split('==')[0]
        print('Installing', package + ', version', version)
        subprocess.run(['python3', '-m', 'pip', 'install', package + '==' + version])
    else:
        print('Installing', package)
        subprocess.run(['python3', '-m', 'pip', 'install', package])
    print('Complete')


def delete_package(package):
    print('Uninstalling', package)
    subprocess.run(['python3', '-m', 'pip', 'uninstall', package, '-y'])
    print('Complete')


def update_reqs():
    actual_deps_dict = get_actual_deps()

    actual_deps = sorted(
        [key + '==' + actual_deps_dict[key] for key in actual_deps_dict]
    )

    with open('requirements.txt', 'w') as f:
        for dep in actual_deps:
            f.write(dep)


def get_actual_deps():
    pr = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE)
    actual_deps = list(
        map(
            lambda x: x.decode('utf-8'),
            filter(
                lambda x: len(x) > 0,
                pr.stdout.split(b'\n')
            )
        )
    )

    actual_deps_dict = {}

    for dep in actual_deps:
        _d = dep.split('==')
        if _d[0] != 'minipyg':
            actual_deps_dict[_d[0]] = _d[1]

    return actual_deps_dict


def get_incoming_deps():
    incoming_deps_dict = {}

    with open('requirements.txt') as f:
        for line in f.readlines():
            _d = line.split('==')
            if _d[0] != 'minipyg':
                incoming_deps_dict[_d[0]] = _d[1]

    return incoming_deps_dict


def entry():
    parser = argparse.ArgumentParser(prog='minipyg')
    parser.add_argument('command', nargs='*', help='run, update, install or uninstall')

    args = parser.parse_args()

    if len(args.command) == 0:
        print('Please, choose the action: run, update, install or uninstall, or configure your own one in minipyg.json (`commands` section).')
        return

    if args.command[0] == 'install':
        if len(args.command) == 1:
            print('Nothing to install!')
            return

        install_package(args.command[1])
        update_reqs()

    if args.command[0] == 'uninstall':
        if len(args.command) == 1:
            print('Nothing to uninstall!')
            return
        delete_package(args.command[1])
        update_reqs()

    if args.command[0] in ('update', 'run'):

        if sys.prefix != sys.base_prefix:

            actual_deps_dict = get_actual_deps()
            incoming_deps_dict = get_incoming_deps()

            # checking package addition/changing
            for item in incoming_deps_dict:
                # changing
                if item in actual_deps_dict:
                    if incoming_deps_dict[item] != actual_deps_dict[item]:
                        delete_package(item)
                        install_package(item, incoming_deps_dict[item])

                # addition
                else:
                    install_package(item, incoming_deps_dict[item])

            # checking deletion
            for item in actual_deps_dict:
                if item not in incoming_deps_dict:
                    if item != 'minipyg':
                        delete_package(item)

        else:
            print('You are outside of the venv. Please activate it via `source venv/bin/activate` command.')

    if args.command[0] == 'run':
        with open('minipyg.json') as f:
            d = json.load(f)
            if 'run' in d['commands']:
                subprocess.run(d['commands']['run'].split())

    if args.command[0] not in ('install', 'uninstall', 'update', 'run'):
        with open('minipyg.json') as f:
            d = json.load(f)
            if args.command[0] in d['commands']:
                subprocess.run(d['commands'][args.command[0]].split())
            else:
                print('Unknown command!')
                return
