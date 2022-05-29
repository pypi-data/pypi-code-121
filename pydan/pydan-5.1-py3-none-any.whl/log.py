#!/usr/bin/env python3

import os
import datetime
import platform
import threading
from functools import wraps

# Niveles de log
class loglevel:
	NONE = 0
	TRACE = 1
	DEBUG = 2
	INFO = 3
	WARN = 4
	ERROR = 5
	FATAL = 6
	ALL = 7
levelstr = [ "NONE ", "TRACE", "DEBUG", "INFO ", "WARN ", "ERROR", "FATAL", "ALL  " ]

# Variables por defecto
level=loglevel.NONE
output=None

# Utilizamos threading local para establecer variables independientes
# a cada hilo, para soportar aplicaciones multi-hilo
tloc=threading.local()
# Sep es el nivel de profundidad en el que nos encontramos
# Cada entrada en un método lo incrementa y cada salida lo decrementa
tloc.deep=0
# tlist es una lista de hilos de la aplicación, debido a que son muy largos los simplificamos
tlist={}

# Método para encapsular un método y capturar sus salidas y entradas
def wrap(fn):
	# https://www.geeksforgeeks.org/python-functools-wraps-function/
	@wraps(fn)
	def wrapper(*args, **kws):

		global tloc
		if getattr(tloc, 'deep', None) is None: tloc.deep = 0

		if fn.__module__ != "__main__":
			methodname=f"{fn.__module__}.{fn.__qualname__}()"
		else:
			methodname=f"{fn.__qualname__}()"

		inside(methodname)
		try:
			ret=fn(*args, **kws)
		except Exception as ex:
			error(f"Exception {type(ex).__name__}: {str(ex)}")
			outbreak()
			raise
		outside()

		return ret
	return wrapper

# Métodos públicos
def fatal(msg):
	__write(loglevel.FATAL,msg)

def error(msg):
	__write(loglevel.ERROR,msg)

def warn(msg):
	__write(loglevel.WARN,msg)

def info(msg):
	__write(loglevel.INFO,msg)

def debug(msg):
	__write(loglevel.DEBUG,msg)

def trace(msg):
	__write(loglevel.TRACE,msg)

def write(msg):
	__write(loglevel.ALL,msg)

def inside(section):
	global tloc
	if getattr(tloc, 'deep', None) is None: tloc.deep = 0
	if getattr(tloc, 'section', None) is None: tloc.section = list()
	tloc.section.append(section)
	__write(loglevel.NONE,f"╭╸ {section}")
	tloc.deep+=1

def outside():
	global tloc
	if getattr(tloc, 'deep', None) is None: tloc.deep = 0
	if getattr(tloc, 'section', None) is None: tloc.section = list()
	section=tloc.section.pop()
	tloc.deep-=1
	__write(loglevel.NONE,f"╰╸ {section}")

def outbreak():
	global tloc
	if getattr(tloc, 'deep', None) is None: tloc.deep = 0
	if getattr(tloc, 'section', None) is None: tloc.section = list()
	section=tloc.section.pop()
	tloc.deep-=1
	__write(loglevel.NONE,f"╰× {section}")

def __write(lvl,msg):
	global tloc,tlist,level,output

	# Si el nivel de log definido es inferior, salimos
	if lvl>0 and lvl<level: return

	# Si no hay fichero definido, salimos
	if not output: return

	# fecha de logueo
	time=datetime.datetime.now()
	timestr=time.strftime('%Y-%m-%d %H:%M:%S.%f')[0:23]

	# Procesamos file por si se han incluido tags de fecha
	fileparsed=output
	if '%y' in fileparsed: fileparsed=fileparsed.replace('%y', time.strftime('%y'))
	if '%Y' in fileparsed: fileparsed=fileparsed.replace('%Y', time.strftime('%Y'))
	if '%m' in fileparsed: fileparsed=fileparsed.replace('%m', time.strftime('%m'))
	if '%d' in fileparsed: fileparsed=fileparsed.replace('%d', time.strftime('%d'))
	if '%H' in fileparsed: fileparsed=fileparsed.replace('%H', time.strftime('%H'))

	# host y pid
	host=platform.node()
	pid=str(os.getpid())

	# threadid posix
	#tidstr="/"+str(threading.get_ident())

	# threadid linux
	#import ctypes
	#libc = ctypes.cdll.LoadLibrary('libc.so.6')
	## System dependent, see e.g. /usr/include/x86_64-linux-gnu/asm/unistd_64.h
	#SYS_gettid = 186
	#tidstr="/"+str(libc.syscall(SYS_gettid))

	# thread id index según aparición
	t=threading.get_ident()
	if t not in tlist: tlist[t]=len(tlist)
	if tlist[t]>0: tidstr="/"+str(tlist[t]).zfill(3)
	else: tidstr=""

	# separador de profundidad
	if getattr(tloc, 'deep', None) is None: tloc.deep = 0
	sepstr="│ "*tloc.deep

	# Juntamos los datos en una línea
	line=f"{timestr} {host} [{pid}{tidstr}] {levelstr[lvl]} - {sepstr}{msg}\n"

	# Escribimos en el log
	f=open(fileparsed, "a", encoding="utf8")
	f.write(line)
	f.close()
