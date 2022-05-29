#!/usr/bin/env python
from logging import exception
import asyncio
import os
import io
import traceback
import subprocess
import threading
import time
import json
import hashlib
import sys
import shutil
import platform
import re
import base64
import websockets
import paramiko
import posixpath
import stat

import win32gui
from win32com.shell import shell, shellcon
#import Xlib.support.connect as xlib_connect

from version import api_version

try:
    from lang import *
except Exception as e:
    try:
        from .lang import *
    except Exception as ee:
        from docrun.lang import *
        pass
    pass

try:
    import psutil
except Exception as e:
    psutil = None
    pass

log              = print

server_address   = "127.0.0.1"
port_term        = 5596

INFO             = {
    'quit'                : False ,
    'is_sftp_processing'  : False,
}

WS_TIMEOUT = 60.0

SSHS             = {}
WEBSOCKETS       = {}
SFTPS            = {}

CKEYS            = []

DISPLAYS         = {}
TIMERS           = {}
TASK_CHECKING    = {}

def to_int_number(s):
    try:
        return int(s)
    except:
        return -1

def md5_of_content(cont):
    hash_md5 = hashlib.md5()
    hash_md5.update(cont)
    return hash_md5.hexdigest()

def b64decode(s):
    try:
        return base64.b64decode(s)
    except:
        return s
    pass

def b64encode(s):
    try:
        return base64.b64encode(s)
    except:
        return s
    pass

def get_private_key( key ):
    try:
        key_file = io.StringIO(key)
        pri = paramiko.RSAKey.from_private_key(key_file)
        key_file.close()
        return pri
    except:
        pass
    try:
        key_file = io.StringIO(key)
        pri = paramiko.DSSKey.from_private_key(key_file)
        key_file.close()
        return pri
    except:
        pass
    try:
        key_file = io.StringIO(key)
        pri = paramiko.ECDSAKey.from_private_key(key_file)
        key_file.close()
        return pri
    except:
        pass
    try:
        key_file = io.StringIO(key)
        pri = paramiko.Ed25519Key.from_private_key(key_file)
        key_file.close()
        return pri
    except:
        pass
    log(lt("Key Error: key cannot be parsed") )
    return None

def get_exec_connection(config):
    err = ""
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy() )
        if config.get('auth_key',None):
            #log("try connect with pkey:", config['auth_key'][:20] )
            private_key = get_private_key( b64decode(config['auth_key']) )
            ssh_client.connect( hostname   = config['server_address'],
                                port       = config['server_port'],
                                username   = config['auth_username'],
                                pkey       = private_key)
            pass
        elif config.get('auth_password',None):
            #log("connect with auth password", config['auth_password'])
            ssh_client.connect( hostname=config['server_address'],
                                port=config['server_port'],
                                username=config['auth_username'],
                                password=b64decode(config['auth_password']))
            pass

        else:
            err = 'no authrization provided'
            pass
    except Exception as e:
        err = "connection failed for: {0}".format(e)
        traceback.print_exc()
        pass
    return {
        "client"   : ssh_client,
        'err'      : err,
    }

def client_exec_command(client, code):
    stdin, stdout, stderr = client.exec_command( code )
    stdin.channel.shutdown_write()
    stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode()
    err = (stderr.read() or b"").decode()
    return [out,err]

def one_run_command(config, command ):
    conn   = get_exec_connection(config)
    err    = conn['err']
    out    = ""
    if not err:
        try:
            #log("client = ", client)
            stdin, stdout, stderr = conn['client'].exec_command(command)
            stdin.channel.shutdown_write()
            stdout.channel.recv_exit_status()
            out = (stdout.read() or b"").decode()
            err = (stderr.read() or b"").decode()

            conn['client'].close()

        except Exception as e:
            err = "command execution for: {0}".format(e)
            traceback.print_exc()
            pass
        pass

    return {
        'out'    : out,
        'err'    : err,
    }

async def test_ssh_connection(websocket, config):
    conn  = get_exec_connection( config )
    if conn['client']: conn["client"].close()
    res = json.dumps({
        "name"       : 'test-ssh-connection',
        'server'     : config['server_address'] + ":" + str(config['server_port']),
        "err"        : conn['err'],
        "result"     : ("no" if conn['err'] else "yes")
    })
    await websocket.send(res)
    pass

async def select_sftp_sync_folder(websocket):
    try:
        desktop_pidl = shell.SHGetFolderLocation(0, shellcon.CSIDL_DESKTOP, 0, 0)
        pidl, display_name, image_list = shell.SHBrowseForFolder(
            win32gui.GetDesktopWindow(),
            desktop_pidl,
            lt("Choose sftp sync folder"),
            0, None, None
        )
        if pidl:
            folder_selected = shell.SHGetPathFromIDList(pidl)
        else:
            folder_selected = b""
            pass
        #log("selected path is "+ folder_selected)

        await websocket.send( json.dumps({
            "name"   : "select-sftp-sync-folder",
            "path"   : folder_selected.decode(),
        }))
    except Exception as  e:
        pass
    pass

async def submit_task(config, ckey, message, websocket):
    #print("get submit task with ",ckey, message )
    #task_code        = message.get("code").replace('$','\$')
    task_options     = message.get("options")
    task_uid         = task_options.get("uid")
    task_queue       = task_options.get("queue")
    batch_codes      = message.get('batch_codes')
    conn     = get_exec_connection(config)
    if conn['err'] or not conn['client']:
        await websocket.send( json.dumps({
            "name"   : "submit-task",
            "ckey"   : ckey,
            "uid"    : task_uid,
            "info"   : "connection_cannot_established",
            "error"  : conn['err'],
        }))
        return
    client   = conn['client']

    check_queue      = message.get("check_queue")
    try:
        ## check requirement
        #print("check requirement and return info")
        [out, err] = check_requirement(client, ckey)
        if err:
            # error occured while prepare directories
            await websocket.send( json.dumps({
                "name"   : "submit-task",
                "ckey"   : ckey,
                "uid"    : task_uid,
                "info"   : "preperation_failed",
                "error"  : err,
            }))
            if client: client.close()
            return
        #log("preperation done without error")

        # check pbs system info
        (slurm_exist, queue_info) = check_if_slurm_exist(client)
        if not slurm_exist: (pbs_exist,   queue_info) = check_if_pbs_exist(client)
        if check_queue:
            queue_type   = "slurm" if slurm_exist else ("pbs" if pbs_exist else "none")
            #print("return queue check info", queue_type, queue_info)
            await websocket.send( json.dumps({
                "name"         : "submit-task",
                "ckey"         : ckey,
                "uid"          : task_uid,
                "info"         : "queue_required" ,
                "queue"        : queue_info,
                "queue_type"   : queue_type,
            }))
            return

        #print('task_options=',task_options)
        #print('deal tasks:', batch_codes)
        for task_batch in batch_codes:
            task_code = batch_codes[task_batch]
            #print("deal task", task_batch, task_code )
            if task_queue and slurm_exist:
                running_mode   = 'slurm'
                [out,err] = submit_task_by_slurm(client, ckey, task_uid, task_batch, task_code, task_options )
                pass
            elif task_queue and pbs_exist:
                running_mode   = 'pbs'
                [out,err] = submit_task_by_torque(client, ckey, task_uid, task_batch, task_code, task_options )
                #print("run task with pbs system")
                pass
            else:
                #print("run task in local system")
                running_mode   = 'shell'
                [out, err] = submit_task_by_shell(client, ckey, task_uid, task_batch, task_code )
                pass
            if err:
                log("task launch error: {}".format(err) )
                await websocket.send( json.dumps({
                    "name"          : "submit-task",
                    "ckey"          : ckey,
                    "uid"           : task_uid,
                    'task_batch'    : task_batch,
                    "info"          : "task_launch_error",
                    "error"         : err,
                }))
            else:
                #print("task launch output:",out)
                await websocket.send( json.dumps({
                    "name"          : "submit-task",
                    "ckey"          : ckey,
                    "uid"           : task_uid,
                    'task_batch'    : task_batch,
                    "running_mode"  : running_mode,
                    "info"          : "task_launch_success",
                }))
            pass

        client.close()

    except Exception as e:
        err = "connection failed for: {0}".format(e)
        traceback.print_exc()
        pass

    if client: client.close()

    pass

def check_requirement(client, ckey):
    [out,err]  = client_exec_command(client, """
cd ~
if ! [ -d pond-calculation-works ]; then
    mkdir pond-calculation-works
fi
cd pond-calculation-works
if ! [ -d {0} ];then
    mkdir {0}
fi
cd {0}
if ! [ -d .tasks ]; then
    mkdir .tasks
fi
if ! [ -f .bashrc ]; then
    touch .bashrc
fi
        """.format(ckey))
    return [out, err]

def check_if_slurm_exist(client):
    [out,err]  = client_exec_command(client, """
. /etc/profile
. ~/.bashrc
echo "#-queue-out-#"
sinfo
    """)
    #print("check if_slurm_exist out=", out)
    #print("check if_slurm_exist err=", err)
    if err: return (False,'')
    out = out.split("#-queue-out-#\n")[1]
    return (True,out)

def  check_if_pbs_exist(client):
    [out,err]  = client_exec_command(client, """
. /etc/profile
. ~/.bashrc
echo "#-queue-out-#"
qstat -Q
    """)
    if err: return (False,'')
    out = out.split("#-queue-out-#\n")[1]
    #print("check if_pbs_exist out=", out)
    #print("check if_pbs_exist err=", err)
    return (True,out)

def submit_task_by_slurm(client, ckey, task_uid, task_batch, task_code, task_options, ):
    #print("run task with pbs system")
    gpu_resource = ("#SBATCH --gres=gpu:"+str(task_options.get("gpus")) ) if task_options.get("gpus",None) else ""
    #print("try submit task to slurm", task_options, gpu_resource)
    task_queue = task_options.get("queue")
    if task_queue[-1] == "*": task_queue = task_queue[:-1]
    [out,err]  = client_exec_command(client, """
. /etc/profile
. ~/.bashrc
cd ~/pond-calculation-works/{2}/
cat << 'EOF' > .tasks/{0}.code
{1}
EOF
cat <<EOF > .tasks/{0}.sh
#!/bin/bash
#SBATCH --job-name={0}
#SBATCH --nodes={3}
#SBATCH --ntasks-per-node={4}
{5}
#SBATCH -p {6}
#SBATCH -o $HOME/pond-calculation-works/{2}/.tasks/{0}.log

cd \$SLURM_SUBMIT_DIR
echo -n "evaluating" >./.tasks/{0}.status

echo \`date +%s\` > ./.tasks/{0}.time
if [ -f /etc/profile ]; then
    . /etc/profile
fi
if [ -f \$HOME/.bashrc ]; then
    . \$HOME/.bashrc
fi
if [ -f .bashrc ]; then 
    . .bashrc
fi


./.tasks/{0}.code > ./.tasks/{0}.log 2>&1

echo \`date +%s\` >> ./.tasks/{0}.time
if [ -f ./.tasks/{0}.pid ]; then 
    rm ./.tasks/{0}.pid;
fi
echo -n "finished" >./.tasks/{0}.status
EOF

chmod +x .tasks/{0}.code
chmod +x .tasks/{0}.sh

if [ -f .tasks/{0}.log ]; then rm .tasks/{0}.log; fi
echo -n "pending" >./.tasks/{0}.status
sbatch ./.tasks/{0}.sh > ./.tasks/{0}.pid
    """.format(
        task_uid+"_"+task_batch, task_code, ckey,
        task_options.get("nodes", 1),
        task_options.get("ppn", 1),
        gpu_resource,
        task_queue,
    ) )
    return [out,err]

def submit_task_by_torque(client, ckey, task_uid, task_batch, task_code, task_options):
    gpu_resource = (":gpus="+str(task_options.get("gpus")) ) if task_options.get("gpus",None) else ""
    #print("try submit task to pbs", task_options, gpu_resource)
    [out,err]  = client_exec_command(client, """
. /etc/profile
. ~/.bashrc
cd ~/pond-calculation-works/{2}/
cat << 'EOF' > .tasks/{0}.code
{1}
EOF
cat <<EOF > .tasks/{0}.pbs
#PBS -N {0}
#PBS -l nodes={3}:ppn={4}{5}
#PBS -q {6}
#PBS -j oe
#PBS -o $HOME/pond-calculation-works/{2}/.tasks/{0}.log

cd \$PBS_O_WORKDIR
echo -n "evaluating" >./.tasks/{0}.status

echo \`date +%s\` > ./.tasks/{0}.time
if [ -f /etc/profile ]; then
    . /etc/profile
fi
if [ -f \$HOME/.bashrc ]; then
    . \$HOME/.bashrc
fi
if [ -f .bashrc ]; then 
    . .bashrc
fi

./.tasks/{0}.code > ./.tasks/{0}.log 2>&1

echo \`date +%s\` >> ./.tasks/{0}.time

if [ -f ./.tasks/{0}.pid ]; then 
    rm ./.tasks/{0}.pid;
fi
echo -n "finished" >./.tasks/{0}.status
EOF
chmod +x .tasks/{0}.code
chmod +x .tasks/{0}.pbs

if [ -f .tasks/{0}.log ]; then rm .tasks/{0}.log; fi
echo -n "pending" >./.tasks/{0}.status

qsub ./.tasks/{0}.pbs > ./.tasks/{0}.pid
    """.format(
        task_uid + "_" + task_batch,
        task_code,
        ckey,
        task_options.get("nodes", 1),
        task_options.get("ppn", 1),
        gpu_resource,
        task_options.get("queue"),
    ))
    #print("submit out:", out)
    #print("submit err:", err)
    return [out,err]

def submit_task_by_shell(client,ckey, task_uid, task_batch, task_code):
    [out,err]  = client_exec_command(client, """
cd ~/pond-calculation-works/{2}/
cat << 'EOF' > .tasks/{0}.code
{1}
EOF
cat <<EOF > .tasks/{0}.task
#!/bin/bash
echo -n "evaluating" >./.tasks/{0}.status
echo \`date +%s\` > ./.tasks/{0}.time
if [ -f /etc/profile ]; then
    . /etc/profile
fi
if [ -f \$HOME/.bashrc ]; then
    . \$HOME/.bashrc
fi
if [ -f .bashrc ]; then 
    . .bashrc
fi
./.tasks/{0}.code
#./.tasks/{0}.code > ./.tasks/{0}.log 2>&1
echo \`date +%s\` >> ./.tasks/{0}.time

sleep 0.5
if [ -f ./.tasks/{0}.pid ]; then 
    rm ./.tasks/{0}.pid;
    echo -n "finished" >./.tasks/{0}.status
else
    echo -n "interupted" >./.tasks/{0}.status
fi
EOF

chmod +x .tasks/{0}.code
chmod +x .tasks/{0}.task

. /etc/profile
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
if [ -f .bashrc ]; then 
    . .bashrc
fi

if [ -f .tasks/{0}.log ]; then rm .tasks/{0}.log; fi
echo -n "pending" >./.tasks/{0}.status
nohup ./.tasks/{0}.task >> ./.tasks/{0}.log 2>&1 &
echo $! > ./.tasks/{0}.pid
    """.format(
        task_uid+"_"+task_batch, task_code, ckey,
    ) )
    return [out, err]

async def stop_task(config, ckey, message, websocket):
    #print("try stop task with ",ckey, message )
    running_mode    = message.get("running_mode" )
    batch           = message.get('batch')
    task_options    = message.get("options" )
    task_uid        = task_options.get("uid")
    conn            = get_exec_connection(config)
    if conn['err'] or not conn['client']:
        await websocket.send( json.dumps({
            "name"   : "check-task",
            "ckey"   : ckey,
            "uid"    : task_uid,
            "info"   : "connection_cannot_established",
            "error"  : conn['err'],
        }))
        return
    client      = conn['client']
    #print("try stop with :", running_mode)
    if running_mode == 'slurm':
        print('kill in slurm mode')
        #print("check slurm task: {0}_{1}".format(task_uid, batch) )
        if check_if_slurm_exist(client)[0]:
            #print("check slurm task:", task_uid)
            [out,err]  = client_exec_command(client, """
. /etc/profile
. ~/.bashrc
cd ~/pond-calculation-works/{1}/.tasks/
if [ -f {0}.pid ]; then
    scancel `cat {0}.pid |awk '{{print $NF}}'`
    rm {0}.pid
    echo -n "interupted" > {0}.status
else
    rm {0}.status
fi
            """.format(task_uid+"_"+batch, ckey))
            pass
        else:
            #print("pbs task kill, but no pbs command found" )
            [out, err] = client_exec_command(
                client, """
cd ~/pond-calculation-works/{1}/.tasks/
if [ -f {0}.pid ]; then
    rm {0}.pid
    echo -n "interupted" {0}.status
else
    rm {0}.status
fi
            """.format(task_uid + "_" + batch, ckey))
            pass
    elif running_mode == 'pbs':
        print('kill in torque mode')
        #print("check pbs task: {0}_{1}".format(task_uid, batch) )
        if check_if_pbs_exist(client)[0]:
            #print("check pbs task:", task_uid)
            [out, err ]  = client_exec_command(client, """
. /etc/profile
. ~/.bashrc
cd ~/pond-calculation-works/{1}/.tasks/
if [ -f {0}.pid ]; then
    qdel `cat {0}.pid`
    rm {0}.pid
    echo -n "interupted" > {0}.status
else 
    rm {0}.status
fi
            """.format(task_uid +"_"+batch, ckey))
            #print("task interupted")
            pass
        else:
            #print("pbs task kill, but no pbs command found" )
            [out, err ]  = client_exec_command(client, """
cd ~/pond-calculation-works/{1}/.tasks/
if [ -f {0}.pid ]; then
    rm {0}.pid
    echo -n "interupted" > {0}.status
else
    rm {0}.status
fi
            """.format(task_uid+"_"+batch, ckey))
            #print("task already vanished")
            pass
        pass
    else: # run by shell
        print('kill in shell mode', task_uid, batch, ckey)
        #print("check no pbs task: {0}".format(task_uid, batch), flush=True)
        [out, err] = client_exec_command(
            client, """
cd ~/pond-calculation-works/{1}/.tasks/
pid=`ps -ef|grep ./.tasks/{0}|grep code|grep -v grep` 
if ! [ "x${{pid}}" == "x" ]; then 
    pid=`echo "${{pid}}"|awk '{{print $2}}'`
    kill -9 ${{pid}}
    echo "pid exist kill it"
fi
if [ -f {0}.pid ]; then
    rm {0}.pid
    echo -n "interupted" > {0}.status
else
    rm {0}.status
fi
        """.format(task_uid + "_" + batch, ckey))
        #print("task interupted",flush=True)
        pass
    print("kill out >>>", out, sep='')
    print("kill err >>>", err, sep='')
    [status, status_err] = client_exec_command( client, """
cd ~/pond-calculation-works/{1}/.tasks/
if [ -f {0}.status ]; then
    cat {0}.status
else
    echo -n "clear"
fi
    """.format(task_uid+"_"+batch, ckey) )
    print("kill status result", task_uid+"_"+batch, status, status_err)
    await websocket.send( json.dumps({
        "name"   : "check-task",
        "info"   : "task-stopped",
        "ckey"   : ckey,
        "uid"    : task_uid,
        "batch"  : batch,
        "error"  : err,
        "output" : out,
        "status" : status,
    }))
    pass

async def check_task(config, ckey, message, websocket):
    #print("try check task with ",ckey, message )
    start_len       = message.get("start_len",0)
    task_options    = message.get('options')
    task_uid        = task_options.get("uid")
    current_batch   = message.get("current_batch")
    jobs            = message.get("batches")
    running_mode    = message.get("running_mode")

    print("try check with:", current_batch, start_len )

    conn     = get_exec_connection(config)
    if conn['err'] or not conn['client']:
        await websocket.send( json.dumps({
            "name"   : "check-task",
            "ckey"   : ckey,
            "uid"    : task_uid,
            "info"   : "connection_cannot_established",
            "error"  : conn['err'],
        }))
        return
    client      = conn['client']

    if TASK_CHECKING.get( ckey+"_"+task_uid ):
        if client: client.close()
        return
    else:
        TASK_CHECKING[ ckey+"_"+task_uid ] = True
        pass

    #print('check evaluating jobs:', jobs, current_batch, start_len)
    batch_result   = []
    output_result  = ""
    error_result  = ""
    for batch in jobs:
        [out,err] = client_exec_command(client, """
    cd ~/pond-calculation-works/{1}/.tasks/
    echo "#-TASK_INFO_START-#"
    if [ -f {0}.pid ]; then
        pid=`cat {0}.pid |awk '{{print $NF}}'`
        if [ {3} == 'slurm' ]; then
            jobid=`cat {0}.pid |awk '{{print $NF}}'`
            jobstate=`squeue --j ${{jobid}} -o "%t"|tail -1`
            if [ ${{jobstate}} == 'PD' ]; then
                echo "queueing"
            elif [ ${{jobstate}} == 'R' ]; then
                echo "evaluating"
            elif [ ${{jobstate}} == 'C' ]; then
                echo "finished"
            else 
                echo ${{jobstate}}
            fi
        elif [ {3} == 'pbs' ]; then
            jobid=`cat {0}.pid`
            jobstate=`qstat -f ${{jobid}} |grep 'job_state'|awk '{{print $NF}}'`
            if [ ${{jobstate}} == "Q" ]; then
                echo "queueing"
            elif [ ${{jobstate}} == "R" ]; then
                echo "evaluating"
            else 
                echo ${{jobstate}}
            fi
        else
            echo "evaluating"
        fi
        if ! [ -f {0}.log ]; then
            echo "#-TASK_INFO_END-#"
            exit 0
        fi
    fi
    if [ -f {0}.status ]; then
        echo `cat {0}.status`
    else 
        echo "clear"
    fi
    if ! [ -f {0}.log ]; then
        echo "#-TASK_INFO_END-#"
        exit 0
    fi
    if [ -f {0}.time ]; then
        echo `cat {0}.time`
    fi
    echo "#-TASK_INFO_END-#"
    if [ {4} ]; then
        out=`cat {0}.log`
        echo -n "${{out:{2}}}"
    fi
        """.format(
            task_uid+"_"+batch, ckey, start_len,
            running_mode,
            'true' if current_batch == batch else '',
        ))
        status, output = out.split("\n#-TASK_INFO_END-#\n",1)
        status = re.split('[ \n]+',status.split("#-TASK_INFO_START-#\n")[-1] )
        batch_result.append([ batch, status])
        if current_batch == batch:
            output_result  = output
            error_result   = err
        pass
    print("get batch result:", batch_result, )
    #print("output result = ", output_result)
    #print("error result = ", error_result)

    await websocket.send( json.dumps({
        "name"            : "check-task",
        "ckey"            : ckey,
        "uid"             : task_uid,
        "current_batch"   : current_batch,
        "start_len"       : start_len,
        "output"          : output_result,
        "error"           : error_result,
        "batch_result"    : batch_result,
    }))
    if client: client.close()
    if TASK_CHECKING.get( ckey+"_"+task_uid ):
        del TASK_CHECKING[ ckey+"_"+task_uid  ]
        pass
    pass

def launch_close_websocket(page_id):
    timer = TIMERS.get("ws_close_"+page_id)
    if timer:
        timer.cancel()
        pass
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop( loop )
    for ckey in CKEYS:
        ssh_id       = ckey+"_"+page_id
        ssh_conn     = SSHS.get(ssh_id,None)
        sftp_conn    = SFTPS.get(ssh_id,None)
        if ssh_conn:
            loop.run_until_complete(close_ssh_connection(None, ssh_conn))
            pass
        if sftp_conn:
            loop.run_until_complete(close_sftp_connection(None, sftp_conn))
            pass
    loop.close()
    TIMERS[ "ws_close_"+page_id ] = None
    pass

async def close_ssh_connection(websocket, conn):
    if websocket:
        try:
            mes = {
                **conn.get('message',{}),
                'name'     : 'shell-message',
                'info'     : 'ssh_connection_closed',
                'message'  : 'ssh connection closed...\r\n',
            }
            #print("send close message to js:", mes)
            await websocket.send(json.dumps(mes))
        except Exception as e:
            log("send mes in close ssh connection failed:{0}".format(e) )
            pass

    if conn:
        log("ssh connection {} closed".format(conn['ssh_id']) )
        conn['message']['message'] = lt('connection closed ...\r\n')
        conn['channel'].close()
        SSHS[ conn['ssh_id'] ] = None
        #print("timer after close = ", TIMERS.get( "ssh_close_"+conn['ssh_id'],None ) )
        pass
    pass


def launch_ssh_communication(page_id, ssh_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop( loop )
    loop.run_until_complete( ssh_communication(page_id, ssh_id) )
    loop.close()
    pass


async def ssh_communication(page_id, ssh_id ):
    try:
        conn = SSHS.get(ssh_id, None)
        #print("start communication with:",websocket, ssh_id)
        #print("conn channel for this communication is :", conn['channel'])
        while True:
            data = conn['channel'].recv(4096)
            if not len(data):
                log("recieved empty data, connection closed, {}".format(ssh_id) )
                await close_ssh_connection(WEBSOCKETS[page_id], conn)
                return
            timer = TIMERS.get("ws_close_"+page_id)
            if timer:
                #print("page reconnecting cancel quit timer", timer)
                timer.cancel()
                TIMERS["ws_close_"+page_id] = None
                pass
            #print("get data from channel:", data)
            #print("data type = ", type(data) )
            #await websocket.send( data )
            #continue
            #print("get ssh data:", data)
            try:
                data = data.decode('utf-8')
                #print("decode data to:", data[:10] )
                pass
            except Exception as e:
                log("decode data failed on: {0}".format( data ) )
                data = ""
                pass
            #print("get ssh data:", data)
            mes = conn['message']
            mes['message'] = data
            mes['info']    = 'term_data'
            try:
                await WEBSOCKETS[page_id].send(json.dumps(mes))
            except Exception as e:
                # set timer to close all websocket related ssh conection
                # cancel timer if the websocket reconnected ( page refresh )
                log("websocket send error, set timer to close in 10s: {0}".format(ssh_id) )
                if TIMERS.get("ws_close_"+page_id): continue
                TIMERS["ws_close_"+page_id] = threading.Timer( WS_TIMEOUT, launch_close_websocket, [page_id])
                TIMERS["ws_close_"+page_id].start()
            pass
        pass
    except Exception as e:
        log("comunication loop quited with error:{0}".format(e) )
        traceback.print_exc()
        # should close ssh connection directly
        await close_ssh_connection(WEBSOCKETS[page_id], conn )
        pass

    pass

async def get_ssh_connection(websocket, config, ckey='', page_id = ''):
    ssh_id =  ckey + "_" + page_id
    #print("try get conn from SSHS:", ssh_id)
    conn = SSHS.get( ssh_id, None )
    if conn and conn.get('transport'):
        #print("get conn channel:", conn['channel'])
        t = conn.get('transport')
        if t.is_active(): return conn
        t.close()
        pass
    try:
        #print("try create new conn" )
        conn = {}
        conn['ssh_id'] = ssh_id

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy() )

        if config.get('auth_key',None):
            #print("try connect with pkey:", config['auth_username'], config['auth_key'][:20] )
            private_key = get_private_key( b64decode(config['auth_key']) )
            client.connect( hostname   =  config['server_address'],
                            port       =  config['server_port'],
                            username   =  config['auth_username'],
                            pkey       =  private_key)
            pass
        elif config.get('auth_password',None):
            #print("connect with auth password",config['auth_username'], config['auth_password'])
            client.connect( hostname   =  config['server_address'],
                            port       =  config['server_port'],
                            username   =  config['auth_username'],
                            password   =  b64decode( config['auth_password'] ) )
            pass
        else:
            log("connect with no auth provided")
            return None
        #print("client = ", client)

        conn['client']      = client
        conn['transport']   = client.get_transport()
        conn['channel']     = conn['transport'].open_session()
        conn['channel'].get_pty(term=config.get('term','linux'),
                                width=config.get('pty_width',80),
                                height=config.get('pty_height',24) )
        conn['channel'].invoke_shell()

        SSHS[ssh_id] = conn

        mes  = {}
        mes['ckey']      = ckey
        mes['page_id']   = page_id
        mes['name']      = 'shell-message'
        mes['info']      = 'term_data'
        conn['message']  = mes
        for i in range(2):
            recv = conn['channel'].recv(1024).decode('utf-8')
            #print("connection established, recv:", recv)
            mes['message']   = recv
            await websocket.send( json.dumps(mes) )
            pass

        if not ckey in CKEYS:
            #print("append ckey to list:", ckey)
            CKEYS.append( ckey )
            pass

        #print("conn created = ", conn, SSHS[ssh_id] )

        threading.Thread(target=launch_ssh_communication,args=([page_id, ssh_id]) ).start()
        #print("return conn:", conn)
        conn['channel'].send("cd ~/pond-calculation-works/{0}\n".format(ckey))
        return conn

    except Exception as e:
        traceback.print_exc()
        await websocket.send(json.dumps({
            'name'      : 'shell-message',
            'info'      : 'connection_error',
            'message'   : 'ssh connection cannot be established: {0}\r\n'.format(e),
            'message'   : lt('ssh connection to {0}:{1} cannot be established: {2}\r\n',config.get("server_address","?"), config.get("server_port","22"), e),
        }))
        log("create connection failed")
        pass
    return None

def is_file_exist(sftp,file):
    try:
        sftp.lstat( file )
        return True
    except Exception as e:
        return False

async def get_sftp_connection(websocket, config, ckey='', page_id = ''):
    ssh_id =  ckey + "_" + page_id
    #print("try get conn from SSHS:", ssh_id)
    conn = SFTPS.get( ssh_id, None )
    if conn and conn.get('transport'):
        #print("get conn channel:", conn['channel'])
        t = conn.get('transport')
        if t.is_active(): return conn
        t.close()
        pass
    try:
        #print("try create new conn" )
        conn = {}
        conn['ssh_id'] = ssh_id

        t   = paramiko.Transport( (config['server_address'], int(config['server_port'] or 22)) )

        if config.get('auth_key',None):
            #print("try connect with pkey:", config['auth_key'][:20] )
            private_key = get_private_key( b64decode(config['auth_key']) )
            t.connect( username=config['auth_username'],
                       pkey=private_key)
            pass
        elif config.get('auth_password',None):
            #print("connect with auth password", config['auth_password'])
            t.connect( username=config['auth_username'],
                       password=b64decode(config['auth_password']))
            pass
        else:
            log("connect with no auth provided")
            return None
        #print("client = ", client)

        conn['transport']   = t
        conn['sftp']        = paramiko.SFTPClient.from_transport(t)

        conn['sftp'].chdir('.')
        conn['home_dir'] = conn['sftp'].getcwd()
        #print("sftp home dir is", conn['home_dir'])

        conn['sftp'].chdir('.')
        works_dir    = conn["home_dir"]+"/pond-calculation-works"
        key_dir      =  works_dir+"/"+ckey
        #print(works_dir, key_dir)
        if not is_file_exist( conn['sftp'], works_dir):
            conn['sftp'].mkdir( works_dir )
            pass
        if not is_file_exist( conn['sftp'], key_dir):
            conn['sftp'].mkdir( key_dir )
            pass

        SFTPS[ssh_id] = conn
        return conn

    except Exception as e:
        traceback.print_exc()
        log("create connection failed")
        pass
    return None

async def close_sftp_connection(websocket, conn):
    if websocket:
        mes = {
            **conn.get('message',{}),
            'name'     : 'sftp-message',
            'info'     : 'sftp_connection_closed',
            'message'  : 'sftp connection closed...\r\n',
        }
        #print("send close message to js:", mes)
        await websocket.send(json.dumps(mes))
    if conn:
        log("try close sftp connection {0}".format( conn['ssh_id'] ) )
        conn['transport'].close()
        SFTPS[ conn['ssh_id'] ] = None
    pass

def prepare_sftp_infos(current_dir, sftp_dir, ckey, conn):
    #print("try get info with:", current_dir, sftp_dir, ckey)
    local_path = sftp_dir
    if not local_path:
        home_dir = os.path.expanduser('~')
        #print('home dir =', home_dir )
        local_path = os.path.join( home_dir, "pond-calculation-works" )
        if not os.path.exists( local_path ): os.mkdir( local_path )
        local_path = os.path.join( local_path, ckey )
        pass

    #print("get local root path:", local_path)
    if not os.path.exists( local_path ): os.mkdir( local_path )

    for tdir in current_dir:
        local_path = os.path.join( local_path, tdir)
        #print("check current_dir:", local_path)
        if not os.path.exists( local_path ): os.mkdir( local_path )
        pass

    if conn:
        remote_path     = "{0}/pond-calculation-works/{1}/{2}".format(conn['home_dir'], ckey, "/".join(current_dir ) )
        pass
    else:
        remote_path     = ""

    return {
        "local_path"   : local_path,
        "remote_path"  : remote_path,
        'current_dir'  : current_dir,
        'ckey'         : ckey,
    }

    pass

def open_sync_folder(current_dir, sftp_dir, ckey, ):
    infos = prepare_sftp_infos(current_dir, sftp_dir, ckey, None)
    subprocess.Popen(r'explorer "{0}"'.format(infos['local_path']),shell=True)
    pass

def sftp_open_file(infos, message):
    item  = message.get('item')
    local_path = os.path.join( infos['local_path'], item['filename'] )
    if platform.system() == 'Windows':
        #subprocess.Popen(r'start {0}'.format(local_path ), shell=True)
        os.startfile(local_path, 'open')
    else:
        subprocess.Popen(r'open {0}'.format(local_path ), shell=True)
        pass
    pass

def sftp_listdir(infos, ckey, sftp, message):
    while INFO['is_sftp_processing']  : time.sleep(0.1)
    INFO['is_sftp_processing']  = True
    try:
        #print("list dir with message:", message)
        old_md5         = message.get("dir_md5")
        #print("try to list dir:", infos, )
        sftp.chdir( infos['remote_path'] )
        current_dir     = sftp.getcwd().split(ckey)[-1]
        while True:
            changed,dirs     = attr_to_list( sftp.listdir_attr( ), infos , sftp )
            if not changed: break
            #print('dir changed try another list')
            pass
        if current_dir and current_dir[-1] == '/': current_dir = current_dir[:-1]
        #print("cwd after list is:", current_dir)
        new_md5  = md5_of_content( json.dumps( dirs ).encode() )
        if old_md5 == new_md5: result = []
        result   = {
            "dirs"         : dirs,
            'md5'          : new_md5,
            'current_dir'  : current_dir,
            'remote_path'  : infos['remote_path'],
        }
        INFO['is_sftp_processing']  = False
        return result
    except Exception as e:
        log("sftp_listdir failed for: {0}".format(e) )
        pass
    INFO['is_sftp_processing']  = False
    pass

def rmtree(sftp, remotepath, level=0):
    for f in sftp.listdir_attr(remotepath):
        rpath = posixpath.join(remotepath, f.filename)
        if stat.S_ISDIR(f.st_mode):
            rmtree(sftp, rpath, level=(level + 1))
        else:
            rpath = posixpath.join(remotepath, f.filename)
            print('removing %s%s' % ('    ' * level, rpath))
            sftp.remove(rpath)
    print('removing %s%s' % ('    ' * level, remotepath))
    sftp.rmdir(remotepath)


def sftp_delete_item(infos, sftp, message):
    print("try delete item")
    while INFO['is_sftp_processing']  : time.sleep(0.1)
    INFO['is_sftp_processing']  = True
    try:
        item         = message.get("item")
        print("delete item:", item)
        # local side
        local_path = os.path.join( infos['local_path'], item['filename'] )
        print("try remove local path:", local_path )
        if item['status'] != 'local_not_exist':
            if item['local_is_dir']:
                print("local remove with command rmtree" )
                shutil.rmtree( local_path )
            else:
                os.remove( local_path )
                pass
            pass
        # remote side
        remote_path  = posixpath.join( infos['remote_path'] , item['filename'] )
        remote_path = remote_path.replace("\\","/")
        print("try remove remote path:", remote_path )
        if item['status'] != 'remote_not_exist' :
            if item['is_dir']:
                print("remote remove with command sftp.rmdir" )
                #sftp.rmdir( remote_path )
                rmtree(sftp, remote_path )
            else:
                sftp.remove( remote_path )
                pass
            pass
        pass
    except Exception as e:
        log("sftp_delete_file for: {0}".format(e) )
        traceback.print_exc()
        pass
    INFO['is_sftp_processing']  = False
    pass

def sftp_upload_file(infos, sftp, message):
    while INFO['is_sftp_processing']  : time.sleep(0.1)
    INFO['is_sftp_processing']  = True
    try:
        item  = message.get('item')
        local_path = os.path.join( infos['local_path'], item['filename'] )
        remote_path  = infos['remote_path'] + "/" + item['filename']
        sftp.put(local_path, remote_path, )
        sftp.utime(remote_path, (item['local_access_time'], item['local_modified_time']))
    except Exception as e:
        log("sftp_upload_file failed for: {0}".format(e) )
        pass
    INFO['is_sftp_processing']  = False
    pass

def sftp_download_file(infos, sftp, message):
    while INFO['is_sftp_processing']  : time.sleep(0.1)
    INFO['is_sftp_processing']  = True
    try:
        item  = message.get('item')
        local_path = os.path.join( infos['local_path'], item['filename'] )
        remote_path  = infos['remote_path'] + "/" + item['filename']
        sftp.get(remote_path, local_path,)
        os.utime(local_path, (item['access_time'],item['modified_time']))
        pass
    except Exception as e:
        log("sftp_download_file failed for: {0}".format(e) )
        pass
    INFO['is_sftp_processing']  = False
    pass

def download_sync_file(sftp, remote_path, local_path):
    try:
        rstat   = sftp.stat( remote_path )
    except :
        rstat   = None
        pass
    lstat   = os.path.exists(local_path) and os.stat(local_path)
    #print("try sync", local_path, remote_path, lstat, rstat )
    if rstat and (rstat.st_mtime != (lstat and lstat.st_mtime)):
        sftp.get(remote_path, local_path)
    pass
async def sftp_prepare_files(infos, sftp, message, websocket):
    #print("try prepare files:", message)
    while INFO['is_sftp_processing']  : time.sleep(0.1)
    INFO['is_sftp_processing']  = True
    file_list          = None
    data_file          = message.get('data_file','')
    current_data_file  = message.get('current_data_file')
    value_type         = message.get('value_type','raw')
    binary_read        = message.get('binary_read')
    try:
        pattern     = message.get('file_pattern')
        files       = message.get("files")
        #print("prepare files:", pattern, files)
        if pattern:
            remote_path  = infos['remote_path']
            local_path   = infos['local_path']
            paths = pattern[0].split("/")
            #print("paths =", paths)
            if len(paths)>1:
                remote_path = remote_path +"/"+ '/'.join( paths[:-1] )
                local_path  = os.path.join(local_path, *paths[:-1] )
                file_prefix = paths[1]
            else:
                file_prefix = paths[0]
                pass
            file_suffix    = pattern[1]
            file_list      = []
            plen,slen = len(file_prefix),len(file_suffix)
            #print('try check', file_prefix, file_suffix)
            for name in sftp.listdir( remote_path ):
                #print("check :", name)
                if name.startswith( file_prefix ) and name.endswith(file_suffix):
                    ind = name[plen:-slen]
                    file_list.append([to_int_number(ind),name])
                    pass
                pass
            #print('file_list = ', file_list)
            if len(file_list) == 0:
                INFO['is_sftp_processing']  = False
                return
            file_list.sort(key=lambda item: item[0] )
            #print("message data_file is", message.get("data_file") )
            data_file    = data_file or file_list[-1][1]
            remote_path  = remote_path + "/" + data_file
            local_path   = os.path.join( local_path, data_file )
            #print('list get is', file_list)
            #print('data_file to be:', data_file)
            #print(remote_path, local_path)
            download_sync_file(sftp, remote_path, local_path)
            pass

        else:
            data_file     = data_file or files[-1]
            local_path    = os.path.join( infos['local_path'], data_file )
            remote_path   = infos['remote_path'] + "/" + data_file
            download_sync_file(sftp, remote_path, local_path)
            pass

        data        = ''
        if not (current_data_file and data_file == current_data_file):
            #print("binary read:", message.get('binary_read'), 'value_type =',value_type)
            if not os.path.exists(local_path):
                await websocket.send( json.dumps({
                    'name'           : message.get("message_name",message.get("name")),
                    'file_list'      : file_list,
                    'data_file'      : data_file,
                    'file_data'      : data,
                    'not_found'      : True,
                }) )
                pass
            with open(local_path,'rb' if message.get('binary_read') else 'r') as f:
                data       = f.read()
                pass
            if value_type == 'number' :
                data      = data.split()
                data = list(map(lambda x:float(x), data, ))
                pass
            elif value_type == 'base64':
                data        = b64encode(data)
                #print('data get is:', type(data)  )
                data        = data.decode()
            pass
        await websocket.send( json.dumps({
            'name'           : message.get("message_name",message.get("name")),
            'file_list'      : file_list,
            'data_file'      : data_file,
            'file_data'      : data,
        }) )
        pass
    except Exception as e:
        log('sftp_prepare_files failed for:{0}'.format(e) )
        traceback.print_exc()
        pass
    INFO['is_sftp_processing']  = False

def attr_to_list(attrs, infos, sftp ):
    # check local dir
    local_items = {}
    for  item in os.listdir(infos['local_path']):
        #print( 'check local item:', item)
        tpath = os.path.join( infos['local_path'], item )
        info = os.stat( tpath )
        local_items[ item ] = {
            'filename'             : item,
            'local_is_dir'         : os.path.isdir( tpath ),
            'local_size'           : info.st_size,
            'local_modified_time'  : int(info.st_mtime),
            'local_access_time'    : int(info.st_atime),
        }

    # check remote dir
    fres = []
    for item in attrs:
        #print("deal item:", item)
        items    = item.longname.split()
        is_dir   = items[0][0] == 'd'
        is_link  = items[0][0] == 'l'
        is_exe   = items[0][3] == 'x'
        sl = {
            "is_dir"         : is_dir,
            "is_exe"         : is_exe,
            "is_link"        : is_link,
            "filename"       : item.filename,
            "mode"           : items[0],
            "owner"          : items[2],
            "size"           : item.st_size,
            "modified_time"  : int(item.st_mtime),
            "access_time"    : int(item.st_atime),
        }
        local_item = local_items.get( item.filename , None)
        if local_item:
            sl = { **local_item, ** sl }
            del local_items[ item.filename ]
            pass
        fres.append( sl )
        if is_dir:
            tdir = os.path.join( infos['local_path'], item.filename )
            if not os.path.exists( tdir ): os.mkdir( tdir )
            pass
        pass

    # items that not present on server side
    dir_changed = False
    for ind in local_items:
        item = local_items[ ind ]
        fres.append( item )
        if item['local_is_dir']: #created dir on server
            tpath = infos['remote_path'] +"/"+item['filename']
            #print("try create new folder:", tpath)
            sftp.mkdir( tpath )
            dir_changed = True
            pass
        pass
    fres.sort(key=lambda item: item.get('filename').lower() )
    #print( "list dir get:",  fres)
    return dir_changed, fres

async def data_processing(websocket, data):
    try:
        config                  = data.get('config',  {})

        page_id                 = data.get('page_id', '0')
        ckey                    = data.get('ckey',    '0')
        ssh_id                  = ckey + "_" + page_id

        message                 = data.get("message", None)
        message_name            = message.get('name',    None)

        WEBSOCKETS[page_id]     = websocket

        await websocket.send(json.dumps({
            'name'         : 'api_version',
            'api_version'  : api_version,
        }))

        #print('\nget input request', message_type, ckey, page_id )
        if message_name  == "test-ssh-connection":
            await test_ssh_connection(websocket, config)
            return

        if message_name == 'select-sftp-sync-folder':
            #print("met select sync folder message:", message)
            await select_sftp_sync_folder(websocket)
            return

        if message_name == 'open-sync-folder':
            try:
                current_dir       = message.get('current_dir')
                sftp_dir          = message.get('sftp_dir')
                open_sync_folder( current_dir, sftp_dir, ckey)
            except Exception as e:
                log("open local sync folder failed for: {0}".format(e) )
                await websocket.send( json.dumps({
                    'name'    : 'sftp-message',
                    'info'    : "",
                    'message' : lt("open sync folder failed for: ")+"{}".format(e),
                }) )
                pass
            return
        if message_name == 'one-run-message':
            info      = message.get("info",'')
            command   = message.get("command",'')
            #print("deal one-run-message:",info, command)
            res = one_run_command(config, command)
            await websocket.send( json.dumps({
                'name'    : message.get("message_name",message_name),
                'info'    : info,
                'ckey'    : ckey,
                'out'     : res.get("out",''),
                'err'     : res.get("err",''),
            }) )
            return
        if message_name == "submit-task":
            if message.get("operation") == "check-task":
                await check_task(config, ckey, message, websocket)
            elif message.get("operation") == "stop-task":
                await stop_task(config, ckey, message, websocket)
                pass
            else:
                await submit_task(config, ckey, message, websocket)
                pass
            return
        if message_name == 'sftp-message':
            #print("get sftp message:", message)
            command      = message.get("command",None)
            #print("get sftp command:", command)
            if not command:
                log("sftp-message without command")
                return
            conn    = await get_sftp_connection(websocket, config, ckey, page_id )
            if not conn or not conn.get("sftp"):
                #print('send failed message type:',message.get("message_name",message_name))
                await websocket.send(json.dumps({
                    'name'     : message.get("message_name",message_name),
                    'info'     : 'connection_failed',
                    'ckey'     : 'ckey',
                    'message'  : lt('sftp connection to {0}:{1} cannot be established...\r\n',config.get("server_address","?"), config.get("server_port","22")),
                }))
                log("failed to get sftp connection record...\n")
                return
            sftp         = conn.get("sftp")
            result       = None
            try:
                sftp_dir        = message.get("sftp_dir")
                current_dir     = message.get("current_dir",[""])
                infos           = prepare_sftp_infos( current_dir, sftp_dir, ckey, conn )
                #print("get sftp infos:", infos)
                if command == 'item-delete':
                    sftp_delete_item(infos, sftp, message )
                    command  = "listdir"
                    pass
                elif command == 'file-upload':
                    result   = sftp_upload_file(infos, sftp, message)
                    command  = 'listdir'
                    pass
                elif command == 'file-download':
                    result   = sftp_download_file(infos, sftp, message)
                    command  = 'listdir'
                    pass
                elif command == 'prepare-files':
                    await sftp_prepare_files(infos, sftp, message, websocket)
                    return
                elif command == 'file-open':
                    sftp_open_file(infos, message)
                    return

                #commands without return will return listdir result
                if command == "listdir":
                    result = sftp_listdir(infos, ckey, sftp, message)
                    pass
                else:
                    log("undealing sftp message: {0}".format(message) )
                    pass
            except Exception as e:
                log("failed to execute sftp command: {0} : {1}".format(command,e))
                await websocket.send(json.dumps({
                    'name'     : message.get("message_name",message_name),
                    'ckey'     : ckey,
                    'info'     : 'sftp_command_failed',
                    'message'  : 'sftp failed to execute command: {0} \r\n'.format(command),
                }))
                #await close_sftp_connection(websocket, conn )
                traceback.print_exc()
                pass

            await websocket.send(json.dumps({
                'name'     : message.get("message_name",message_name),
                'command'  : command,
                'ckey'     : ckey,
                'result'   : result,
            }))
            return

        if message_name == 'shell-message':
            conn    = await get_ssh_connection(websocket, config, ckey, page_id )
            if not conn:
                log('send failed message of type: {0}'.format(
                    message.get("message_name",message_name))
                )
                await websocket.send(json.dumps({
                    'name'     : message.get("message_name",message_name),
                    'info'     : 'connection_failed',
                    'message'  : lt('ssh connection to {0}:{1} cannot be established...\r\n',config.get("server_address","?"), config.get("server_port","22")),
                }))
                log("failed to get ssh connection record ...\n")
                return

            #print("message recieved try deal with:", message )
            if message.get('operation',None) == 'resize_pty':
                cols = int( message.get('cols') )
                rows = int( message.get('rows') )
                #print("try resize to", cols, rows)
                try:
                    conn['channel'].resize_pty(width=cols, height=rows)
                except Exception as e:
                    log("resize pty failed for: {}".format(e) )
                    await close_ssh_connection(websocket, conn)
                    pass
                return

            #print('get input message: ', message)
            data = message.get('data',None)
            if data:
                #print("你好")
                #data = data.encode("utf-8").decode("unicode_escape")
                #print("send data to ssh:", data )
                try:
                    conn['channel'].send(data)
                except Exception as e:
                    log("send data failed for: {0}".format(e) )
                    await close_ssh_connection(websocket, conn)
                    pass
                pass
            return
        log("undealing message: {0}".format(message) )
    except Exception as e:
        traceback.print_exc()
        log("data processing exception raised for: {0}".format(e) )
        #print("set timer to close websocket conn in case of page refresh")
        if not TIMERS.get("ws_close_"+page_id):
            TIMERS["ws_close_"+page_id] = threading.Timer( WS_TIMEOUT, launch_close_websocket, [page_id])
            TIMERS["ws_close_"+page_id].start()
            pass
        return 'break'
    pass

def launch_data_processing(websocket, data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop( loop )
    loop.run_until_complete( data_processing(websocket, data))
    loop.close()
    pass

async def request_processing(websocket, path ):

    async def request():
        #print("\nsocket loop started")
        #print("\n met new request", websocket, path)
        while True:
            try:
                json_text = await websocket.recv()
                try:
                    data      = json.loads( json_text )
                except Exception as e:
                    log('decode json data {0} failed'.format(json_text))
                    log('exception: {0}'.format(e))
                    pass
                page_id   = data.get('page_id', '0')
                threading.Thread(
                    target=launch_data_processing,
                    args=[websocket, data]
                ).start()
                #time.sleep(0.05)
            except Exception as e:
                traceback.print_exc()
                log("request loop quit for: {0}".format(e) )
                #print("set timer to close websocket conn in case of page refresh")
                if not TIMERS.get("ws_close_"+page_id):
                    TIMERS["ws_close_"+page_id] = threading.Timer( WS_TIMEOUT, launch_close_websocket, [page_id])
                    TIMERS["ws_close_"+page_id].start()
                    pass
                #await websocket.close()
                break
            pass
        pass

    request_task = asyncio.create_task( request() )
    await request_task

    pass

def run_server(in_log_f=None): # in non-main thread
    #if in_log_f: log = in_log_f
    log("starting server for remote calculate on port {0}".format(port_term) )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop( loop )
    loop = asyncio.get_event_loop()

    try:
        server = websockets.serve(request_processing, server_address, port_term)
        loop.run_until_complete( server )
        loop.run_forever()
        log("server loop quited")
    except Exception as e:
        log("quit with error: {0}".format(e) )
        pass
    #print("task assigned")
    pass

def stop_server(lang='python'):
    log("try stop server")
    pass

def check_parent_pid():
    if not psutil: return
    while True:
        if not psutil.pid_exists( INFO['parent_pid'] ):
            log("no parent found. Quiting...")
            os._exit(1)
            pass
        time.sleep(0.05)
        pass

    pass


if __name__  == "__main__":
    try:
        INFO['parent_pid'] = int(sys.argv[-1])
        threading.Thread(target=check_parent_pid).start()
    except:
        INFO['parent_pid'] = -1
        log("not launched by parent process in manner")
        pass
    run_server()
