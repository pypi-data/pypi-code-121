#!/usr/bin/env python3

# Data Helpers

import re
import collections
import os
import sys
#import io
#import binascii
#import random
from datetime import datetime,timezone
import base64
import platform  # platform.node() -> hostname
# for yaml
#from ruamel.yaml.comments import CommentedMap
import ruamel.yaml
# for json
import json
# for xml
#import dicttoxml
import xmltodict
# self tools
import csv
import math
from pydan import run
from pydan.ansi import c

# repair LANG=C -> utf8
if(sys.getfilesystemencoding()=="ascii" and sys.getdefaultencoding()=="utf-8"):
	sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
cj={
	"none":c["none"],
	"header":c["orange"], # tree
	"group":c["lightblue"],
	"item":c["cyan"],
	"null":c["gray"],
	"date":c["violet"],
	"str":c["green"],
	"int":c["lightgreen"],
	"float":c["olive"],
	"bool":c["white"],
	"unk":c["red"],
	"varint":c["lightpink"],
	"varenv":c["pink"],
	"varcmd":c["red"],
	"err":c["lightred"],
	"binary":c["purple"],
	# bg
	"headerbg":c["graybg"], # col
}

def colprint(d,header=None,key=None,indent="",crop=True,format='tree',fields=None,fieldcolors=None,enum=False,keyname=None,title=None,emptyremove=False):
	if format=="tree":
		treeprint(d,header,key,indent,crop)
		return
	if format=="column":
		tableprint(d,header,fields=fields,fieldcolors=fieldcolors,enum=enum,keyname=keyname,title=title,emptyremove=emptyremove)
		return

def tableprint(datain,header=None,fields=None,fieldcolors=None,short=False,enum=False,keyname='key',title=None,emptyremove=False):
	if len(datain)==0: return
	columncolors=[
	"yellow",
	"lightblue",
	"pink",
	"cyan",
	"orange",
	"green",
	"salmon",
	"maroon",
	"red",
	"blue",
	"olive",
	"purple",
	"violet",
	"magenta",
	"lightpink",
	"lightorange",
	"lightcyan",
	"lightgreen",
	"lightred"
	]

	if type(datain) is dict:
		# Convert dict to list
		data=[]
		for k in [*datain]:
			dataline={}
			dataline.update({keyname:k})
			dataline.update(datain[k])
			data.append(dataline)
	else:
		data=datain

	reg_cropansi=re.compile("\x1b\\[[;\\d]*[A-Za-z]", re.VERBOSE)

	if fieldcolors is None and fields is None:
		# generate fields to print
		fields=list()
		for r in data:
			for k in r.keys():
				if k not in fields: fields.append(k)
		# generate default colors
		fieldcolors={}
		n=0
		for k in fields:
			fieldcolors[k]=columncolors[n]
			n=n+1
			if n==len(columncolors): n=0
	else:
		if fieldcolors is None:
			# generate fieldcolors
			fieldcolors={}
			n=0
			for k in fields:
				fieldcolors[k]=columncolors[n]
				n=n+1
				if n==len(columncolors): n=0
		else:
			# extract fields from fieldcolor keys
			fields=list(fieldcolors.keys())

	#if count:
	#	fields.insert(0, {"n":"1"})

	# bool replace
	for d in data:
		for var in fields:
			if d.get(var) and isinstance(d[var], bool):
				if d[var]:
					d[var]="Yes"
				else:
					d[var]="No"

	# emptyremove
	deletefields=list()
	if emptyremove:
		for var in fields:
			isnull=True
			for d in data:
				if d.get(var) is not None:
					isnull=False
			if isnull:
				deletefields.append(var)
	for f in deletefields:
		if f in fields:
			fields.remove(f)

	# calculate column sizes
	sizes=None
	if not short:
		sizes={}

		# fields header size
		for var in fields:
			sizes[var]=len(var)

		# value size
		for d in data:
			for var in fields:
				if d.get(var) is not None:
					barestr=reg_cropansi.sub("", str(d[var]))
					varsize=len(barestr)
					if varsize>sizes[var]:
						sizes[var]=varsize

	# enumeration column
	enumsize=0
	if enum:
		enumsize=1
		if len(data)>=10: enumsize=2
		if len(data)>=100: enumsize=3
		n=0

	# draw title
	if title is not None:
		width=0
		if enumsize>0: width+=enumsize+1
		for var in fields: width+=sizes[var]+1
		pad1=' '*math.floor((width-len(title))/2)
		pad2=' '*math.ceil((width-len(title))/2)
		#print(f"\x1b[4m\x1b[48;5;17m\x1b[1m{pad1}{title}{pad2}\x1b[0m")
		print(f"\x1b[48;5;17m\x1b[1m{title}{pad1}{pad2}\x1b[0m")

	# draw fields header up
	if header=="up":
		tableprint_column_header(fields, sizes, enumsize)

	for d in data:
		if enum:
			n+=1
			nstr=str(n).rjust(enumsize)+" "
			print(nstr, end="")
		for var in fields:
			f=d.get(var)
			if f is None: f="·"
			strf=str(f)
			if fieldcolors.get(var):
				print(c.get(fieldcolors[var]), end="")
			else:
				print(c.get("none"), end="")
			print(strf,end="")
			if sizes is None:
				print(c.get("none")+" ",end="")
			else:
				barestr=reg_cropansi.sub("", strf)
				s=sizes[var]-len(barestr)
				if len(strf)==1 and ord(strf[0])>10000: s-=1 # wide char
				for f in range(0,s+1):
					print(" ",end="")
		print("\x1b[0m")

	# draw fields header down
	if header=="down":
		tableprint_column_header(fields, sizes, enumsize)

def tableprint_column_header(fields, sizes, enumsize=0):

		#print("\x1b[48;5;237m",end="")
		print(cj["headerbg"],end="")

		if enumsize>0:
			print("#".ljust(enumsize)+" ", end="")

		for var in fields:
			print("\x1b[37m",end="")
			print(var,end="")
			if sizes is None:
				print(c.get("none")+" ",end="")
			else:
				for f in range(0,sizes[var]-len(var)+1):
					print(" ",end="")
		print("\x1b[0m")

#{{{ colprint: Imprime un dict por pantalla con colores según el tipo de datos
def treeprint(d,header=None,key=None,indent="",crop=True):
	indentchars="    "
	if(header): print(cj["header"]+header+cj["none"]);indent=indent+indentchars

	# Si es diccionario iteramos
	if isinstance(d,dict) or isinstance(d,collections.OrderedDict):  # or type(d)==CommentedMap):
		#if(type(d)==dict or type(d)==collections.OrderedDict or type(d)==CommentedMap):
		#if hasattr(d,'__iter__') and type(d)!=str:
		if key is not None: print(f"{indent}{cj['group']}{key}:{cj['none']}"); indent+=indentchars
		if len(d)==0: print(f"{indent}{cj['null']}empty{cj['none']}")
		else:
			for k in d: treeprint(d[k], key=k, indent=indent)
		return

	# Si es lista listamos con [indice]
	#if(type(d)==list):
	#	i=0
	#	print(indent+cj["group"]+key+":"+cj["none"])
	#	indent=indent+indentchars
	#	# Lista de strings
	#	#if type(key[0])==str:
	#	#	for k in d:
	#	#		print(indent+cj["item"]+"["+str(i)+"]: "+cj["none"], end='')

	#	#for k in d:
	#	#	#print(indent+cj["group"]+key+"["+str(i)+"]:"+cj["none"])
	#	#	#colprint(k, indent=indent+indentchars)
	#	#	#print(indent+cj["item"]+"["+str(i)+"]: "+cj["none"], end='')
	#	#	colprint(k, indent=indent+cj["item"]+"["+str(i)+"]: ")
	#	#	i=i+1
	#	#	#print(k);
	#
	#	for k in d:
	#		#print(indent+cj["group"]+key+"["+str(i)+"]:"+cj["none"])
	#		print(indent+cj["group"]+"["+str(i)+"]:"+cj["none"])
	#		colprint(k, indent=indent+indentchars)
	#	#	#print(indent+cj["item"]+"["+str(i)+"]: "+cj["none"], end='')
	#		#colprint(k, indent=indent+cj["item"]+"["+str(i)+"]: ")
	#		i=i+1
	#		#print(k);
	#	return

	if isinstance(d,list) or isinstance(d,tuple):
		# Vacia
		if len(d)==0:
			if(key is not None):
				print(indent+cj["group"]+key+"[]: "+cj["null"]+"empty"+cj["none"])
			else:
				print(indent+cj["null"]+"empty"+cj["none"])
			return

		# Lista de tipos soportados
		if type(d[0]) in [str,int,float,datetime]:
			i=0
			if key is not None:
				print(indent+cj["group"]+key+":"+cj["none"])
				for k in d:
					treeprint(str(k), key="["+str(i)+"]", indent=indent+indentchars)
					i+=1
			else:
				for k in d:
					treeprint(str(k), key="["+str(i)+"]", indent=indent)
					i+=1
			return

		#for k in d:
		#	#print(indent+cj["group"]+key+"["+str(i)+"]:"+cj["none"])
		#	#colprint_tree(k, indent=indent+indentchars)
		#	#print(indent+cj["item"]+"["+str(i)+"]: "+cj["none"], end='')
		#	colprint_tree(k, indent=indent+cj["item"]+"["+str(i)+"]: ")
		#	i=i+1
		#	#print(k);

		# Lista de objetos
		if(type(d[0])==dict or type(d[0])==collections.OrderedDict):
			i=0
			for k in d:
				if key is None: key=""
				print(indent+cj["group"]+key+"["+str(i)+"]:"+cj["none"])
				treeprint(k, indent=indent+indentchars)
				i=i+1
			return

		print(cj["err"]+"¿list of "+type(d[0]).__name__+"?"+cj["none"])
		return
		#print("unknown "+type(d).__name__)
		#return

	# Mostramos key
	if(key is not None): print(indent+cj["item"]+str(key)+": ", end='')
	else: print(indent, end='')

	# Mostramos valor
	#t=type(d)
	if isinstance(d,str):
		p=re.compile("\$([a-zA-Z0-9_]*)\$")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\$"+k+"\$", cj["varenv"]+"$"+k+"$"+cj["str"], d)
		p=re.compile("\%([a-zA-Z0-9_]*)\%")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\%"+k+"\%", cj["varint"]+"%"+k+"%"+cj["str"], d)
		p=re.compile("\(\(([^)]*)\)\)")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\(\(.*\)\)", cj["varcmd"]+"(("+k+"))"+cj["str"], d)
		if crop and len(d)>4000:
			print(cj["binary"]+"###DATA-"+str(len(d))+"###"+cj["none"])
		else:
			print(cj["str"]+d+cj["none"])
	elif isinstance(d,datetime):
		dtstr=re.sub("\+00:00", "Z", d.isoformat())
		#dtstr=d.__str__()
		print(cj["date"]+dtstr+cj["none"])
	elif isinstance(d,int):
		print(cj["int"]+str(d)+cj["none"])
	elif isinstance(d,float):
		print(cj["float"]+str(d)+cj["none"])
	elif isinstance(d,bool):
		print(cj["bool"]+str(d)+cj["none"])
	#	elif(t==list):
	#		print
	#		for i in d:
	#			colprint_tree(i,header="x",indent=indent)
	#			#print(indent+indentchars+cj["str"]+i)
	#			#print(d)
	elif d is None:
		print(cj["null"]+"null"+cj["none"])
	else:
		print(f"{cj['err']}¿{str(d.__name__)}?{cj['none']}")
#}}}

# Por cada item en d reemplaza $var$ por el valor de la variable en la lista varlist
#{{{ replacevars
def replacevarsold(d, varlist, unknownempty=False, emptyremove=False, unknownnull=False, emptynull=False, __debugiter=0):
	#o=collections.OrderedDict()
	o={}
	#for di in range(0,__debugiter): print("    ", end="")
	#print("replacevars:")
	__debugiter=__debugiter+1
	for k in d:
		#for di in range(0,__debugiter): print("    ", end="")
		#print(f"- {k} [{type(d[k]).__name__}]")
		if type(d[k])==dict or type(d[k])==collections.OrderedDict:
			d[k]=replacevarsold(d[k], varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter)
			o[k]=d[k]
			continue
		elif type(d[k])==list:
			o[k]=[]
			__debugiter=__debugiter+1
			for i in d[k]:
				for di in range(0,__debugiter): print("    ", end="")
				#print(f"* item {i}")
				o[k].append(replacevarsold(i, varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter))
			continue
		else:
			if(type(d[k])==str):
				#if(d[k][0]=='$'):
				#	var=d[k][1:-1]
				#	v=varlist.get(var)
				#	if(v): o[k]=v
				#else:
				#	o[k]=d[k]

				# Buscamos variables en varlist
				p=re.compile("\\$([a-zA-Z0-9_]*)\\$")
				vars=set(p.findall(d[k]))
				# No hay variables
				if vars is None:
					o[k]=d[k]
					continue
				# Hay variables
				for sk in vars:
					val=varlist.get(sk)
					if val is None:
						if(unknownempty): val=""
						else:
							if(unknownnull):
								if emptynull: val="$null$"
								else: val="null"
							else:
								continue
					#if d[k]==f"${sk}$":  # python 3.6
					if d[k]=="$"+sk+"$":  # python 3.6
						# si el valor es exacto ("$var$"), reemplazamos por el tipo de objeto de varlist
						d[k]=val
					else:
						# reemplazamos dentro del string
						d[k]=re.sub("\\$"+sk+"\\$", str(val), d[k])

				if(d[k]=="$null$" and emptynull): continue
				if(d[k]=="" and emptyremove): continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o
#}}}

def replacevars(data, varlist, flags=[], __debugiter=0):
	__debug=False
	#__debug=True

	unkvar=re.compile("^\\$([a-zA-Z0-9_]*)\\$$")

	if __debug:
		for di in range(0,__debugiter): print("    ", end="")
		print("\033[1;33mreplacevars:\033[0m")
		__debugiter=__debugiter+1

	if type(data)==str:
		return replacevars_str(data, varlist, __debugiter=__debugiter)

	if type(data)==dict:
		if __debug:
			for di in range(0,__debugiter): print("    ", end="")
			print("\033[32mdict:\033[0m")
			__debugiter=__debugiter+1
		o={}
		for k,v in data.items():
			if __debug:
				for di in range(0,__debugiter): print("    ", end="")
				#print(f"\033[33m- Item '{k}' [{type(data[k]).__name__}]\033[0m")  # python 3.6
				print("\033[33m- Item '"+k+"' ["+type(data[k]).__name__+"]\033[0m")  # python 3.6
			if type(v)==str:
				r=replacevars_str(v, varlist, __debugiter=__debugiter)
				add=True
				if "nullremove" in flags and r is None and v is not None: add=False
				if "emptyremove" in flags and r=="" and v!="": add=False
				if "emptynull" in flags and r=="" and v!="": r=None
				if "unkremove" in flags and type(r)==str and unkvar.match(r): add=False
				if "unkempty" in flags and type(r)==str and unkvar.match(r): r=""
				if "unknull" in flags and type(r)==str and unkvar.match(r): r=None
				if add: o[k]=r
			else:
				o[k]=replacevars(v, varlist, flags=flags, __debugiter=__debugiter)
		return o

	if type(data)==list:
		o=[]
		if __debug:
			for di in range(0,__debugiter): print("    ", end="")
			print("\033[32mlist:\033[0m")
			__debugiter=__debugiter+1
		for k in data:
			if __debug:
				for di in range(0,__debugiter): print("    ", end="")
				#print(f"\033[33m- Item '{k}' [{type(k).__name__}]\033[0m")
				print("\033[33m- Item '"+k+"' ["+type(k).__name__+"]\033[0m")
			oi=replacevars(k, varlist, flags=flags, __debugiter=__debugiter)
			o.append(oi)
		return o

	if type(data)==set:
		o=set()
		if __debug:
			for di in range(0,__debugiter): print("    ", end="")
			print("\033[32mset:\033[0m")
			__debugiter=__debugiter+1
		for k in data:
			if __debug:
				for di in range(0,__debugiter): print("    ", end="")
				#print(f"\033[33m- Item '{k}' [{type(k).__name__}]\033[0m")
				print("\033[33m- Item '"+k+"' ["+type(k).__name__+"]\033[0m")
			oi=replacevars(k, varlist, flags=flags, __debugiter=__debugiter)
			o.add(oi)
		return o

	# unknown!
	if __debug:
		for di in range(0,__debugiter): print("    ", end="")
		#print(f"\033[1;31m¿{type(data).__name__}?\033[0m")
		print("\033[1;31m¿"+type(data).__name__+"?\033[0m")
	return data

#	for k in d:
#		for di in range(0,__debugiter): print("    ", end="")
#		print(f"\033[33m- {k} [{type(d[k]).__name__}]\033[0m")
#		if type(d[k])==dict or type(d[k])==collections.OrderedDict:
#			d[k]=replacevars2(d[k], varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter)
#			o[k]=d[k]
#			continue
#		elif type(d[k])==list:
#			o[k]=[]
#			__debugiter=__debugiter+1
#			for i in d[k]:
#				for di in range(0,__debugiter): print("    ", end="")
#				print(f"* item {i}")
#				o[k].append(replacevars2(i, varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter))
#			continue
#		else:
#			if(type(d[k])==str):
#				o[k]=replacevars2_str(d[k], varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter)
#	return o
#}}}

def replacevars_str(data, varlist, __debugiter=0):
	__debug=False
	#__debug=True
	if __debug:
		for di in range(0,__debugiter+1): print("    ", end="")
		#print(f"\033[34mreplacevars2_str: '{data}'\033[0m", end="")
		print("\033[34mreplacevars2_str: '"+data+"'\033[0m", end="")
	out=data
	p=re.compile("\\$([a-zA-Z0-9_]*)\\$")
	vars=p.findall(data)
	# No hay variables
	if len(vars)==0:
		if __debug:
			print(" (no vars)", end="")
		out=data
	else:
		if __debug:
			print(" (vars found)", end="")
		# Hay variables
		for sk in vars:
			if __debug:
				print(" (repl "+sk+")", end="")
			if sk not in varlist: continue
			val=varlist.get(sk)
			#if val is None:
			#	if(unknownempty): val=""
			#	else:
			#		if(unknownnull):
			#			if emptynull: val="$null$"
			#			else: val="null"
			#		else:
			#			continue

			# TODO: no borrar variables que no existen!
			if data=="$"+sk+"$":
				# si el valor es exacto ("$var$"), reemplazamos por el tipo de objeto de varlist
				out=val
			else:
				# reemplazamos dentro del string
				out=re.sub("\\$"+sk+"\\$", str(val), out)

		#if(out=="$null$" and emptynull): out=None
		#if(out=="$null$"): out=None
		#if(out=="" and emptyremove): out=None  # ???? TODO
	#if out=="#null#": out=None
	if __debug: print("\033[34m -> '"+out+"' ["+type(out).__name__+"]\033[0m")
	return out
#}}}

# Por cada item en d reemplaza $e$var$ por variable de entorno
#{{{ replaceenv
def replaceenv(d, unknownempty=False, emptyremove=None):
	o=collections.OrderedDict()
	for k in d:
		if(type(d[k])==dict or type(d[k])==collections.OrderedDict):
			d[k]=replaceenv(d[k], unknownempty=unknownempty, emptyremove=emptyremove)
			o[k]=d[k]
			continue
		else:
			if(type(d[k])==str):
				p=re.compile("\$e$([a-zA-Z0-9_]*)\$")
				vars=set(p.findall(d[k]))
				# No hay variables
				if(vars is None):
					o[k]=d[k]
					continue
				# Hay variables
				for sk in vars:
					if (sk=="HOSTNAME"): val=platform.node()
					else: val=os.environ.get(sk)
					if(val is None):
						if(unknownempty): val=""
						else: continue
					d[k]=re.sub("\$e\$"+sk+"\$", val, d[k])

				if(d[k]=="" and emptyremove): continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o
#}}}

# Por cada item en d reemplaza ((cmd)) por la ejecución de cmd
# Por cada item en d reemplaza $b$file$ por el fichero en b64
# Por cada item en d reemplaza $t$file$ por el contenido del fichero
#{{{ runvars
def runvars(d, unknownempty=False, emptyremove=None):
	o=collections.OrderedDict()
	for k in d:
		if(type(d[k])==dict or type(d[k])==collections.OrderedDict):
			d[k]=runvars(d[k], unknownempty=unknownempty, emptyremove=emptyremove)
			o[k]=d[k]
			continue
		else:
			if(type(d[k])==str):
				modified=False

				# Comando a ejecutar
				r_buscacmd=re.compile("\(\((.*)\)\)")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars is None):
					o[k]=d[k]
				#	continue
				else:
					modified=True
					# Hay variables
					for sk in vars:
						# b|fichero -> base64 fichero
						#sk=re.sub(r"^t\|(.*)$", r"cat '\g<1>'", sk)
						sk=re.sub(r"^b\|(.*)$", r"cat '\g<1>'|base64 -w0", sk)
						pars=["bash","-c",sk]
						ex=run.cmd(pars)
						#if ex.retcode==0:
						val=ex.out
						if(val is None):
							if(unknownempty): val=""
							else: continue
						#d[k]=re.sub("\(\("+sk+"\)\)", val, d[k])
						d[k]=re.sub("\(\(.*\)\)", val, d[k])

				# Fichero base64
				r_buscacmd=re.compile(r"$b$(.*)$")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars is None):
					o[k]=d[k]
				else:
					modified=True
					# Hay variables
					for sk in vars:
						f=open(sk, "rb")
						fdata=base64.b64encode(f.read()).decode()
						d[k]=re.sub(r"$b$.*$", fdata, d[k])

				# Fichero directo
				r_buscacmd=re.compile(r"$t$(.*)$")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars is None):
					o[k]=d[k]
				else:
					modified=True
					# Hay variables
					for sk in vars:
						f=open(sk, "r")
						fdata=f.read()
						d[k]=re.sub(r"$t$.*$", fdata, d[k])

				if modified and d[k]=="" and emptyremove: continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o
#}}}

# Values of dict contained in another dict
def contained(d1, d2):
	for k in d1:
		if d2.get(k) is None: return False
		if(type(d1[k])==dict or type(d1[k])==collections.OrderedDict):
			if not contained(d1[k], d2[k]): return False
		else:
			if d1[k]!=d2[k]: return False
	return True

# csv tools
def tocsv(data,sep=None,fields=None):

	if sep is None: sep='|'
	if type(sep) == int: sep='|'
	out=""

	if fields is None:
		fields=[]
		for row in data:
			for k in row:
				if k not in fields:
					fields.append(k)

	first=True
	for var in fields:
		if first: first=False
		else: out=out+sep
		out=out+var

	for row in data:
		out=out+"\n"
		first=True
		for var in fields:
			if first: first=False
			else: out=out+sep
			val=row.get(var)
			strval=str(val).replace("\n", "\\n")
			if val is None: val=""
			out=out+strval
	return out

#{{{ xml tools
# XML -> dict
def fromxml(xmldata):
	# TODO: funciona?
	#return dicttoxml.parse("<xml>"+xmldata+"</xml>", disable_entities=True)["xml"]
	return xmltodict.parse(xmldata)
def readxml(xmlfile):
	f=open(xmlfile,"rt")
	xml=f.read()
	data=fromxml(xml)
	return data
#}}}

#{{{ json tools
def fromjson(jsondata):
	return json.loads(jsondata,object_pairs_hook=json_parser_hook)

def readjson(jsonfile):
	f=open(jsonfile,"rt")
	json=f.read()
	data=fromjson(json)
	return data

def tojson(data,indent=None):
	return json.dumps(data,separators=(',',':'),default=json_serializer_hook,indent=indent)

def writejson(data,filename,tabs=0,spaces=0):
	f=open(filename, "w")
	indent=None
	if spaces!=0:
		indent=spaces
	if (tabs==1):
		indent='\t'
	jsondata=tojson(data,indent=indent)
	f.write(jsondata)
	f.write("\n")
	f.close()

# json -> dict
def json_parser_hook(js):
	#out=collections.OrderedDict(js)
	out=dict(js)
	for (key, value) in out.items():
		# Hora con timezone sin milisegundos
		try:
			dt=re.sub("Z$", "UTC",value)
			dt=datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%Z")
			#dt=dt.replace(tzinfo=datetime.timezone(datetime.timedelta(0)))
			dt=dt.replace(tzinfo=timezone.utc)
			out[key]=dt
			continue
		except Exception: pass
		# Hora con timezone con milisegundos
		try:
			dt=re.sub("Z$", "UTC",value)
			dt=datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%Z")
			dt=dt.replace(tzinfo=timezone.utc)
			out[key]=dt
			continue
		except Exception: pass
		# Hora sin timezone sin milisegundos
		try:
			out[key]=datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
			continue
		except Exception: pass
		# Hora sin timezone con milisegundos
		try:
			out[key]=datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
			continue
		except Exception: pass
	return out

# dict -> json
def json_serializer_hook(o):
	if isinstance(o, datetime):
		return re.sub("\+00:00", "Z", o.isoformat())

#}}}

#{{{ yaml tools
def fromrawyaml(yamldata):
	yaml=yamldata.replace("\t", "  ")
	data=ruamel.yaml.load(yaml, Loader=ruamel.yaml.Loader)
	return data

def readrawyaml(filename):
	# Cargar fichero yaml en dict
	import collections
	ruamel.yaml.representer.RoundTripRepresenter.add_representer(
	collections.OrderedDict, ruamel.yaml.representer.RoundTripRepresenter.represent_ordereddict)
	f=open(filename,"rt")
	yamldata=f.read()
	data=fromrawyaml(yamldata)
	return data


def readyaml(filename):

	def yaml_include(loader, node):
		subdata=None
		if os.path.isfile(node.value):
			f=node.value
			with open(f, 'r') as s: subdata=ruamel.yaml.load(s, Loader=ruamel.yaml.Loader)
		else:
			path=os.path.dirname(filename)
			f=path+os.path.sep+node.value
			if os.path.isfile(f):
				with open(f, 'r') as s: subdata=ruamel.yaml.load(s, Loader=ruamel.yaml.Loader)
		return subdata

	ruamel.yaml.add_constructor('!include', yaml_include)
	with open(filename, 'r') as f: data=ruamel.yaml.load(f, Loader=ruamel.yaml.Loader)
	if data is None: data={}

	# Procesamos tag antiguo yaml-include
	if data.get("yaml-include"):
		for f in data["yaml-include"]:
			if os.path.isfile(f):
				with open(f, 'r') as s: subdata=ruamel.yaml.load(s, Loader=ruamel.yaml.Loader)
				data.update(subdata)
			else:
				path=os.path.dirname(filename)
				f=path+os.path.sep+f
				if os.path.isfile(f):
					with open(f, 'r') as s: subdata=ruamel.yaml.load(s, Loader=ruamel.yaml.Loader)
					data.update(subdata)
		data.pop("yaml-include")

	return data

def yamlupdate(filename,var,val,node=None):
	yaml=ruamel.yaml.YAML()
	yaml.width=4096
	f=open(filename,"r")
	data=yaml.load(f.read())
	f.close()
	datamod=data
	if node:
		for n in node:
			datamod=datamod.get(n)
	datamod[var]=val
	f=open(filename, "w")
	yaml.dump(data, f)
	f.close()

def writeyaml(data,filename):
	yaml=ruamel.yaml.YAML()
	yaml.width=4096
	f=open(filename, "w")
	yaml.dump(data, f)
	f.close()

#}}}

#{{{ csv tools
# csv -> dict
def fromcsv(csvdata, delimiter=';', header=True, idfield=None):
	# TODO: header=False
	data=dict()
	csv_reader=csv.reader(csvdata.splitlines(), delimiter=';')
	headerfields=next(csv_reader)
	id=0
	for row in csv_reader:
		obj=dict()
		for pos,field in enumerate(headerfields): obj[field]=row[pos]
		if idfield:
			if len(obj[idfield]): data[obj[idfield]]=obj
		else:
			data[id]=obj
		id+=1
	return data

def readcsv(csvfile, delimiter=';', header=True, idfield=None):
	with open(csvfile,"rt") as file: csvdata=file.read()
	data=fromcsv(csvdata, delimiter, header, idfield)
	return data
#}}}
