from platform import system as system_name  # Returns the system/OS name
from os import system as system_call  # Execute a shell command


# 下载中心redis
DOWNLOADER_CENTER_REDIS = {
    'outer': {
        'host': '115.159.3.51',
        'port': 53189,
        'db': 0,
        'password': '&redisd0o#2@1951'
    },
    'inner': {
        'host': '10.154.199.106',
        'port': 53189,
        'db': 0,
        'password': '&redisd0o#2@1951'
    }
}


def ping(ip):
    try:
        parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"
        return system_call("ping " + parameters + " " + ip + " > log.txt") == 0
    except:
        return False

if ping(DOWNLOADER_CENTER_REDIS['inner']['host']):
    ENVIR = 'inner'
else:
    ENVIR = 'outer'
