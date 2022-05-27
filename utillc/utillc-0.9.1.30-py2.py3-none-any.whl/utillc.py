#!/usr/bin/python
from __future__ import print_function

#from utillc.__init__ import *


__version__ = "0.9.1.30"
utillc_version = __version__
__all__ = ( 'EKOX', 'STACK', 'EKO', 'TYPE', 'EKOI', 'EKOT', 'EKOH', 'EKOF', 'test', 'Bool', 'ntimes', 'LINE', 'resizeImage')

#import pymf
from datetime import datetime
import platform
python3Running = platform.python_version() == 3
#print (platform.python_version()[0])
import matplotlib
import os
import logging
import threading
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import sys, os, getopt, os.path
#from time import *
import time as _time
from time import gmtime, strftime
from datetime import timedelta
#from numpy import *
import numpy as np, scipy, scipy.misc
import scipy.ndimage
import re
try :
    import tempfile, cv2
    import atexit
except :
    pass

class NoException(Exception):
    """Exception never raised
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

import inspect


class MyLogger(logging.Logger):

    def __init__(self, name, level = logging.NOTSET):
        return super(MyLogger, self).__init__(name, level)        

def info(self, x) : 
    return EKOT(x, llevel=1)

logging.setLoggerClass(MyLogger)



#print( strftime("Starting up %I:%M:%S %p", _time.localtime()))

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

start = _time.time()
INFO = 100
WARNING = 1000
ERROR = 2000
LOG = 3000

try :
    oeeko = os.environ["MINEKOLEVEL"]
    defe = int(oeeko)
except :
    defe = ERROR

#print("defe ", defe)

_readEL = True
_el = 1000

try :
    _noReadEnv = os.environ["EKONOREADENV"] != ""
except KeyError:
    _noReadEnv = False

if _noReadEnv:
    _readEL = False
else :
    _readEL = True
    import argparse

_readEL = True


donothing = lambda : 1
donothing1 = lambda x : 1

def el():
    global _el, _readEL
    #print("read el ", _readEL)
    if _readEL:
        __parser = argparse.ArgumentParser()
        InitArgs(__parser)
        SetOptions(__parser)
        ainit_ = EKO_init_end(cause='start', r=0)

        try:
            pass
            atexit.register(EKO_init_end, cause='end', r=2)
        except :
            pass
    #print(" el() _el ", _el)
    return _el

Bool = lambda x : { '': True, 'yes' : True, 'no' : False, 'True' : True, 'False' : False , False : False, True : True}[x]

def InitArgs(parser):
    global _el, _readEL, options_
    try:
        parser.add_argument('--minekolevel', dest='el', default=defe, type=int, help='log level')
        parser.add_argument('--verbose', default=False, type=bool, help='enable verbose mode')
        options_, rem = parser.parse_known_args()
    except Exception as e:
        print("exception : " , str(e))
        pass

def SetOptions(parser):
    global _el, _readEL, options_
    try :
        _el = int(os.environ["MINEKOLEVEL"])
    except :
        _el = -1
    try :
        try:
            _el = options_.el
            #print ("_el ", _el)
        except AttributeError:
            pass
        if options_.verbose:
            _el = -1
        #_readEL = False
    except :
        pass
    #print("xxx _el ", _el)

ekodict = {}
ekodict2 = {}
ekostream = sys.stderr
ekostream = sys.stdout

doeko = True

class ET :
    etab = ""
    def __init__(self) :
        ET.etab = "" + ET.etab
    def __enter__(self):
        return self
    def __exit__(self, _, __, ___):
        ET.etab = ET.etab[1:]


def print1(x, color=False, noeko=False) :

    #print((doeko, noeko))

    if doeko  and not noeko :
        if color : ekostream.write(bcolors.WARNING)
        ekostream.write(ET.etab + x + "\n")
        if color : ekostream.write(bcolors.ENDC)
        ekostream.flush()
    return x


threadIDS = {}


def tt(_loc):
    global start, ekodict
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)
    ll = _loc + '_' + str(len(ff))
    x = _time.time()
    elapsed = (x - start)
    start = x
    now = int(elapsed *1000)

    #print1('dict=' + str(ekodict))
    #print1('x=' + str(x))
    #print1('ll=' + str(ll))

    if ll in ekodict :
        then = ekodict[ll]
        ppp = '/' + str(int((x - then)*1000)).zfill(4)
    else:
        ppp = ''
    ekodict[ll] = x

    thid = threading.get_ident()
    if thid not in threadIDS :
        threadIDS[thid] = len(threadIDS)
    # display thread id if number of active thread > 2
    dthid = '(' + str(threadIDS[thid]).zfill(2) + ')' if len(threadIDS) > 2 else ""
    return '[' + str(now).zfill(4) + ppp + 'ms]' + dthid + ' '

def TIME(f, n=10) :
    """
    calls f with current time (sec), filename, line in source file
    """
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    xx = _time.time()
    for i in range(n):
        r = f((xx, ff[1], ff[2]))
    yy = _time.time()
    return ((yy-xx)/n, r)

def LINE() :
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    return str(ff[1]) +  ':' + str(ff[2])

def stringify(x) :
    pattern = 'stringify\((\w)\)'
    regex = re.compile(pattern)
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    match = regex.search(ff[4][0])
    g = match.groups()[0]
    rr = ff[4][0].replace(' ','').replace('SS','').replace('(','').replace(')','').replace('\n','')
    return g


def ntimes(closure = lambda x : sys.exit(0), max=-1) :
    global ekodict2
    if max >= 0 :
        closure = lambda x : 0
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)
    ll = str(len(ff))
    if ll in ekodict2 :
        ekodict2[ll] = ekodict2[ll] + 1
        closure(ekodict2[ll])
        if ekodict2[ll] >= max :
            sys.exit(0)
    else:
        ekodict2[ll] = 0
    

def dictify(x) :
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)
    pattern = 'dictify\( *\((\w)(, *\w)* *\) *\)'
    pattern = 'dictify\(\((\w)(, \w)\)\)'
    regex = re.compile(pattern)
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    EKOX(ff)
    EKOX(ff[4][0])
    match = regex.search(ff[4][0])
    return dict(zip([_x.replace(' ','').replace(',', '') for _x in match.groups()], list(x)))


every_dict = {}

def everySeconds(closure, intervalInSeconds, tag="a") :
    if tag not in every_dict :
        every_dict[tag]  = datetime.now()
    else :
        now = datetime.now()
        duration = now - every_dict[tag]
        duration_in_s = duration.total_seconds() 
        if duration_in_s > intervalInSeconds :
            closure()
            every_dict[tag]  = datetime.now()


def FE(x) :
    return EKOX(x, INFO, withprint=False, llevel=1, pattern="print")

def ROWCOLNUMBER(x) :
    h = x.shape[0]
    w = x.shape[1]
    xx = np.hstack((np.asarray([range(h)]).T, x))
    xx = np.vstack((np.asarray([range(w+1)]) + -1, xx))
    return xx


def STACK(llevel=0) :
    """
    print the call stack from this point
    """
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1:]
    pp = '\n'.join([ str(e[1]) + ":" + str(e[2]) + ": fct=" + str(e[3]) + ", line=" + str(e[4][0].strip()) for e in ff])
    print1("Stack_________________________:\n" + pp + "\n___________________________\n")

def info(x) : return EKOX(x, llevel=1)

def EKOX(x,n=INFO,pref="", color=False, check=False, withprint=True, llevel=0, pattern="EKOX"):
    """
    output x variable name followed by its value (in an emacs error format)
    """
    r = ""
    frame = inspect.currentframe()
    ofrl =  len(inspect.getouterframes(frame))
    #ff = inspect.getouterframes(frame)[(1 + llevel) % ofrl]
    ff = inspect.getouterframes(frame)[(1 + llevel) % ofrl]
    
    inl = ""
    try :
        inl = "\n" if isinstance(x, np.ndarray) else ""
    except :
        pass
    #print ("n=", n, ', el()=', el())
    prt = (check and not x) or n >= el()

    ppat = pattern + "("
    #print("coucou")
    #print((prt, n, el()))

    if prt :
        loc = str(ff[1]) +  ':' + str(ff[2])
        strng = str(x)
        doublecommainid = ('((' in str(ff[4][0])) and ('))' in str(ff[4][0]))
        if isinstance(x, tuple) and doublecommainid:
            tk1 = str(ff[4][0]).replace(ppat, '').replace(')\n', '').strip('\n ').split(',')
            if len(tk1) == len(list(x)) :
                tk = str(ff[4][0]).replace(ppat, '').replace(')\n', '').strip('\n ')[1:-1].split(',')
                tkk = ', '.join([sx + ' = ' + str(sv) for sx, sv in zip(tk, list(x))])
            else :
                tkk = str(ff[4][0]).replace(ppat, '').replace(')\n', '').strip('\n ') + '=' + inl + pref + strng
        else :
            tkk=inl + pref + strng
            try :
                tkk = str(ff[4][0]).replace(ppat, '').replace(')\n', '').strip('\n ') + '=' + inl + pref + strng
            except :
                pass
        if '\n' in strng :
            strng = '\n' + strng
        preamb = loc + ": " if withprint else ""
        if (ff[4] != None) :
            r = print1(preamb + tt(loc) + tkk + '.', color=color, noeko=not withprint)
        else:
            r = print1(preamb + tt(loc) + str(ff[3]) + '=' + inl + pref + strng + '.', color=color, noeko= not withprint)

    if check and not x :
        assert(c)
    return r


def EKOX_old(x,n=INFO,pref=""):
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    inl = ""
    try :
        inl = "\n" if isinstance(x, ndarray) else ""
    except :
        pass
    #print "el=", n, ', ', el()
    if (n >= el()):

        loc = str(ff[1]) +  ':' + str(ff[2])
        strng = str(x)
        if '\n' in strng :
            strng = '\n' + strng
        if (ff[4] != None) :
            r = print1(loc +  ': ' + tt(loc) + str(ff[4][0]).replace('EKOX(', '').replace(')\n', '').strip('\n ') + '=' + inl + pref + strng + '.')
        else:
            r = print1(loc +  ': ' + tt(loc) + str(ff[3]) + '=' + inl + pref + strng + '.')
    return r

numImages = 0
tempDir = "/kaggle/working/images"
tempDir = "/tmp/images"

#print(tempDir)
def EKOP(x,n=INFO, dir=tempDir, sz=500, label="", width=1000, height = 500, labels=None):
    """
    create an bar plot image from an array
    """
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    fn = tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=dir, prefix=label)
    #EKOX(fn)
    #EKOX(TYPE(x))
    if (n < el()): return ""
    if not isinstance(x, np.ndarray) :
        x = np.asarray(x)
    dpi = 100
    fig = plt.figure(figsize=(float(width)/dpi, float(height)/dpi), dpi=dpi)
    if len(x.shape) == 1 :
        plt.plot(x)
    else :
        if labels is None : labels= [""] * x.shape[0]
        t = range(x.shape[0])
        for i in range(x.shape[1]) : plt.plot(t, x[:,i], label=labels[i])
        plt.legend()
    fig.savefig(fn)
    plt.close()
    loc = (ff[1]) +  ':' + str(ff[2])
    inl = "\n" if isinstance(x, np.ndarray) else ""
    if (n >= el()):
        if (ff[4] != None) :
            r = print1(loc +  ': ' + tt(loc) + str(ff[4][0]).replace('EKOP(', '').replace(')\n', '').strip('\n ') + '=' + inl + '[[file:' + str(fn.name) + ']].')
        else:
            r = print1(loc +  ': ' + tt(loc) + str(ff[3]) + '=' + inl +  '[[file:' + str(fn.name) + ']].')
    return r

    
def EKOF(fx,n=INFO, dir=tempDir, sz=500, label="", suffix=".png", width=1000, height = 500, llevel=0):    
    """
    matplotlib genraic interface
    """
    r = ""
    frame = inspect.currentframe()
    #ff = inspect.getouterframes(frame)[1]
    ofrl =  len(inspect.getouterframes(frame))
    ff = inspect.getouterframes(frame)[(1 + llevel) % ofrl]    
    fn = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, dir=dir, prefix=label)
    if (n < el()): return ""
    dpi = 100
    fig = plt.figure(figsize=(float(width)/dpi, float(height)/dpi), dpi=dpi)
    fx(fig)
    fig.savefig(fn, dpi=dpi)
    plt.close(fig)
    loc = (ff[1]) +  ':' + str(ff[2])
    inl = "\n"
    if (n >= el()):
        if (ff[4] != None) :
            r = print1(loc +  ': ' + tt(loc) + str(ff[4][0]).replace('EKOP(', '').replace(')\n', '').strip('\n ') + '=' + inl + '[[file:' + str(fn.name) + ']].')
        else:
            r = print1(loc +  ': ' + tt(loc) + str(ff[3]) + '=' + inl +  '[[file:' + str(fn.name) + ']].')
    return r



def EKOH(x,n=INFO, dir=tempDir, sz=500., label="", width=1000, height = 500):
    """
    """
    def histo(fig) :
        matplotlib.pyplot.hist(x, bins=50)
    return EKOF(histo, n, dir, sz, label, ".png", width, height, llevel=1)



def EKOB(x,n=INFO, dir=tempDir, sz=500, label="", ):
    """
    create an bar plot image from an array
    """
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    fn = tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=dir, prefix=label)
    #EKOX(fn)
    EKOX(TYPE(x))
    if (n < el()): return ""
    if not isinstance(x, np.ndarray) :
        x = np.asarray(x)
    n = x.shape[0]
    max = x.max()
    x = x / max * sz
    thick = 2
    pas = thick*2
    img = np.ones((n*pas, sz, 3))
    red = (0, 0, 255)
    [ cv2.line(img, (i*pas, sz), (i*pas, sz - int(e*sz)), red, 2) for i,e in enumerate(x) ]
    cv2.imwrite(fn.name, img)

    loc = (ff[1]) +  ':' + str(ff[2])
    inl = "\n" if isinstance(x, np.ndarray) else ""
    if (n >= el()):
        if (ff[4] != None) :
            r = print1(loc +  ': ' + tt(loc) + str(ff[4][0]).replace('EKOB(', '').replace(')\n', '').strip('\n ') + '=' + inl + '[[file:' + str(fn.name) + ']].')
        else:
            r = print1(loc +  ': ' + tt(loc) + str(ff[3]) + '=' + inl +  '[[file:' + str(fn.name) + ']].')
    return r


def EKOI(x,n=INFO, small=True,dir=tempDir, sz=150, label=""):
    """
    output x variable name, create an image based on x value and output a string which cause emacs to display the image
    """
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    os.makedirs(dir, exist_ok = True) 
    fn = tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=dir, prefix=label)
    #EKOX(fn)

    if (n < el()): return ""
    if x is None : return ""
    if not isinstance(x, np.ndarray) :
        x = np.asarray(x)
    if len(x.shape) == 2 :
        x = np.stack([x]*3, axis=2) 
        
    if x.dtype in [ np.float, np.float128, np.float16, np.float32, np.float64, np.floating] :

        mean, std, imin_, imax_  = np.mean(x.astype(float)), np.std(x.astype(float)), np.argmin(x), np.argmax(x)
        if mean > 1. or x[imax_] > 1. :
            x = x.astype(int)
        else :
            x = (x * 255).astype(int)

    if small :
        fx = sz / x.shape[0]
        fy = fx
        #print(fx)
        x = scipy.ndimage.zoom(x, (fx, fx, 1))


    #EKOX(TYPE(x))
    cv2.imwrite(fn.name, x[:,:,::-1])
    loc = (ff[1]) +  ':' + str(ff[2])
    inl = "\n" if isinstance(x, np.ndarray) else ""
    if (n >= el()):
        if (ff[4] != None) :
            r = print1(loc +  ': ' + tt(loc) + str(ff[4][0]).replace('EKOX(', '').replace(')\n', '').strip('\n ') + '=' + inl + '[[file:' + str(fn.name) + ']].')
        else:
            r = print1(loc +  ': ' + tt(loc) + str(ff[3]) + '=' + inl +  '[[file:' + str(fn.name) + ']].')
    return r

def EKOZ(x):
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    inl = "\n" if isinstance(x, ndarray) else ""
    if (ff[4] != None) :
        return str(ff[4][0]).replace('EKOX(', '').replace(')\n', '').strip('\n ')
    else:
        return str(ff[3])

def testeko(x):
    EKOX(x)

a='eko'
#testeko(a)

def SEKO(x) :
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    if (ff[4] != None) :
        loc = str(ff[1]) +  ':' + str(ff[2])
        r += loc +  ': ' + tt(loc) + '=' + str( x)
    return r

def EKOT(x,n=INFO,pref="", color=False, llevel=0 ):
    """
    output x value
    """

    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1 + llevel]
    if (ff[4] != None and n >= el()) :
        loc = str(ff[1]) +  ':' + str(ff[2])
        r += print1( loc +  ': ' + tt(loc) + '=' + pref + str( x) + '.', color=color)
    return r

def LINE():
    """
    yields the line file/numer whithout printing
    """
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    if (ff[4] != None) :
        loc = str(ff[1]) +  ':' + str(ff[2])
        r += loc +  ' line ' + tt(loc) + '.'
    return r

    


def EKO(n=INFO, llevel=0):
    """
    output file:line
    put llevel=1 for line number corresponding to call of the fct where EKO is
    """
    r = ""
    frame = inspect.currentframe() 
    ofrl =  len(inspect.getouterframes(frame))
    ff = inspect.getouterframes(frame)[(llevel+1)%ofrl]
    if (ff[4] != None and n >= el()) :
        loc = str(ff[1]) +  ':' + str(ff[2])
        r += print1 (loc +  ': ' + tt(loc) + '.')
        pass
    return r

class EK__ :
    def __init__(self) :
        EKO()

def TYPE(x,tab="", bins=10, range=None) :
    """
    returns a string describing the type of x
    """
    return '\n' + TYPE1(x, tab, 0, bins=bins, range=range)


def TYPE1(x,tab, depth, comp_mean=True, bins=10, range=None) :
    try :
        import torch
        if isinstance(x, torch.Tensor) :
            x = x.cpu().detach().numpy()
    except Exception as e:
        pass

    if isinstance(x, list) :
        w = ""
        if len(x) > 0:
            t = TYPE1(x[0], tab, depth+1, comp_mean=False)
            for i,e in enumerate(x):
                if TYPE1(e, tab, depth+1, comp_mean=False) != t:
                    w = "-not uniform-" + str(i) + '-'
                    break
        return 'list' + w + '#' + str(len(x)) + '(' + (TYPE1(x[0], tab+' ', depth+1) if len(x) > 0 else '') + ')'
    elif isinstance(x, tuple) :
        return 'tuple#' + str(len(x)) + '(' + ''.join(['\n' + tab + ' ' + str(i) + ' : ' + TYPE1(e, tab + ' ', depth+1) for i,e in enumerate(x)]) + '\n' + tab + ')'
    elif isinstance(x, np.ndarray) : #, np.generic) ) :
        imin_, imax_, mean, std, min_, max_ = 0,0,0,0,0,0
        hst=""
        if comp_mean :
            try :
                mean, std, imin_, imax_  = np.mean(x.astype(float)), np.std(x.astype(float)), np.argmin(x), np.argmax(x)
                imax_ = np.unravel_index(np.argmax(x, axis=None), x.shape)
                max_ = x[imax_]
                imin_ = np.unravel_index(np.argmin(x, axis=None), x.shape)
                min_ = x[imin_]
                hst = np.histogram(x.flatten(), bins=bins, range=range)
                lhstv = [str(e)  for e in hst[0]]
                lhstb = [str(e) for e in hst[1]]
                smx = np.max( [ len(s) for s in lhstv + lhstb])
                lhstv = [e.rjust(smx + 1, ' ')  for e in lhstv]
                lhstb = [e.rjust(smx + 1, ' ') for e in lhstb]

                hstv = ' '.join(lhstv)
                hstb = ' '.join(lhstb)
                hst = "\nhist=" + hstv
                hst +="\nbins=" + hstb
            except Exception as e:
                EKOX(e)
                pass
        return str(type(x).__name__) + '#' + str(x.shape) + '(' + str(x.dtype) + ', m=' + str(mean) + ' s=' + str(std) + ',min=' + str(min_) + '[' + str(imin_) + '],max=' + str(max_) + '[' + str(imax_) + ']' + hst + ')'
    elif isinstance(x, dict) :
        return 'dict#' + str(len(x)) + '(' + ((TYPE1(list(x.keys())[0], tab + ' ', depth+1) + ':' + TYPE1(list(x.values())[0], tab+' ', depth+1)) if len(x) > 0 else '') + ')'
    else :

        try :
            import torch
            if isinstance(x, torch.Tensor) :
                return  str(type(x).__name__) + '#' + str(x.size()) + '(' + str(x.type()) + ', m=' + str(x.float().mean()) + ' s=' + str(x.float().var()) + ')'
        except Exception as e:
            logging.info(e)
            pass

        return type(x).__name__



def EKO_init_end(cause, r) :
    return 1
    if r <= 0:
        #EKOX(cause)
        print('www')
        return 1
    else :
        print('xxxx\n')
        EKO_init_end(cause, r-1)
        print('yyy')
        os._exit(0)
    return 1

def array2txt_(a) :
    def f1(l1,s) :
        return s[0].join([f1(x, s[1:]) for x in l1]) if isinstance(l1, list) else str(l1).zfill(2)
    l = a.tolist()
    r = f1(l, '\n  ')
    return '\n' + r

def array2txt(a) :
    return array2txt_(a.astype(int))

last = -1
totdur = 0
lastloc = ""
progressn = 0
def PROGRESS(cur, total, v = "", WW=50, force=False) :
    global last, lastloc, totdur, progressn
    progressn += 1
    v = str(v)

    if force or sys.stdout.isatty():
        frame = inspect.currentframe()
        ff = inspect.getouterframes(frame)[1]
        loc = ""
        if (ff[4] != None) :
            loc = str(ff[1]) +  ':' + str(ff[2])

        now = _time.time()
        if cur == 0 or lastloc != loc:
            totdur = 0
            last=-1
        if last > 0 and lastloc == loc and loc != "":
            elapsed = (now - last)
            totdur += elapsed
            eta = float(total - cur) * totdur / cur
            p = float(cur) / total
            print( '\r', end='')

            sss = ['='] * int(p * WW) + ['-'] * int((1.-p)* WW)
            sss[progressn % len(sss)] = '.'
            print( ''.join(sss), end='')
            etaf = str(timedelta(seconds=int(eta)))
            if cur >= total :
                print( os.path.basename(loc) + ' TOT:' + str(timedelta(seconds=int(totdur))) + ', ' + v)
            else:
                print( os.path.basename(loc) + ' ETA:' + etaf + ', ' + str(cur) + '/' + str(total) + ' ' + v, end='')
            sys.stdout.flush()
        lastloc =  loc
        last = now

def ENV(var, defval=None) :
    isin = var in os.environ
    val =  os.environ[var] if isin else defval
    return val


#EKOX(sys.path)

noimage=0

# n emacs, use org-mode as your buffer's major mode.
# You then have access to all the power of org-mode formatting,
# which includes linking to image files and displaying them:
# then you can call org-toggle-inline-images (C-c C-x C-v) to display images in the buffer (without a prefix argument,
# it will display only images without description; if you give a prefix argument, it will display all images)


# to be used with iimage-mode in emacs
def IMG(x, desc="an image", n=INFO,pref="") :
    global noimage
    array=x
    im = os.path.join(tempDir, str(noimage).zfill(3) + ".png")
    scipy.misc.imsave(im, array)
    ss = "[[file:" + im + "][" + desc + "]]"
    ekostream.write(ss + "\n")
    ekostream.flush()
    r = ""
    frame = inspect.currentframe()
    ff = inspect.getouterframes(frame)[1]
    inl = ""
    try :
        inl = "\n" if isinstance(x, ndarray) else ""
    except :
        pass
    #print "el=", n, ', ', el()
    if (n >= el()):

        loc = str(ff[1]) +  ':' + str(ff[2])

        if (ff[4] != None) :
            r = print1(loc +  ': ' + tt(loc) + str(ff[4][0]).replace('IMG(', '').replace(')\n', '').strip('\n ')  + '.')
        else:
            r = print1(loc +  ': ' + tt(loc) + str(ff[3]) + '.')
    noimage += 1
    return r

"""
Bytes-to-human / human-to-bytes converter.
Based on: http://goo.gl/kTQMs
Working with Python 2.x and 3.x.
Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
License: MIT
"""
SYMBOLS = {
    'customary'     : ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
    'customary_ext' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                       'zetta', 'iotta'),
    'iec'           : ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
    'iec_ext'       : ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
                       'zebi', 'yobi'),
}

def bytes2human(n, format='%(value).1f %(symbol)s', symbols='customary'):
    """
    Convert n bytes into a human readable string based on format.
    """
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)


def checkGradient(optimizer=None, loss=None) :
    import torch
    if isinstance(optimizer, torch.nn.Module) :  
        named_parameters = optimizer.named_parameters()
        def itt() :
            for i, (n, p) in enumerate(named_parameters) :
                if(p.requires_grad) and ("bias" not in n) and p.grad is not None:
                    #p.grad.detach_()
                    yield p
    if isinstance(optimizer, torch.optim.Optimizer) :
        def itt() :
            for group in optimizer.param_groups : 
                for p in group['params'] : 
                    if p.requires_grad and p.grad is not None :
                        yield p
    if isinstance(optimizer, list) and isinstance(optimizer[0], torch.Tensor) :
        def itt() :
            for t in optimizer :
                #t.grad.detach_()
                #t.grad.zero_()
                yield t
    #for i, p in enumerate(itt()): p.grad.zero_()
    #loss.backward() # retain_graph=True)
    lgs, ave_grads, max_grads, grads = [], [], [], {}
    for i, p in enumerate(itt()):
        grads[i]= p.grad
        ave_grads.append((grads[i]).abs().mean().item())
        max_grads.append((grads[i]).abs().max().item())
        lgs.append(grads[i].flatten())
    #EKOX(len(ave_grads))
    tgrads = torch.cat(lgs)
    return tgrads.cpu().detach().numpy(), ave_grads, max_grads

def crappyhist(a, bins=20, width=80):
    h, b = np.histogram(a, bins)
    s = '\n'.join([ '{:5.3f}  | {:{width}s} {}'.format(
        b[i], 
        '#'*int(width*h[i]/np.amax(h)), 
        h[i], 
        width=width) for i in range (0, bins)])
    return ' \n' + s

def resizeImage(x, ht, wt, keepAspectRatio = True, pad=True) :
    assert(len(x.shape) == 3)
    if keepAspectRatio :
        h,w,_ = x.shape
        art = ht/wt
        ari = h/w
        if ari > art or  np.isclose(art, ari) :
            if pad :
                k = ht/h
                nww = int(w*k)
                ii = int((wt-nww)/2)                
                imr = cv2.resize(x, dsize = (nww, ht), interpolation=cv2.INTER_CUBIC)
                black = np.zeros((ht, wt, 3),dtype=np.uint8)                
                black[:, ii : ii + nww , :] = imr
                res = black
            else :
                k = wt/w
                nhh = int(h*k)
                imr = cv2.resize(x, dsize = (wt, nhh), interpolation=cv2.INTER_CUBIC)
                hhh, www, _ = imr.shape
                ii = int((nhh - ht)/2)
                res = imr[ii : ii+ht, :, :]
            hhh, www, _ = res.shape
            assert(hhh == ht and www == wt)
            return res
        else :
            y = resizeImage(np.transpose(x, (1, 0, 2)), wt, ht, pad=pad)
            res = np.transpose(y, (1, 0, 2))
            hhh, www, _ = res.shape
            assert(hhh == ht and www == wt)
            return res
    else :
        imr = cv2.resize(x, dsize = (wt, ht), interpolation=cv2.INTER_CUBIC)
        return imr


def test() :
    import scipy.misc
    face = scipy.misc.face()
    EKOI(face)
    EKOX(face.shape)
    hh, ww, _ = face.shape
    EKOI(resizeImage(face, ht=hh*2, wt=ww*3)) 
    EKOI(resizeImage(face, ht=hh*3, wt=ww*2)) 
    EKOI(resizeImage(face, ht=hh*2, wt=ww*3, pad=False)) 
    EKOI(resizeImage(face, ht=hh*3, wt=ww*2, pad=False)) 
    
    
    EKO()
    x,y=1, 'y'
    EKOX(x)


    EKOH(np.random.rand(100))

    im = np.fromfunction(lambda i, j: i*i/600/600 * 255 + j/600*255, (600, 600), dtype=float)
    EKOX(im.shape)
    EKOI(im)

    
    im = np.fromfunction(lambda i, j: np.asarray([(np.sin(i/np.pi/10) + np.cos(j/np.pi/10))/2.*255]*3), (600, 600), dtype=float).transpose(1,2,0)
    EKOX(TYPE(im))
    EKOI(im)
    EKO()
    EKOX(x,n=INFO)
    EKOX(x,n=WARNING)
    EKOX(x,n=ERROR)
    EKOT((1,2))
    EKOX((x,y))
    xy = (2,3)
    EKOX(xy)
    #print(FE(x))
    EKOX((x,y))
    print(FE((x,y)))
    EKOT("success", n=LOG, color=True)

if __name__ == "__main__":
    print(__version__)
