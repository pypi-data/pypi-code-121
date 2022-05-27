#######################################################################
#
# Copyright (C) 2021 David Palao
#
# This file is part of PacBio data processing.
#
#  PacBio data processing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBio data processing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBio data processing.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import sys
import time
import os
import datetime

import psutil


TIME_DELTA = 0.01


def catch_processes(*names, skip=None):
    ls = []
    for p in psutil.process_iter(["name", "exe", "cmdline"]):
        if skip and p.pid==skip:
            continue
        name_matches = p.info['name'] in names
        if name_matches:
            flag = p.info['name']
        exe_matches = p.info['exe'] and os.path.basename(p.info['exe']) in names
        if exe_matches:
            flag = p.info['exe']
        cmdline_matches = p.info['cmdline']
        if cmdline_matches:
            for arg in p.info['cmdline']:
                if any((name in arg) for name in names):
                    cmdline_matches = True
                    flag = p.info['cmdline']
                    break
            else:
                cmdline_matches = False
        if name_matches or exe_matches or cmdline_matches:
            ls.append((p.pid, flag, p))
    return ls


def process_time_series(*names, skip=None):
    start = time.time()
    procs = {datetime.datetime.now(): []}
    if len(names) == 0:
        return procs
    while True:
        try:
            now = time.time()-start
            procs[now] = catch_processes(*names, skip=skip)
            time.sleep(TIME_DELTA)
        except KeyboardInterrupt:
            break
    return procs


def main():
    me = psutil.Process()
    procs = process_time_series(*sys.argv[1:], skip=me.pid)
    for t, proc_info in procs.items():
        print(f"{t} :")
        for pid, flag, _ in proc_info:
            print(f"  [{pid}] {flag}")
        print()

if __name__ == "__main__":
    sys.exit(main())
    
