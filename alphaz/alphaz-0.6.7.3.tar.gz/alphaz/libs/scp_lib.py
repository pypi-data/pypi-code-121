import paramiko
import scpclient

def scp_to_server(file_path,host, username,password=None,copy=False):
    """ Securely copy the file to the server. """
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    #ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
    ssh_client.connect(host, username=username, password=password,port=22)

    if not copy: return

    with scpclient.closing(scpclient.Write(ssh_client.get_transport(), "~/")) as scp:
        scp.send_file(file_path, remote_filename="/data/elk/workstream_dbms_logs/from_ws/test.BIN")