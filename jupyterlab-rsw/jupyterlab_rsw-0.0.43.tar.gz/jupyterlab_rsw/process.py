'''
    process.ts
 
    Copyright (C) 2022 by RStudio, PBC

'''

from jupyterlab_rsw.constants import PROC_DIR, COMMANDS_TO_SKIP, ARGS_TO_SKIP

import os
import re
import subprocess
import threading
from typing import List, Dict

exit_watchers: Dict[int, subprocess.Popen] = {}

class Process:
    def __init__(self, pid, name, args, inodes, wd):
        self.pid: int = int(pid)
        self.name: str = name
        self.args: List[str] = args
        self.inodes: List[int] = [int(i) for i in inodes]
        self.wd: str = wd

def cleanup_watchers():
    for value in exit_watchers.values:
        value.kill(9)

def add_on_exit_thread(on_exit, popen_args):
    def run_in_thread(on_exit, popen_args):
        proc = subprocess.run(*popen_args)
        on_exit()
        return
    thread = threading.Thread(target = run_in_thread, args=(on_exit, popen_args))
    thread.start()
    # returns immediately after the thread starts
    return thread
    
def watch_for_exit(pid, on_exit, args):
  if pid not in exit_watchers:
      def exit_callback():
          on_exit(*args)
          exit_watchers.pop(pid)
      exit_watcher = add_on_exit_thread(exit_callback, [['/bin/bash', '-c', f'while ps hp {pid}; (( "$?" == "0" )); do sleep 3; done']])
      exit_watchers[pid] = exit_watcher

def kill_process(pid):
    subprocess.Popen(['/bin/bash', '-c', f'kill {pid}'])

async def get_processes() -> List[Process]:
    observed_inodes: Dict[int, List[int]] = {}
    processes: List[Process] = [] 
    for entry in os.scandir(PROC_DIR):
        if entry.is_dir() and entry.name.isnumeric():
            proc = await get_process(entry.name)
            if proc is not None:
                processes.append(proc)
                for inode in proc.inodes:
                    if inode in observed_inodes:
                        observed_inodes[inode].append(proc.pid)
                    else:
                        observed_inodes[inode] = [proc.pid]
    mapped_procs: Dict[int, Process] = {}
    for proc in processes:
        mapped_procs[proc.pid] = proc
    processes = await filter_inodes(mapped_procs, observed_inodes)
    return processes

def get_inodes(proc_path: str) -> List[int]:
    inodes: List[int] = []
    path = f"{proc_path}fd/"
    
    for entry in os.scandir(path):
        if entry.is_symlink():
            link = os.readlink(entry.path)
            reg_match = re.compile('socket:\\[([^\\]]*)\\]').match(link)
            if reg_match:
                inode = reg_match[1]
                # Don't allow duplicates
                if inode not in inodes:
                    inodes.append(inode)
    return inodes

async def get_parent_pid(pid: int) -> int:
    ppid_field: int = 3
    stat_path: str = f"{PROC_DIR}{pid}/stat"

    try:
        with open(stat_path) as f:
            data = f.read()
    except:
        return
    
    stat_fields: List[str] = data.split()
    if len(stat_fields) <= ppid_field:
        print(f'Unable to get parent ID of process because {stat_path} could not be parsed - too few fields.')
        return

    if not stat_fields[ppid_field].isnumeric():
        print(f'Unable to get parent ID of process because {stat_path} could not be parsed - ppid {stat_fields[ppid_field]} was not a number.')
        return
    return int(stat_fields[ppid_field])

async def get_parent_pid_tree(pid: int, ppids: List[int] = []) -> List[int]:
    ppid = await get_parent_pid(pid)
    if ppid is not None and ppid != 0 and ppid != '0':
        ppids.append(ppid)
        return await get_parent_pid_tree(ppid, ppids)
    else:
        return ppids

async def get_process(pid: int) -> Process: 
    proc_path = PROC_DIR + str(pid) + '/'
    try: 
        stat_info = os.stat(proc_path)
        # only retrieve processes that belong to current user
        if stat_info.st_uid == os.geteuid():
            # Get the command and args from the command line file
            with open(f'{proc_path}cmdline') as f:
                args = list(filter(lambda value: value != '', f.read().split('\0')))
            cmd = args.pop(0)
            wd = os.readlink(f'{proc_path}cwd')
    
            if not should_skip_process(cmd, args):
                # Get the inode values and return the Process.
                # We're only looking for processes that have at least one open socket.
                inodes = get_inodes(proc_path)
                if len(inodes) > 0:
                    return Process(pid, cmd, args, inodes, wd)
    except:
        pass # don't bother logging errors

async def filter_inodes(processes: Dict[int, Process], observed_inodes: Dict[int, List[int]]) -> List[Process]:
    for inode, pids in observed_inodes.items():
      # Only worry about duplicates.
      pids = [int(i) for i in pids]
      if len(pids) > 1:
          for pid in pids:
              ppids = await get_parent_pid_tree(pid)
              if len(list(filter(lambda v: v in ppids, pids))) > 0 and pid in processes:
                  processes[pid].inodes.remove(inode)
    return list(processes.values())

def should_skip_process(name: str, args: List[str]) -> bool:
    def format_match(values: List[str]) -> re.match:
        sep = '|'
        return re.compile('(' + sep.join(values) + ')')
    
    if name in COMMANDS_TO_SKIP:
        return True
    
    for value in args:
        if format_match(ARGS_TO_SKIP).match(value):
            return True

    return False
