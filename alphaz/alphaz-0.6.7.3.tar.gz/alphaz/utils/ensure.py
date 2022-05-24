import subprocess, os, psutil, logging
from logging.handlers import TimedRotatingFileHandler

from core import core

LOG = core.get_logger('ensure')

screens = {
    'telegram_dev': {
        'active':    True,
        'name':      'SRC_TELEGRAM_DEV',
        'dir':       '/home/truegolliath/svntools/GolliathPrivate',
        'shell_cmd': './telegram.sh'
    },
    'telegram_prod': {
        'active':   True,
        'name':      'SCR_TELEGRAM_PROD',
        'dir':       '/home/truegolliath/prodIO/GolliathPrivate',
        'shell_cmd': './telegram.sh'
    },
    'telegram_public_dev': {
        'active':    False,
        'name':      'SCR_TELEGRAM_PUBLIC_DEV',
        'dir':       '/home/truegolliath/svntools/GolliathPrivate',
        'shell_cmd': './telegram_public.sh'
    },
    'telegram_public_prod': {
        'active':   True,
        'name':      'SCR_TELEGRAM_PUBLIC',
        'dir':       '/home/truegolliath/prodIO/GolliathPrivate',
        'shell_cmd': './telegram_public.sh'
    },
    '8080' : {
        'active':   True,
        'name':      'SCR_VNC8080',
        'dir':       '/home/truegolliath/svntools',
        'shell_cmd': './launch_8080.sh'
    },
    '8081': {
        'active':   True,
        'name':      'SCR_VNC8081',
        'dir':       '/home/truegolliath/svntools',
        'shell_cmd': './launch_8081.sh'
    },
    'tunnel_public': {
        'active':   True,
        'name':      'SCR_TUNNEL_PUBLIC',
        'dir':       '/home/truegolliath/svntools',
        'shell_cmd': './mysql_tunnel.sh'
    }
}

def get_cmd_output(cmd):
    result = subprocess.check_output(cmd, shell=True)
    lines = str(result).split("\\n")
    i = 0
    output_lines = []
    for line in lines:
        line = line.replace('\\t','    ').replace('\\r','')
        output_lines.append(line)
        i += 1
    return output_lines

cmd     = "screen -ls"
lines   = get_cmd_output(cmd)

for name, screen in screens.items():
    active      = screen['active']
    if not active:
        continue

    screen_name = screen['name']
    pid         = None
    for line in lines:
        if '.%s '%screen_name in line:
            pid = line.split('.')[0].replace(' ','')
            pid = int(pid)

    if pid is None:
        os.chdir(screen['dir'])
        cmd = "screen -dm -S %s bash -c '%s; exec bash'"%(screen['name'],screen['shell_cmd'])
        LOG.error('   ==> Restart screen for %s'%name)
        if active:
            get_cmd_output(cmd)
    else:
        LOG.info('Screen %s %s is running ...'%(pid,name))

    p = psutil.Process(pid)
    if len(p.children()) != 0:
        child   = p.children()[0]
        child_p = psutil.Process(child.pid)

        running = len(child_p.children()) != 0
        
        if not running:
            cmd = "screen -S %s -X stuff '%s'$(echo '\015')"%(pid,screen['shell_cmd'])
            if active:
                get_cmd_output(cmd)
            LOG.error('   ==> Restart process %s %s in screen %s'%(screen['shell_cmd'],pid,name))
        else:
            LOG.info('Process %s %s in screen %s is running ...'%(screen['shell_cmd'],pid,name))
