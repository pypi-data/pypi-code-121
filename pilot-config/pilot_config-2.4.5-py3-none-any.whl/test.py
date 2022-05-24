import paramiko
#import base64

client = paramiko.SSHClient()
client.load_system_node_keys()
client.set_missing_node_key_policy(paramiko.WarningPolicy())

client.connect('192.168.101.85', username='pi', password='raspberry')
#stdin, stdout, stderr = client.exec_command('cat /proc/pilot/module3/eeprom/fid')
stdin, stdout, stderr = client.exec_command('uname -a')
output = ''.join(stdout)
print(output)

chan = client.get_transport().open_session()
chan.exec_command('uuname -a')
print ("exit status: {}".format(chan.recv_exit_status()))

client.close()
