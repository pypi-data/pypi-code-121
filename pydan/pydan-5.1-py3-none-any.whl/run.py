#!/usr/bin/env python3

import subprocess
import types
import sys
import os
import time

def cmd(cmd):
	ret=types.SimpleNamespace()

	if sys.platform.startswith('win'):
		cmdproc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x00000200)
	else:
		cmdproc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=os.setpgrp)
	t1=time.time()
	binout,binerr=cmdproc.communicate()
	t2=time.time()
	ret.time=t2-t1
	ret.out=binout.decode().rstrip()+binerr.decode().rstrip()
	ret.retcode=cmdproc.returncode
	return ret
