from json import load
from os import remove
from paramiko import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import NoValidConnectionsError
from scp import SCPClient
from socket import timeout
from .properties import files

def setup(instance):
    from random import choice
    with open(files['account'], 'r') as f:
        account = load(f)
    user = account['username']
    passwd = account['password']
    dict_ = list('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890')
    psk = ''
    for i in range(64):
        psk += choice(dict_)
    with open('ipsec.secrets.sample') as f:
        with open('span.data/ipsec.secrets', 'w') as g:
            g.write(f.read().replace('$psk', psk).replace('$passwd', passwd).replace('$user', user))
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    host = instance['ip']
    user = 'root'
    port = 22
    print('It may take a few minutes for the instance to get ready for further operations...')
    while 1:
        try:
            ssh.connect(host, port, user, instance['pwd'], timeout=3)
            break
        except (timeout, NoValidConnectionsError):
            pass
    print('Executing setup script...')
    scp = SCPClient(ssh.get_transport())
    scp.put('span.data', '.', True)
    remove('span.data/ipsec.secrets')
    ssh.exec_command('cd span.data ; chmod 755 -R . ; ./setup > setup.log 2>&1')
    ssh.close()
