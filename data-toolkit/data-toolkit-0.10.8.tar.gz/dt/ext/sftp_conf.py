import os
import json

def get_sftp_path():
    '''
    Checks if SFTP config exists.
    '''
    cwd = os.getcwd()
    target_path = os.path.join(cwd, '.vscode/sftp.json')
    return target_path

def write_sftp(name: str, remote: str, ip: int,
                user: str, port: int, key_path: str):
    sftp_path = get_sftp_path()
    new_config = {
        "name": name,
        "host": ip,
        "protocol": "sftp",
        "port": port,
        "username": user,
        "remotePath": remote,
        "privateKeyPath" : key_path,
        "uploadOnSave": True,
        "watcher": {
            "files": "*.{py,.sh,.txt}"
        },
        "ignore": [
            ".vscode",
            "*.png",
            "*.jpg",
            "*.npy",
            ".git/", 
            "*.pt",
            "wandb/"
        ]
    }
    if not os.path.exists(sftp_path):
        os.mkdir(os.path.join(os.getcwd(), '.vscode'))
        # create sftp
        with open(sftp_path, 'w') as fp:
            fp.write(json.dumps(new_config).replace("'", ""))
        print(new_config)

    else:
        old_config = json.load(open(sftp_path, 'r'))
        # TODO: update values from new config
        config = {
            **new_config
        }
        with open(sftp_path, 'w') as fp:
            fp.write(json.dumps(new_config).replace("'", ""))
        print(new_config)
        
