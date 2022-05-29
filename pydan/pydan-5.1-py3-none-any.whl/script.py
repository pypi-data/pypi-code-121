#!/usr/bin/env python3

import sys
import os

# Directorio del script principal
#scriptdir=sys.path[0]

# Cambiamos al directorio del script principal
#os.chdir(scriptdir)

# Utilizamos scriptdir/lib como path para los import
#sys.path.insert(1,scriptdir+'/lib')

# Cambiamos el nombre del proceso al del script si está disponible setproctitle
try:
	import setproctitle
	setproctitle.setproctitle(os.path.basename(sys.argv[0]))
except ImportError:
	pass

# Excepciones coloreadas
try:
	import colored_traceback.always # noqa
except ImportError:
	pass

# Exportamos scriptdir al script principal
#import __main__
#__main__.scriptdir=scriptdir

def parsecmdline_old():
	cmdline={}
	cmdline["params"]=[]
	cmdline["options"]={}
	i=0
	while i < len(sys.argv)-1:
		i+=1
		s=sys.argv[i]
		if '=' in s:
			keyval=s.split("=")
			cmdline["options"][keyval[0]]=keyval[1]
		elif s[0]=='-':
			#i+=1
			#val=sys.argv[i]
			#key=s[1:]
			#if (key[0]=='-'):
			#	key=key[1:]
			#cmdline["options"][key]=val
			p=s[1:]
			if (p[0]=='-'):
				p=p[1:]
			if '=' in p:
				keyval=p.split("=")
				cmdline["options"][keyval[0]]=keyval[1]
			else:
				cmdline["options"][p]=1
		else:
			cmdline["params"].append(s)
	if not cmdline["params"]:
		cmdline["cmd"]=""
	else:
		cmdline["cmd"]=cmdline["params"][0]
	return cmdline

# ¿?
#    cmdline=script.parsecmdline2(
#        cmds={
#            "h:help":[],"t:token":[],"cl:configlist":[],
#            "ul:userlist":[],"ulraw":[],"ug:userget":[],"us:userset":[],"ua:useradd":[],"ud:userdel":[],
#            "ll:liclist":[],"la:licadd":[],"ld:licdel":[]
#        },
#        opts=["r:raw"],
#        multiopts=["o:out"]
#    )

def parsecmdline(suboptions=[]):
	cmdline={}
	# command0 command1 command2 param1=one param2=two -option -option2=other --option3 another
	cmdline["cmd"]=[]
	cmdline["par"]={}
	cmdline["opt"]={}
	i=0
	while i < len(sys.argv)-1:
		i+=1
		s=sys.argv[i]
		if s[0]!='-':
			if '=' in s:
				keyval=s.split("=")
				cmdline["par"][keyval[0]]=keyval[1]
			else:
				cmdline["cmd"].append(s)
		elif s[0]=='-':
			if s[1]=='-':
				i+=1
				val=sys.argv[i]
				key=s[2:]
				cmdline["opt"][key]=val
			else:
				p=s[1:]
				if (p[0]=='-'):
					p=p[1:]
				if '=' in p:
					keyval=p.split("=")
					cmdline["opt"][keyval[0]]=keyval[1]
				else:
					cmdline["opt"][p]=1
	if not cmdline["cmd"]:
		cmdline["command"]=""
	else:
		cmdline["command"]=cmdline["cmd"][0]
	return cmdline

class CMDLine:
	cmd=[]
	par={}
	opt={}
	command=""

def parsecmdline2(suboptions=[]):
	cmdline=CMDLine
	# command0 command1 command2 param1=one param2=two -option -option2=other --option3 another
	i=0
	while i < len(sys.argv)-1:
		i+=1
		s=sys.argv[i]
		if s[0]!='-':
			if '=' in s:
				keyval=s.split("=")
				cmdline.par[keyval[0]]=keyval[1]
			else:
				cmdline.cmd.append(s)
		elif s[0]=='-':
			if s[1]=='-':
				i+=1
				val=sys.argv[i]
				key=s[2:]
				cmdline.opt[key]=val
			else:
				p=s[1:]
				if (p[0]=='-'):
					p=p[1:]
				if '=' in p:
					keyval=p.split("=")
					cmdline.opt[keyval[0]]=keyval[1]
				else:
					cmdline.opt[p]=1
	if len(cmdline.cmd):
		cmdline.command=cmdline.cmd[0]
	return cmdline
