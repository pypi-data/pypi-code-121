#!/usr/bin/env python3

import os
import datetime
import platform
import threading
import functools

# Niveles de log
NONE = 0
TRACE = 1
DEBUG = 2
INFO = 3
WARN = 4
ERROR = 5
FATAL = 6
ALL = 7
levelstr = [ "NONE ", "TRACE", "DEBUG", "INFO ", "WARN ", "ERROR", "FATAL", "ALL  " ]

class chars:
	vline="│ "
	groupstart="╭╸ "
	groupend="╰╸ "
	groupbreak="╰× "
	ggroupsingle="╶╸ "
	ggroupsinglebreak="╶× "

# Variables por defecto
level=NONE
expandlevel=DEBUG
output=None
context=None

# Variables precalculadas
hostname=platform.node()
pidstr=str(os.getpid())

# tlist es una lista de hilos de la aplicación, debido a que son muy largos los simplificamos
tlist={}
# utilizamos threading local para establecer variables independientes a cada hilo
tloc=threading.local()

SELFDEBUG=False

class LogFlow:

	class Group:
		def __init__(self, lvl, name, expand=None, parent=None):
			if SELFDEBUG:
				print(f"new Group: name={name} expand={expand}")
			self.lvl=lvl
			self.name=name
			self.expand=expand
			self.parent=parent
			self.enabled=False

		def enable(self):
			self.enabled=True
			if self.parent is not None:
				self.parent.enable()

	class Line:
		def __init__(self, flow, lvl, msg, prefix, boundary=False):
			if SELFDEBUG:
				groupname="None"
				if flow.group is not None: groupname=flow.group.name
				print(f"new line lvl={lvl} prefix='{prefix}' msg='{msg}' group={groupname}")
			self.flow=flow
			self.date=datetime.datetime.now()
			self.lvl=lvl
			self.msg=msg
			self.prefix=prefix
			self.group=flow.group
			self.boundary=boundary

			if self.group is not None:
				if not self.group.enabled:
					global level
					if lvl>=level:
						self.group.enable()

		def print(self):

			if self.group is not None:
				if not self.group.enabled: return ""
				if not self.boundary:
					if self.group.expand is not None:
						if self.lvl<self.group.expand: return ""
					else:
						global level
						if self.lvl<level: return ""

			#date=datetime.datetime.now()
			timestr=self.date.strftime('%Y-%m-%d %H:%M:%S.%f')[0:23]
			ctxstr=self.flow.ctx+" " if self.flow.ctx else ""
			#line=f"{timestr} {hostname} [{pidstr}{self.tidstr}] {levelstr[self.lvl]} {ctxstr}- {self.pointer.prefix}{self.msg}\n"
			line=f"{timestr} {hostname} [{pidstr}{self.flow.tidstr}] {levelstr[self.lvl]} {ctxstr}- {self.prefix}{self.msg}\n"
			return line

	def __init__(self):
		self.deep=0
		self.buf=[]
		self.group=None
		self.ctx=None

		# thread id index según aparición
		t=threading.get_ident()
		if t not in tlist: tlist[t]=len(tlist)
		if tlist[t]>0: self.tidstr="/"+str(tlist[t]).zfill(3)
		else: self.tidstr=""

	def flush(self):
		global output

		# Procesamos file por si se han incluido tags de fecha
		fileparsed=output
		date=datetime.datetime.now()
		if '%y' in fileparsed: fileparsed=fileparsed.replace('%y', date.strftime('%y'))
		if '%Y' in fileparsed: fileparsed=fileparsed.replace('%Y', date.strftime('%Y'))
		if '%m' in fileparsed: fileparsed=fileparsed.replace('%m', date.strftime('%m'))
		if '%d' in fileparsed: fileparsed=fileparsed.replace('%d', date.strftime('%d'))
		if '%H' in fileparsed: fileparsed=fileparsed.replace('%H', date.strftime('%H'))

		f=open(fileparsed, "a", encoding="utf8")
		for line in self.buf: f.write(line.print())
		f.close()
		self.buf.clear()
		self.ctx=None

	def add(self, lvl, msg):

		if SELFDEBUG:
			print(f"flow add: lvl={lvl}")

		prefix="│ "*self.deep

		line=self.Line(flow=self, lvl=lvl, prefix=prefix, msg=msg)
		self.buf.append(line)
		if self.deep==0:
			self.flush()

	def inside(self, name, lvl=NONE, expand=None):

		if SELFDEBUG:
			selfgroupname="None"
			if self.group is not None:
				selfgroupname=self.group.name
			print(f"inside: name={name} selfgroupname={selfgroupname}")

		# guardamos info grupo para el outside
		newgroup=self.Group(lvl=lvl, name=name, expand=expand, parent=self.group)
		self.group=newgroup

		if SELFDEBUG:
			selfgroupname=self.group.name
			selfgroupparent="None"
			if self.group.parent is not None:
				selfgroupparent=self.group.parent.name
			print(f"inside: selfgroupname={selfgroupname} selfgroupparent={selfgroupparent}")

		prefix="│ "*self.deep+"╭╸ "; self.deep+=1

		line=self.Line(flow=self, lvl=self.group.lvl, prefix=prefix, msg=self.group.name, boundary=True)
		self.buf.append(line)

	def outside(self, fail=False):
		self.deep-=1
		if fail:
			prefix="│ "*self.deep+"╰× "
		else:
			prefix="│ "*self.deep+"╰╸ "

		line=self.Line(flow=self, lvl=self.group.lvl, prefix=prefix, msg=self.group.name, boundary=True)
		self.buf.append(line)
		self.group=self.group.parent

		if self.deep==0: self.flush()

	def setctx(self, ctx):
		self.ctx=ctx

	def addctx(self, ctx):
		if self.ctx is not None: self.ctx+=" "
		else: self.ctx=""
		self.ctx+=ctx

class LogFlowOld:
	LDEBUG=False
	CTX=None

	def __init__(self, group=None, grouplvl=NONE, parent=None, expand=expandlevel):
		if self.LDEBUG: print(f"{id(self)} init parent={id(parent)}")

		self.buffer=list()
		self.expand=expand

		if group is None:
			# flow de primer nivel
			self.pointer=self
			self.group=None
			self.parent=None
			self.prefix=""

			# thread id index según aparición
			t=threading.get_ident()
			if t not in tlist: tlist[t]=len(tlist)
			if tlist[t]>0: self.tidstr="/"+str(tlist[t]).zfill(3)
			else: self.tidstr=""
		else:
			# subflow/grupo debajo de otro
			self.group=group
			self.grouplvl=grouplvl
			self.parent=parent
			self.prefix=parent.prefix+chars.vline
			self.tidstr=parent.tidstr
			self.printed=False # indica si se va a imprimir o no este grupo (depende del nivel de los adds)

	def setctx(self, ctx):
		self.CTX=ctx

	def add(self, lvl, msg):
		"""
		Agrega una línea al grupo actual
		"""
		if self.LDEBUG: print(f"{id(self)} pointer={id(self.pointer)} add: {msg}", end="")

		if self.expand:
			#if lvl<self.expand and lvl<level and lvl!=NONE: return
			if lvl<self.expand and lvl<level: return
		else:
			#if lvl<level and lvl!=NONE: return
			if lvl<level: return

		if lvl>=level: self.pointer.printed=True

		# generamos line
		date=datetime.datetime.now()
		timestr=date.strftime('%Y-%m-%d %H:%M:%S.%f')[0:23]
		ctxstr=self.CTX+" " if self.CTX else ""
		line=f"{timestr} {hostname} [{pidstr}{self.tidstr}] {levelstr[lvl]} {ctxstr}- {self.pointer.prefix}{msg}\n"

		self.pointer.buffer.append(line)
		#if self.pointer.loglevel<lvl: self.pointer.loglevel=lvl

		# si somos el flow raiz, grabamos
		if self.pointer is self: self.write(date)

	def inside(self, group, lvl=NONE, expand=None):
		"""
		Crea un grupo nuevo por debajo del actual
		"""
		if self.LDEBUG: print(f"{id(self)} pointer={id(self.pointer)} inside")

		# entramos
		newentry=LogFlow(group=group, grouplvl=lvl, parent=self.pointer, expand=expand)
		self.pointer=newentry

		# print?
		if lvl>=level: self.pointer.printed=True

		# generamos linea
		#date=datetime.datetime.now()
		#timestr=date.strftime('%Y-%m-%d %H:%M:%S.%f')[0:23]
		#line=f"{timestr} {hostname} [{pidstr}{self.tidstr}] {levelstr[lvl]} - {self.pointer.parent.prefix}{chars.groupstart}{self.pointer.group}\n"
		#self.pointer.buffer.append(line)
		# new
		self.pointer.insidedate=datetime.datetime.now()

	def outside(self, fail=False):
		if self.LDEBUG: print(f"{id(self)} pointer={id(self.pointer)} outside pointer.parent={id(self.pointer.parent)}")

		# generamos linea
		#self.pointer.outsideerror=error
		#if error: exitchar=chars.groupbreak
		#else: exitchar=chars.groupend
		#date=datetime.datetime.now()
		#timestr=date.strftime('%Y-%m-%d %H:%M:%S.%f')[0:23]
		#line=f"{timestr} {hostname} [{pidstr}{self.tidstr}] {levelstr[0]} - {self.pointer.parent.prefix}{exitchar}{self.pointer.group}\n"
		#self.pointer.buffer.append(line)
		# new
		date=datetime.datetime.now()
		self.pointer.outsidefail=fail
		self.pointer.outsidedate=date

		# salimos
		oldentry=self.pointer
		self.pointer=self.pointer.parent
		if oldentry.printed:
			self.pointer.buffer.append(oldentry)
			self.pointer.printed=True

		# si somos el flow raiz, grabamos
		if self.pointer is self: self.write(date)

	def write(self, date):
		global tloc,output

		# Procesamos file por si se han incluido tags de fecha
		fileparsed=output
		if '%y' in fileparsed: fileparsed=fileparsed.replace('%y', date.strftime('%y'))
		if '%Y' in fileparsed: fileparsed=fileparsed.replace('%Y', date.strftime('%Y'))
		if '%m' in fileparsed: fileparsed=fileparsed.replace('%m', date.strftime('%m'))
		if '%d' in fileparsed: fileparsed=fileparsed.replace('%d', date.strftime('%d'))
		if '%H' in fileparsed: fileparsed=fileparsed.replace('%H', date.strftime('%H'))

		f=open(fileparsed, "a", encoding="utf8")
		f.write(self.get())
		f.close()

	# Método recursivo que se ejecutará en cada subgrupo
	def get(self):
		if self.LDEBUG: print(f"{id(self)} get")

		innerlines=""
		for line in self.buffer:
			if type(line) is LogFlow:
				innerlines+=line.get()
			else:
				innerlines+=line

		if self.group is not None:
			# grouptime
			gtimedate=self.outsidedate-self.insidedate
			gtime=f" [{gtimedate.total_seconds():0.3f}]"

			# linea inside
			timestr=self.insidedate.strftime('%Y-%m-%d %H:%M:%S.%f')[0:23]
			insideline=f"{timestr} {hostname} [{pidstr}{self.tidstr}] {levelstr[self.grouplvl]} - {self.parent.prefix}{chars.groupstart}{self.group}\n"

			# linea outside
			if self.outsidefail: exitchar=chars.groupbreak
			else: exitchar=chars.groupend
			timestr=self.outsidedate.strftime('%Y-%m-%d %H:%M:%S.%f')[0:23]
			outsideline=f"{timestr} {hostname} [{pidstr}{self.tidstr}] {levelstr[self.grouplvl]} - {self.parent.prefix}{exitchar}{self.group}{gtime}\n"

			data=insideline+innerlines+outsideline
		else:
			data=innerlines

		self.buffer.clear()
		return data


# Método para encapsular un método y capturar sus salidas y entradas
#def wrap(fn, level=loglevel.NONE):
#	# https://www.geeksforgeeks.org/python-functools-wraps-function/
#	@wraps(fn)
#	def wrapper(*args, **kws):
#
#		global tloc
#		if getattr(tloc, 'deep', None) is None: tloc.deep = 0
#
#		if fn.__module__ != "__main__":
#			methodname=f"{fn.__module__}.{fn.__qualname__}()"
#		else:
#			methodname=f"{fn.__qualname__}()"
#
#		inside(methodname, level=level)
#		try:
#			ret=fn(*args, **kws)
#		except Exception as ex:
#			error(f"Exception {type(ex).__name__}: {str(ex)}")
#			outbreak()
#			raise
#		outside()
#
#		return ret
#	return wrapper

# https://www.geeksforgeeks.org/python-functools-wraps-function/
# https://stackoverflow.com/questions/10176226/how-do-i-pass-extra-arguments-to-a-python-decorator
def wrap(fn=None, level=NONE, expand=None):
	if not fn: return functools.partial(wrap, level=level, expand=expand)

	@functools.wraps(fn)
	def f(*args, **kws):

		global tloc
		if getattr(tloc, 'deep', None) is None: tloc.deep = 0

		if fn.__module__ != "__main__":
			methodname=f"{fn.__module__}.{fn.__qualname__}()"
		else:
			methodname=f"{fn.__qualname__}()"

		inside(methodname, level=level, expand=expand)
		try:
			ret=fn(*args, **kws)
		except Exception as ex:
			error(f"Exception {type(ex).__name__}: {str(ex)}")
			outbreak()
			raise
		outside()

		return ret
	return f

# Métodos públicos
def setoutput(filepath, filename=None):
	global output
	if filename is not None:
		output=filepath+os.sep+filename
	else:
		output=filepath

def setlevel(newlvl):
	global level
	if type(newlvl) == int:
		level=newlvl
	if type(newlvl) == str:
		newlvl=newlvl.upper()
		if newlvl=="NONE": level=NONE
		if newlvl=="TRACE": level=TRACE
		if newlvl=="DEBUG": level=DEBUG
		if newlvl=="INFO": level=INFO
		if newlvl=="WARN": level=WARN
		if newlvl=="ERROR": level=ERROR
		if newlvl=="FATAL": level=FATAL
		if newlvl=="ALL": level=ALL

def setcontext(ctx):
	if getattr(tloc, 'flow', None) is None: tloc.flow=LogFlow()
	tloc.flow.setctx(ctx)

def addcontext(ctx):
	if getattr(tloc, 'flow', None) is None: tloc.flow=LogFlow()
	tloc.flow.addctx(ctx)

def fatal(msg):
	__log(FATAL,msg)

def error(msg):
	__log(ERROR,msg)

def warn(msg):
	__log(WARN,msg)

def info(msg):
	__log(INFO,msg)

def debug(msg):
	__log(DEBUG,msg)

def trace(msg):
	__log(TRACE,msg)

def write(msg):
	__log(ALL,msg)

def __log(lvl,msg):
	global tloc
	if not output: return # Si no hay fichero definido, salimos
	if getattr(tloc, 'flow', None) is None: tloc.flow=LogFlow()
	tloc.flow.add(lvl, msg)

def inside(name, level=NONE, expand=None):
	global tloc
	if not output: return
	if getattr(tloc, 'flow', None) is None: tloc.flow=LogFlow()
	tloc.flow.inside(name, lvl=level, expand=expand)

def outside(fail=None):
	global tloc
	if not output: return
	if getattr(tloc, 'flow', None) is None: tloc.flow=LogFlow()
	tloc.flow.outside(fail=fail)

def outbreak():
	global tloc
	if not output: return
	if getattr(tloc, 'flow', None) is None: tloc.flow=LogFlow()
	tloc.flow.outside(fail=True)
