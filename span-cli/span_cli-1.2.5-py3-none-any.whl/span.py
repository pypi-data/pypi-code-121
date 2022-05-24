from getpass import getpass
from json import dump, load
from os import chdir, makedirs
from os.path import dirname, exists
from requests import get, post, delete
from time import sleep
import readline
from rich.console import Console
from rich.table import Column, Table
from .properties import files
from .setup import setup

chdir(dirname(__file__))
default = {'history': '', 'instances': '[]', 'key': '', 'account': '{}'}
for file in default:
    if not exists(files[file]):
        makedirs(dirname(files[file]), exist_ok=True)
        with open(files[file], 'w') as f:
            f.write(default[file])
readline.read_history_file(files['history'])
with open(files['key'], 'r') as f:
    api_key = f.read()


def cli():
    pass


def set_api_key():
    global api_key
    while 1:
        tmp = getpass('API Key: ')
        test = get('https://api.vultr.com/v2/account', headers={'Authorization': 'Bearer %s' % tmp})
        if test.status_code == 200:
            api_key = tmp
            break
        print('Error: %s' % test.json()['error'])
    with open(files['key'], 'w') as f:
        f.write(api_key)


def set_username(username):
    with open(files['account'], 'r') as f:
        original = load(f)
    original.update({'username': username})
    with open(files['account'], 'w') as f:
        dump(original, f)


def set_password():
    while 1:
        tmp = getpass('Password: ')
        if tmp == '':
            print('Error: Password cannot be empty.')
            continue
        if tmp == getpass('Confirm Password: '):
            break
        print('Error: Passwords do not match.')
    with open(files['account'], 'r') as f:
        original = load(f)
    original.update({'password': tmp})
    with open(files['account'], 'w') as f:
        dump(original, f)


def regions():
    lst = []
    cursor = ''
    params = {'per_page': 500}
    while 1:
        if cursor != '':
            params['cursor'] = cursor
        page = get('https://api.vultr.com/v2/regions', params).json()
        for region in page['regions']:
            lst.append(list(region.values())[:-1])
        if page['meta']['links']['next'] == '':
            break
        cursor = page['meta']['links']['next']
    return lst


def plans():
    lst = []
    cursor = ''
    params = {'per_page': 500, 'type': 'vhp'}
    region_ids = {i[0] for i in regions}
    while 1:
        if cursor != '':
            params['cursor'] = cursor
        page = get('https://api.vultr.com/v2/plans', params).json()
        for plan in page['plans']:
            lst.append([plan['id'], str(plan['bandwidth']), str(plan['monthly_cost']), ', '.join(region_ids - set(plan['locations']))])
        if page['meta']['links']['next'] == '':
            break
        cursor = page['meta']['links']['next']
    return lst


def create_instance(name, region, plan):
    with open(files['instances'], 'r') as f:
        for instance in load(f):
            if instance['n'] == name:
                print('Error: Instance with name "%s" already exists.' % name)
                return
    data = {'region': region, 'plan': plan, 'os_id': 381, 'label': 'Span Instance'}
    instance = post('https://api.vultr.com/v2/instances', json=data, headers={'Authorization': 'Bearer %s' % api_key})
    if instance.status_code != 202:
        print('Error: %s' % instance.json()['error'])
        return
    instance = instance.json()['instance']
    password = instance['default_password']
    for plan in plans:
        if plan[0] == instance['plan']:
            cost = plan[2]
            break
    while 1:
        instance = get('https://api.vultr.com/v2/instances/%s' % instance['id'], headers={'Authorization': 'Bearer %s' % api_key}).json()['instance']
        if instance['status'] == 'active':
            break
        sleep(1)
    instance = {'id': instance['id'], 'n': name, 'ip': instance['main_ip'], 'r': instance['region'], 'pwd': password, 'd': instance['date_created'], 'b': str(instance['allowed_bandwidth']), 'c': str(cost)}
    with open(files['instances'], 'r') as f:
        original = load(f)
    original.append(instance)
    with open(files['instances'], 'w') as f:
        dump(original, f)
    return instance


def list_instances():
    with open(files['instances'], 'r') as f:
        instances = load(f)
    if instances == []:
        print("You haven't created any instances yet.")
        return
    table = Table('Name', Column('IP', no_wrap=True), 'Region', 'Date Created', 'BW/GB·mo⁻¹', 'Cost/$·mo⁻¹', highlight=True)
    for instance in instances:
        table.add_row(instance['n'], instance['ip'], instance['r'], instance['d'], instance['b'], instance['c'])
    console.print(table)


def get_info(name, output):
    with open(files['instances'], 'r') as f:
        instances = load(f)
    for instance in instances:
        if instance['n'] == name:
            if output:
                table = Table('Name', Column('IP', no_wrap=True), 'Region', 'Date Created', 'BW/GB·mo⁻¹', 'Cost/$·mo⁻¹', highlight=True)
                table.add_row(instance['n'], instance['ip'], instance['r'], instance['d'], instance['b'], instance['c'])
                console.print(table)
            return instance
    print('Error: Instance with name "%s" does not exist.' % name)


def delete_instance(name):
    id = ''
    with open(files['instances'], 'r') as f:
        instances = load(f)
    for instance in instances:
        if instance['n'] == name:
            id = instance['id']
            break
    if id == '':
        print('Error: Instance with name "%s" does not exist.' % name)
        return
    rq = delete('https://api.vultr.com/v2/instances/%s' % id, headers={'Authorization': 'Bearer %s' % api_key})
    if rq.status_code != 204:
        print('Error: %s' % rq.json()['error'])
    else:
        instances.remove(instance)
        with open(files['instances'], 'w') as f:
            dump(instances, f)


def get_regions():
    global regions, regions_df
    if type(regions) != list:
        print('Fetching regions...')
        regions = regions()
        regions_df = Table(Column('ID', no_wrap=True), 'City', 'Country', 'Continent')
        for region in regions:
            regions_df.add_row(*region)

def get_plans():
    global plans, plans_df
    if type(plans) != list:
        print('Fetching plans...')
        plans = plans()
        plans_df = Table(Column('ID', no_wrap=True), Column('Bandwidth/GB·mo⁻¹', justify='right'), Column('Cost/$·mo⁻¹', justify='right'), 'Excluded Regions', highlight=True)
        for plan in plans:
            plans_df.add_row(*plan)


console = Console()
while 1:
    try:
        cmd = input('span\033[32m$\033[0m ').split()
        cmd[0] = cmd[0].lower()
        readline.write_history_file(files['history'])
        if cmd == []:
            continue
        if cmd[0] == 'regions':
            get_regions()
            console.print(regions_df)
        elif cmd[0] == 'plans':
            get_regions()
            get_plans()
            console.print(plans_df)
        elif cmd[0] == 'create':
            if api_key == '':
                set_api_key()
            if len(cmd) != 4:
                print('Usage: create <name> <region> <plan>')
            else:
                get_regions()
                get_plans()
                print('Creating instance...')
                instance = create_instance(*cmd[1:])
                if instance != None:
                    print('Instance created. IPv4 address: %s' % instance['ip'])
                    setup(instance)
        elif cmd[0] == 'setup':
            if len(cmd) != 2:
                print('Usage: setup <name>')
            else:
                instance = get_info(cmd[1], False)
                if instance != None:
                    setup(instance)
        elif cmd[0] == 'key':
            set_api_key()
        elif cmd[0] == 'user':
            if len(cmd) != 2:
                print('Usage: user <username>')
            else:
                set_username(cmd[1])
        elif cmd[0] == 'pwd':
            set_password()
        elif cmd[0] == 'ls':
            list_instances()
        elif cmd[0] == 'info':
            if len(cmd) != 2:
                print('Usage: info <name>')
            else:
                get_info(cmd[1], True)
        elif cmd[0] == 'del':
            if len(cmd) != 2:
                print('Usage: del <name>')
            else:
                delete_instance(cmd[1])
        elif cmd[0] == 'help':
            print('''\
Usage:
    key                               Set API key.
    user <username>                   Set username for VPN connection.
    pwd                               Set password for VPN connection.
    regions                           List all regions.
    plans                             List all plans.
    create <name> <region> <plan>     Create and setup a new instance.
    setup <name>                      Setup an existing instance.
    ls                                List all instances.
    info <name>                       Get information about an instance.
    del <name>                        Delete an instance.
    help                              Show this message.''')
        elif cmd[0] == 'exit':
            break
        else:
            print('Error: Unknown command "%s"' % cmd[0])
    except EOFError:
        print()
        break
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print('\033[31mError:\033[0m', e)
